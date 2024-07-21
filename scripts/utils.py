import argparse


class Utils:
    """
    Utility functions for the project.
    """

    def __init__(self):
        pass

    def parse_args():
        """
        Parse the command line arguments.
        """
        parser = argparse.ArgumentParser(description="Run the project.")
        parser.add_argument("-a", "--appName", required=True, help="second")
        parser.add_argument("-b", "--bugId", required=True, help="first input image")

        return vars(parser.parse_args())
