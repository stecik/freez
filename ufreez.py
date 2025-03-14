from argparse import ArgumentParser
from Freez import Ufreez

NAME: str = "ufreez"
DESCRIPTION: str = (
    "A command-line utility to restore previously saved workspaces using 'freez'."
    "Allows users to reopen saved window sessions, list available workspace snapshots, "
    "or delete them when no longer needed."
    "ufreez can be customized in the config.py file."
)
EPILOG: str = (
    "Examples:"
    "  Reopen a saved workspace:             ufreez -n my_workspace || "
    "  List all saved workspaces:            ufreez -l || "
    "  Delete a saved workspace:             ufreez -d my_workspace || "
    "For more details, refer to the documentation or use -h for help. || "
)


parser = ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG)

mode_group = parser.add_mutually_exclusive_group()

mode_group.add_argument(
    "-n", "--name", type=str, help="Unique name of the saved workspace"
)

mode_group.add_argument(
    "-l",
    "--list",
    action="store_true",
    help="List all saved workspaces",
)

mode_group.add_argument(
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
