from argparse import ArgumentParser

NAME = "freez"
DESCRIPTION = ""
EPILOG = ""


parser = ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG)
parser.add_argument("name", type=str, help="Unique name of the saved workspace")
parser.add_argument(
    "-c", "--close", help="Save the current workspace and close all windows"
)
parser.add_argument(
    "-s", "--shutdown", help="Save the current workspace and shutdown the system"
)
args = parser.parse_args()
