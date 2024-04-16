#!/usr/bin/env python3

import argparse
import logging
import os

from dotenv import load_dotenv

# Load environment variables for specified env file, or from current directory env file
if os.getenv("ENV_FILE_PATH"):
    load_dotenv(os.getenv("ENV_FILE_PATH"))
else:
    load_dotenv()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='program')
    parser.add_argument('-v', help="verbose mode", action="count")

    args = parser.parse_args()

    if args.v is not None:
        if args.v == 1:
            logging.basicConfig(level=logging.INFO)
        elif args.v > 1:
            logging.basicConfig(level=logging.DEBUG)
