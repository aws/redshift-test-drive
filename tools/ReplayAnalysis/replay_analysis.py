import os

import common.log as log_helper


def launch_analysis_v2():
    """Package install and server init"""

    # add explicit instructions for user

    os.system("python3 -m pip install -r requirements.txt")
    os.chdir(f"{os.getcwd()}/tools/ReplayAnalysis/gui")

    # explicit version checking
    if os.system("node -v") != 0:
        print("Please install node before proceeding.")
        exit(-1)

    if os.system("npm install") != 0:
        print("Could not install npm packages. ")

    os.system("npm run start-backend &")
    os.system("npm start")


def main():
    log_helper.init_logging("replay_analysis.log",dir='tools/ReplayAnalysis/logs',logger_name="ReplayAnalysisLogger")
    log_helper.log_version()
    launch_analysis_v2()


if __name__ == "__main__":
    main()
