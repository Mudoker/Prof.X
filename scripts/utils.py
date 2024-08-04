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
        parser.add_argument("-app", "--appName", required=True, help="Name of the application.")
        parser.add_argument("-bug", "--bugId", required=True, help="ID of the bug.")

        return vars(parser.parse_args())
