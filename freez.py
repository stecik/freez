from Freez import Freez
from argparse import ArgumentParser

NAME = "freez"
DESCRIPTION = ""
EPILOG = ""


def validate_args(args):
    if args.manage and not args.name:
        raise ValueError("Name is required to save workspace")


parser = ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG)

parser.add_argument("-n", "--name", type=str, help="Unique name of the saved workspace")

parser.add_argument(
    "-m", "--manage", action="store_true", help="Select which windows to save"
)

parser.add_argument(
    "-c",
    "--close",
    action="store_true",
    help="Save the current workspace (if name provided) and close all windows",
)

parser.add_argument(
    "-s",
    "--shutdown",
    action="store_true",
    help="Save the current workspace (if name provided), close all windows and shutdown the system",
)

parser.add_argument(
    "-r",
    "--reboot",
    action="store_true",
    help="Save the current workspace (if name provided), close all windows and reboot the system",
)

parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    help="List all saved workspaces",
)

parser.add_argument(
    "-d",
    "--delete",
    type=str,
    nargs="+",
    help="Delete a saved workspace",
)

args = parser.parse_args()

if __name__ == "__main__":
    try:
        validate_args(args)
        freez = Freez()
        freez.run(args)
    except Exception as e:
        print(e)
