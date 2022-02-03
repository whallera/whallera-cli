import argparse 

from lib.mp1 import * 
from lib.discovery import discovery 
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Whallera CLI')
    
    commands = parser.add_mutually_exclusive_group()
    commands.add_argument('--discovery', action="store_true")

    commands.add_argument('--read-bank', action="store_true")
    commands.add_argument('--write-bank', action="store_true")

    args = parser.parse_args()

    if args.discovery:

        print(discovery())

    elif args.read_bank:
        pass 

    elif args.write_bank:
        pass 


