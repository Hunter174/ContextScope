import argparse

from app.bootstrap import bootstrap


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Force setup wizard"
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset configuration and secrets"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    bootstrap(
        force_setup=args.setup,
        reset=args.reset
    )