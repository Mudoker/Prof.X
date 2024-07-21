# Base configuration for all scripts
import sys
import importlib

sys.path.append("./scripts")

modules_to_reload = [
    "scripts.utils",
    "scripts.styler",
]
[importlib.reload(sys.modules[m]) for m in modules_to_reload if m in sys.modules]

# Import user-defined scripts
from scripts.utils import Utils
from scripts.styler import Styler

styler = Styler()


# Main function
def main():
    styler.log("Welcome to X-Men for automed GUI-based testing!", format="box")

    # Parse the command line arguments
    args = Utils.parse_args()

    appName = args["appName"]
    bugId = args["bugId"]

    styler.log(f"The test is for {appName} with bugId {bugId}")


# Call the main function if the script is executed directly
if __name__ == "__main__":
    main()
