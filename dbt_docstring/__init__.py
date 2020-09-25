#!/usr/bin/env python3
import argparse, os, sys

COMMAND = "dbt_docstring"


def main():
    """
    Entry point
    """
    parser = argparse.ArgumentParser(COMMAND)

    parser.add_argument(
        "-a", "--arg",
        help="Some arg")

    args = parser.parse_args()


if __name__ == "__main__":
    main()
