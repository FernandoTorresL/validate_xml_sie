# validate_xml_sie.py

import argparse
import datetime
import os
from configparser import ConfigParser

import lxml.etree as ET

import style


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
        "--xsd_check",
        action="store_true",
        help="check xml file vs xsd definition file",
    )
    parser.add_argument(
        "-r",
        "--renapo_check",
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

def _get_xsd_file():
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

def create_report_file(input_xml_file, xsd_file, xsd_check, renapo_check):
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
        output_report_file = "./output_files/{datetime}_report.csv".format(
            datetime=now,input_xml_file=input_xml_file)

        csv_header = "# Input XML File:" + input_xml_file
        csv_header = csv_header + "|XSD File:" + xsd_file
        csv_header = csv_header + "|xsd_check:" + str(xsd_check)
        csv_header = csv_header + "|renapo_check:" + str(renapo_check)

        with open(output_report_file, mode="w+", newline="", encoding="utf-8") as f:
            f.write(csv_header+ "\n")

        return output_report_file

def check_xml_input_file(input_xml_file, output_file):
    style.change_color(style.WHITE)
    linea_reporte = "Revisando existencia de archivo XML"
    print(linea_reporte)

    xml_file_path = os.path.join("./", "input_files")
    file_exist=False

    for filename in os.listdir(xml_file_path):
        if filename.endswith(".xml") and filename == input_xml_file:
            file_exist= True

    if not file_exist:
        style.change_color(style.RED)
        linea_reporte = xml_file_path + "/" + input_xml_file + "|File not found."
        print(f"\t{linea_reporte}")

        save_on_report(output_file, linea_reporte)

    return file_exist

def read_xml():
    pass

def validate_vs_xsd(input_xml_file, xsd_file, output_report_file):
    #Validate XML against XSD
    try:
        style.change_color(style.WHITE)
        linea_reporte = "Validando XML contra XSD"
        print(linea_reporte)

        xml_file_path = os.path.join("./input_files/", input_xml_file)
        xsd_file_path = os.path.join("./archivo_xsd/", xsd_file)

        xmlschema = ET.XMLSchema(ET.parse(xsd_file_path))

        tree = ET.parse(xml_file_path)

        if xmlschema.validate(tree) == False:
            style.change_color(style.RED)
            linea_reporte = "XML MAL FORMADO contra definición XSD"
        else:
            style.change_color(style.GREEN)
            linea_reporte = "XML CORRECTO vs Definición XSD"

        print(f"\t{linea_reporte}")
        save_on_report(output_report_file, linea_reporte)

    except FileNotFoundError:
        style.change_color(style.RED)
        print("File not found.")
    except ET.ParseError:
        style.change_color(style.RED)
        print("Error parsing XML file.")
    except ValueError as ve:
        style.change_color(style.RED)
        print("Validation error:", ve)

def analyzing_data():
    pass

def validate_xsd_regex():
    pass

def validate_custom_rules():
    pass

def search_on_ws():
    pass

def save_on_report(output_report_file, linea):
    with open(output_report_file, mode="a", newline="", encoding="utf-8") as f:
        f.write(linea + "\n")


if __name__ == "__main__":

    # Get user parameters
    read_user_cli_args()

    user_args = read_user_cli_args()
    # Check the args values
    style.change_color(style.BLUE)

    print(f"\tParameters:{user_args.xml_file, user_args.xsd_check, user_args.renapo_check}", end="\n\n")
    print(f"\tParameter xml_file:\t{user_args.xml_file}", end="\n")
    print(f"\tParameter xsd_check:\t{user_args.xsd_check}", end="\n")
    print(f"\tParameter renapo_check:\t{user_args.renapo_check}", end="\n\n")

    # Testing getting a secret
    input_xml_file = user_args.xml_file[0]
    print(f"\tInput XML File:\t{input_xml_file}", end="\n")

    ws_renapo_url = _get_ws_renapo_url()
    print(f"\tURL WS_RENAPO:\t{ws_renapo_url}", end="\n")

    xsd_file = _get_xsd_file()
    print(f"\tXSD File:\t{xsd_file}", end="\n\n")

    # MAIN
    # Create output file and save params
    output_file = create_report_file(input_xml_file, xsd_file, user_args.xsd_check, user_args.renapo_check)
    print(f"\tOutput File:\t{output_file}", end="\n")

    # Check that XML File exist
    #print(check_xml_input_file(input_xml_file))
    print("", end="\n")
    if check_xml_input_file(input_xml_file, output_file):
        validate_vs_xsd(input_xml_file, xsd_file, output_file)


