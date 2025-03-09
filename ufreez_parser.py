from argparse import ArgumentParser

NAME = "ufreez"
DESCRIPTION = ""
EPILOG = ""


parser = ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG)
parser.add_argument("name", type=str, help="Unique name of the saved workspace")

args = parser.parse_args()
