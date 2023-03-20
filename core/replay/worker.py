import datetime
import logging
import random
import sys
import threading
import time
import traceback
from queue import Empty

from common.log import init_logging
from core.replay.connection_thread import ConnectionThread
from core.replay.stats import collect_stats, init_stats


class ReplayWorker:
    logger = logging.getLogger("SimpleReplayWorkerLogger")

    def __init__(
        self,
        process_idx,
        replay_start_time,
        first_event_time,
        queue,
        worker_stats,
        connection_semaphore,
        num_connections,
        peak_connections,
        config,
        total_connections,
        error_logger,
        replay_id,

    ):
        self.peak_connections = peak_connections
        self.num_connections = num_connections
        self.connection_semaphore = connection_semaphore
        self.worker_stats = worker_stats
        self.queue = queue
        self.first_event_time = first_event_time
        self.replay_start_time = replay_start_time
        self.process_idx = process_idx
        self.config = config
        self.default_interface = self.config.get("default_interface")
        self.odbc_driver = (self.config.get("odbc_driver"),)
        self.total_connections = total_connections
        self.error_logger = error_logger
        self.replay_id = replay_id


    def replay(self):
        """Worker process to distribute the work among several processes.  Each
        worker pulls a connection off the queue, waits until its time to start
        it, spawns a thread to execute the actual connection and associated
        transactions, and then repeats."""
        # Logging needs to be separately initialized so that the worker can log to a separate log file
        init_logging(
            f"replay_worker-{self.process_idx}",
            dir = f"simplereplay_logs/replay_log-{self.replay_id}",
            logger_name="SimpleReplayWorkerLogger",
            level=self.config.get("log_level", "INFO"),
            script_type=f"replay worker - {self.process_idx}"
        )

        # map thread to stats dict
        connection_threads = {}
        connections_processed = 0

        threading.current_thread().name = "0"

        perf_lock = threading.Lock()

        try:
            # stagger worker startup to not hammer the get_cluster_credentials api
            time.sleep(random.randrange(1, 3))
            self.logger.debug(f"Worker {self.process_idx} ready for jobs")

            # time to block waiting for jobs on the queue
            timeout_sec = 10

            last_empty_queue_time = None

            # get the next job off the queue and wait until its due
            # loop terminates when a False is received over the queue
            while True:
                try:
                    if self.connection_semaphore is not None:
                        self.logger.debug(
                            f"Checking for connection throttling ({self.num_connections.value} / "
                            f"{self.config['limit_concurrent_connections']} active connections)"
                        )
                        sem_start = time.time()
                        self.connection_semaphore.acquire()
                        sem_elapsed = time.time() - sem_start
                        self.logger.debug(f"Waited {sem_elapsed} sec for semaphore")

                    job = self.queue.get(timeout=timeout_sec)
                except Empty:
                    if self.connection_semaphore is not None:
                        self.connection_semaphore.release()

                    elapsed = (
                        int(time.time() - last_empty_queue_time)
                        if last_empty_queue_time
                        else 0
                    )
                    # take into account the initial timeout
                    elapsed += timeout_sec
                    empty_queue_timeout_sec = self.config.get(
                        "empty_queue_timeout_sec", 120
                    )
                    self.logger.debug(
                        f"No jobs for {elapsed} seconds (timeout {empty_queue_timeout_sec})"
                    )
                    # normally processes exit when they get a False on the queue,
                    # but in case of some error we exit if the queue is empty for some time
                    if elapsed > empty_queue_timeout_sec:
                        self.logger.warning(f"Queue empty for {elapsed} sec, exiting")
                        break
                    if last_empty_queue_time is None:
                        last_empty_queue_time = time.time()
                    continue

                last_empty_queue_time = None

                if job is False:
                    self.logger.debug("Got termination signal, finishing up.")
                    break

                thread_stats = init_stats({})

                # how much time has elapsed since the replay started
                time_elapsed_ms = (
                    datetime.datetime.now(tz=datetime.timezone.utc)
                    - self.replay_start_time
                ).total_seconds() * 1000.0

                # what is the time offset of this connection job relative to the first event
                connection_offset_ms = job["connection"].offset_ms(
                    self.first_event_time
                )
                delay_sec = (connection_offset_ms - time_elapsed_ms) / 1000.0

                self.logger.debug(
                    f"Got job {job['job_id'] + 1}, delay {delay_sec:+.3f} sec (extracted connection time: {job['connection'].session_initiation_time})"
                )

                # if connection time is more than a few ms in the future, sleep until its due.
                # this is approximate and we use "a few ms" here due to the imprecision of
                # sleep as well as the time for the remaining code to spawn a thread and actually
                # make the db connection.
                if connection_offset_ms - time_elapsed_ms > 10:
                    time.sleep(delay_sec)

                self.logger.debug(
                    f"Starting job {job['job_id'] + 1} (extracted connection time: "
                    f"{job['connection'].session_initiation_time}). {len(threading.enumerate())}, "
                    f"{threading.active_count()} connections active."
                )

                connection_thread = ConnectionThread(
                    self.process_idx,
                    job["job_id"],
                    job["connection"],
                    self.default_interface,
                    self.odbc_driver,
                    self.replay_start_time,
                    self.first_event_time,
                    self.error_logger,
                    thread_stats,
                    self.num_connections,
                    self.peak_connections,
                    self.connection_semaphore,
                    perf_lock,
                    self.config,
                    self.total_connections,
                )
                connection_thread.name = f"{job['job_id']}"
                connection_thread.start()
                connection_threads[connection_thread] = thread_stats

                self.join_finished_threads(
                    connection_threads, self.worker_stats, wait=False
                )

                connections_processed += 1

            self.logger.debug(
                f"Waiting for {len(connection_threads)} connections to finish..."
            )
            self.join_finished_threads(connection_threads, self.worker_stats, wait=True)
        except Exception as e:
            self.logger.error(f"Process {self.process_idx} threw exception: {e}")
            self.logger.debug("".join(traceback.format_exception(*sys.exc_info())))
            
        if connections_processed:
            self.logger.debug(
                f"Max connection offset for this process: {self.worker_stats['connection_diff_sec']:.3f} sec"
            )

        self.logger.debug(f"Process {self.process_idx} finished")

    def join_finished_threads(self, connection_threads, worker_stats, wait=False):
        # join any finished threads
        finished_threads = []
        for t in connection_threads:
            if not t.is_alive() or wait:
                self.logger.debug(
                    f"Joining thread {t.connection_log.session_initiation_time}"
                )
                t.join()
                collect_stats(worker_stats, connection_threads[t])
                finished_threads.append(t)

        # remove the joined threads from the list of active ones
        for t in finished_threads:
            del connection_threads[t]

        self.logger.debug(
            f"Joined {len(finished_threads)} threads, {len(connection_threads)} still active."
        )
        return len(finished_threads)
