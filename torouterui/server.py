
from torouterui import app
import argparse


def main():
    """Primary entry-point for torouterui.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
        help="enable debugging interface")
    args = parser.parse_args()
    app.run(debug=args.debug)
