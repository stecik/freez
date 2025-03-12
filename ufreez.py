from argparse import ArgumentParser
from Freez import Ufreez

NAME = "ufreez"
DESCRIPTION = ""
EPILOG = ""


parser = ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG)

parser.add_argument("-n", "--name", type=str, help="Unique name of the saved workspace")

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
        ufreez = Ufreez()
        ufreez.run(args)
    except Exception as e:
        print(e)
