from Freez import Freez
from argparse import ArgumentParser

NAME = "freez"
DESCRIPTION = ""
EPILOG = ""

parser = ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG)
parser.add_argument("name", type=str, help="Unique name of the saved workspace")
parser.add_argument(
    "-m", "--manage", action="store_true", help="Select which windows to save"
)
parser.add_argument(
    "-c",
    "--close",
    action="store_true",
    help="Save the current workspace and close all windows",
)
parser.add_argument(
    "-s",
    "--shutdown",
    action="store_true",
    help="Save the current workspace and shutdown the system",
)
args = parser.parse_args()

if __name__ == "__main__":
    freez = Freez()
    freez.run(args)
