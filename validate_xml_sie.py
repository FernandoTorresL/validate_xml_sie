# validate_xml_sie.py

import argparse
from configparser import ConfigParser


def read_user_cli_args():
    """Handles the CLI user interactions.

    Returns:
        argparse.Namespace: Populated namespace object
    """
    parser = argparse.ArgumentParser(
        description="validate xml file and xml tags vs a Web Service data"
    )

    parser.add_argument(
        "xml_file", nargs="+", type=str, help="enter the xml filename"
    )
    parser.add_argument(
        "-x",
        "--xsd",
        action="store_true",
        help="check xml file vs xsd definition file",
    )
    parser.add_argument(
        "-r",
        "--renapo",
        action="store_true",
        help="check xml data vs WS RENAPO",
    )

    return parser.parse_args()


def _get_ws_renapo_url():
    """Fetch the WS-URL from your configuration file.

    Expects a configuration file named "secrets.ini" with structure:

        [urls]
        ws_url_renapo=<YOUR-WS_RENAPO-URL>
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["urls"]["ws_url_renapo"]

def _get_xsd_filename():
    """Fetch the XSD definition file from your configuration file.

    Expects a xsd definition file named "xsd_file.xsd":

        [urls]
        ws_url_renapo=<YOUR-WS_RENAPO-URL>

        [files]
        xsd_file=filename.xsd
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["files"]["xsd_file"]

def create_report():
    pass

def read_xml():
    pass

def validate_vs_xsd():
    pass

def analyzing_data():
    pass

def validate_xsd_regex():
    pass

def validate_custom_rules():
    pass

def search_on_ws():
    pass

def save_on_report():
    pass


if __name__ == '__main__':

    # Get user parameters
    read_user_cli_args()

    user_args = read_user_cli_args()
    # Check the args values
    print(f"\tParameters:{user_args.xml_file, user_args.xsd, user_args.renapo}", end="\n\n")

    # Testing getting a secret
    print(f"\tInput XML File:\t{user_args.xml_file}", end="\n")

    ws_renapo_url=_get_ws_renapo_url()
    print(f"\tURL WS_RENAPO:\t{ws_renapo_url}", end="\n")

    xsd_filename=_get_xsd_filename()
    print(f"\tXSD File:\t{xsd_filename}", end="\n")

