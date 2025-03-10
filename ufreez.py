from argparse import ArgumentParser
from Freez import Ufreez

NAME = "ufreez"
DESCRIPTION = ""
EPILOG = ""


parser = ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG)
parser.add_argument("name", type=str, help="Unique name of the saved workspace")

args = parser.parse_args()

if __name__ == "__main__":
    ufreez = Ufreez()
    ufreez.run(args)
