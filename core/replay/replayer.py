import logging
import multiprocessing
import os
import signal
import time
from multiprocessing.managers import SyncManager
from queue import Full, Empty

from worker import ReplayWorker

from stats import init_stats, collect_stats, display_stats, print_stats

logger = logging.getLogger("SimpleReplayLogger")


# Needs to be in global scope since multiprocessing cannot pickle objects
def init_manager():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class Replayer:
    def __init__(self, config):
        self.config = config
        num_workers = self.config.get("num_workers")

        if not num_workers:
            # get number of available cpus, leave 1 for main thread and manager
            num_workers = os.cpu_count()
            if num_workers > 0:
                num_workers = max(num_workers - 1, 4)
            else:
                num_workers = 4
                logger.warning(
                    f"Couldn't determine the number of cpus, defaulting to {num_workers} processes."
                    f"Use the configuration parameter num_workers to change this."
                )
        self.num_workers = num_workers
        self.workers = []

    def sigint_handler(self, signum, frame):
        logger.error("Received SIGINT, shutting down...")

        for worker in self.workers:
            worker.terminate()

        for worker in self.workers:
            worker.join()
        logger.info("Workers terminated")

        raise KeyboardInterrupt

    def start_replay(
        self, connection_logs, first_event_time, total_queries, replay_start_timestamp
    ):
        manager = SyncManager()
        manager.start(init_manager)
        """ create a queue for passing jobs to the workers.  the limit will cause
        put() to block if the queue is full """
        queue = manager.Queue(maxsize=1000000)
        logger.debug(f"Running with {self.num_workers} workers")

        # find out how many processes we started with.  This is probably 1, due to the Manager
        initial_processes = len(multiprocessing.active_children())
        logger.debug(f"Initial child processes: {initial_processes}")

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        connection_semaphore = None
        num_connections = manager.Value(int, 0)
        peak_connections = manager.Value(int, 0)
        if self.config.get("limit_concurrent_connections"):
            # create an IPC semaphore to limit the total concurrency
            connection_semaphore = manager.Semaphore(
                self.config.get("limit_concurrent_connections")
            )

        per_process_stats = {}
        errors = manager.list()
        for idx in range(self.num_workers):
            per_process_stats[idx] = manager.dict()
            init_stats(per_process_stats[idx])
            replay_worker = ReplayWorker(
                idx,
                replay_start_timestamp,
                first_event_time,
                queue,
                per_process_stats[idx],
                connection_semaphore,
                num_connections,
                peak_connections,
                self.config,
                len(connection_logs),
                errors,
            )
            self.workers.append(multiprocessing.Process(target=replay_worker.replay))
            self.workers[-1].start()

        signal.signal(signal.SIGINT, self.sigint_handler)

        logger.debug(f"Total connections in the connection log: {len(connection_logs)}")

        # add all the jobs to the work queue
        for idx, connection in enumerate(connection_logs):
            if not self.put_and_retry(
                {"job_id": idx, "connection": connection}, queue, non_workers=initial_processes
            ):
                break

        # and add one termination "job"/signal for each worker so signal them to exit when
        # there is no more work
        for idx in range(self.num_workers):
            if not self.put_and_retry(False, queue, non_workers=initial_processes):
                break

        active_processes = len(multiprocessing.active_children()) - initial_processes
        logger.debug("Active processes: {}".format(active_processes))

        # and wait for the work to get done.
        logger.debug(f"{active_processes} processes running")
        cnt = 0

        self.observe_active_processes(
            active_processes,
            cnt,
            initial_processes,
            num_connections,
            peak_connections,
            per_process_stats,
            queue,
            total_queries,
        )

        # cleanup in case of error
        remaining_events = 0
        try:
            # clear out the queue in case of error to prevent broken pipe
            # exceptions from internal Queue thread
            while not queue.empty():
                remaining_events += 1
                job = queue.get_nowait()
                logger.error(f"Could not process connection log - {job.get('connection', '')}")
        except Empty:
            pass

        if remaining_events > 0:
            logger.error("Not all jobs processed, replay unsuccessful")
        logger.debug("Aggregating stats")
        aggregated_stats = init_stats({})
        for idx, stat in per_process_stats.items():
            collect_stats(aggregated_stats, stat)

        print_stats(per_process_stats)
        for worker in self.workers:
            worker.join()
        manager.shutdown()
        return aggregated_stats

    def observe_active_processes(
        self,
        active_processes,
        cnt,
        initial_processes,
        num_connections,
        peak_connections,
        per_process_stats,
        queue,
        total_queries,
    ):
        while active_processes:
            cnt += 1
            active_processes = len(multiprocessing.active_children()) - initial_processes
            if cnt % 60 == 0:
                logger.debug(f"Waiting for {active_processes} processes to finish")
                try:
                    queue_length = queue.qsize()
                    logger.debug(f"Queue length: {queue.qsize()}")
                    logger.debug(f"Remaining connections: {queue_length - len(self.workers)}")
                except NotImplementedError:
                    # support for qsize is platform-dependent
                    logger.debug("Queue length not supported.")

            # aggregate stats across all threads so far
            try:
                aggregated_stats = init_stats({})
                for idx, stat in per_process_stats.items():
                    collect_stats(aggregated_stats, stat)
                if cnt % 5 == 0:
                    display_stats(aggregated_stats, total_queries, peak_connections)
                    peak_connections.value = num_connections.value
            except KeyError:
                logger.debug("No stats to display yet.")

            time.sleep(1)

    @staticmethod
    def put_and_retry(job, queue, timeout=10, non_workers=0):
        """Retry adding to the queue indefinitely until it succeeds. This
        should only raise an exception and retry if the queue limit is hit."""
        attempt = 0
        while True:
            try:
                queue.put(job, block=True, timeout=timeout)
                break
            except Full:
                # check to make sure child processes are alive
                active_workers = len(multiprocessing.active_children()) - non_workers
                if active_workers == 0:
                    logger.error(
                        "Queue full, but there don't appear to be any active workers.  Giving up."
                    )
                    return False
                attempt += 1
                logger.info(f"Queue full, retrying attempt {attempt}")

        return True