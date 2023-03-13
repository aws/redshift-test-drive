import os
from common.util import init_logging


def launch_analysis_v2():
    """Package install and server init"""

    # add explicit instructions for user

    os.system("pip install -r requirements.txt")
    os.chdir(f"{os.getcwd()}/tools/replay-analysis/util/gui")

    # explicit version checking
    if os.system("node -v") != 0:
        print("Please install node before proceeding.")
        exit(-1)

    if os.system("npm install") != 0:
        print("Could not install npm packages. ")

    os.system("npm run start-backend &")
    os.system("npm start")


def main():
    logger = init_logging()
    launch_analysis_v2()


if __name__ == "__main__":
    main()
