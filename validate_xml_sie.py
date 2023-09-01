# validate_xml_sie.py

import argparse
import datetime
import os
from configparser import ConfigParser

import lxml.etree as ET
import pandas as pd

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
        output_file = "./output_files/{datetime}_report.csv".format(
            datetime=now,input_xml_file=input_xml_file)

        csv_header = "# Input XML File:" + input_xml_file
        csv_header = csv_header + "|XSD File:" + xsd_file
        csv_header = csv_header + "|xsd_check:" + str(xsd_check)
        csv_header = csv_header + "|renapo_check:" + str(renapo_check)

        with open(output_file, mode="w+", newline="", encoding="utf-8") as f:
            f.write(csv_header+ "\n")

        return output_file

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

def read_xml_to_csv(input_xml_file, output_file):
    # Parse XML
    xml_file_path = os.path.join("./input_files/", input_xml_file)

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Extract data
    data = []
    for elem in root:
        row = {}
        for subelem in elem:
            row[subelem.tag] = subelem.text
        data.append(row)

    df = pd.DataFrame(data)

    return df


def dataframe_to_csv(df, output_file):

    now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    output_csv_file = "./output_files/{datetime}_dataframe.csv".format(
        datetime=now)

    df.to_csv(output_csv_file, encoding='utf-8')

    linea_reporte = "# Output CSV File generated: " + output_csv_file

    style.change_color(style.GREEN)
    print(f"\t{linea_reporte}")

    save_on_report(output_file, linea_reporte)

def validate_vs_xsd(input_xml_file, xsd_file, output_file):
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
            linea_reporte = "# XML MAL FORMADO contra definición XSD"
        else:
            style.change_color(style.GREEN)
            linea_reporte = "# XML CORRECTO vs Definición XSD"

        print(f"\t{linea_reporte}")
        save_on_report(output_file, linea_reporte)

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

def validate_custom_rules(input_xml_file, output_file):
    try:
        # Parse XML
        xml_file_path = os.path.join("./input_files/", input_xml_file)

        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Perform your custom structure validation here
        if root.tag != "EMPLEADOS_EMPRESA":
            raise ValueError("Invalid root element. (EMPLEADOS_EMPRESA not present)")

        num_registros = 0
        linea_reporte = ""
        # Validate specific tag elements
        for empleado in root.findall('.//EMPLEADO'):
            num_registros += 1
            lista_incidencias = []
            # Perform validation for 'some_tag' elements here
            print('Registro #: ' + str(num_registros))

            # Extract CURP value
            curp_element = empleado.find('CURP').text
            if curp_element is None:
                raise ValueError("CURP element not found in XML on record # " + str(num_registros))

            curp_value = curp_element

            print('Buscando CURP: ' + curp_value )
            if curp_value:
                # Extract CURP value
                nombre_xml      = empleado.find("NOMBRE").text
                ap_paterno_xml  = empleado.find("APELLIDO_PATERNO").text
                ap_materno_xml  = empleado.find("APELLIDO_MATERNO").text
                sexo_xml        = empleado.find("SEXO").text
                lugar_nac_xml   = empleado.find("LUGAR_NACIMIENTO").text
                dia_nac_xml     = empleado.find("DIA_NACIMIENTO").text
                mes_nac_xml     = empleado.find("MES_NACIMIENTO").text
                anio_nac_xml    = empleado.find("ANIO_NACIMIENTO").text

                nombre_xml      = nombre_xml.replace("#", "Ñ")
                ap_paterno_xml  = ap_paterno_xml.replace("#", "Ñ")
                if ap_materno_xml:
                    ap_materno_xml  = ap_materno_xml.replace("#", "Ñ")

                dict_renapo_sexo = {
                    'H': '1',
                    'M': '2' 
                }

                dict_renapo = {
                    'AS': '01', 
                    'BC': '02', 
                    'BS': '03', 
                    'CC': '04', 
                    'CH': '08', 
                    'CL': '05', 
                    'CM': '06', 
                    'CS': '07', 
                    'DF': '09', 
                    'DG': '10', 
                    'GR': '12', 
                    'GT': '11', 
                    'HG': '13', 
                    'JC': '14', 
                    'MC': '15', 
                    'MN': '16', 
                    'MS': '17', 
                    'NE': '35', 
                    'NL': '19', 
                    'NT': '18', 
                    'OC': '20', 
                    'PL': '21', 
                    'QR': '23', 
                    'QT': '22', 
                    'SL': '25', 
                    'SP': '24', 
                    'SR': '26', 
                    'TC': '27', 
                    'TL': '29', 
                    'TS': '28', 
                    'VZ': '30', 
                    'YN': '31', 
                    'ZS': '32', 
                    }

                lugar_nac_curp = curp_value[11:13]
                if dict_renapo[lugar_nac_curp] != lugar_nac_xml:
                    incidencia = curp_element + ': Lugar de nacimiento: ' + lugar_nac_xml + ', no coincide con RENAPO: ' + lugar_nac_curp
                    lista_incidencias.append(incidencia)

                sexo_curp = curp_value[10:11]
                if dict_renapo_sexo[sexo_curp] != sexo_xml:
                    incidencia = curp_element + ': Sexo: ' + sexo_xml + ', no coincide con RENAPO: ' + sexo_curp
                    lista_incidencias.append(incidencia)

                dia_nac_curp = curp_value[8:10]
                if dia_nac_curp != dia_nac_xml:
                    incidencia = curp_element + ': Día Nacimiento: ' + dia_nac_xml + ', no coincide con RENAPO: ' + dia_nac_curp
                    lista_incidencias.append(incidencia)

                mes_nac_curp = curp_value[6:8]
                if mes_nac_curp != mes_nac_xml:
                    incidencia = curp_element + ': Mes Nacimiento: ' + mes_nac_xml + ', no coincide con RENAPO: ' + mes_nac_curp
                    lista_incidencias.append(incidencia)

                anio_nac_curp = curp_value[4:6]
                dif_homonimia = curp_value[16:17]

                if dif_homonimia.isdigit() == True:
                    anio_nac_curp = 1900 + int(anio_nac_curp)
                else:
                    anio_nac_curp = 2000 + int(anio_nac_curp)

                if anio_nac_curp != int(anio_nac_xml):
                    incidencia = curp_element + ': Año Nacimiento: ' + str(anio_nac_xml) + ', no coincide con RENAPO: ' + str(anio_nac_curp)
                    lista_incidencias.append(incidencia)

                for incidencia in lista_incidencias:
                    style.change_color(style.RED)
                    print(incidencia)
                    save_on_report(output_file, incidencia)

            style.change_color(style.GREEN)
            linea_reporte = '************'
            print(linea_reporte)
            save_on_report(output_file, linea_reporte)


    except FileNotFoundError:
        print("XML file not found.")
    except ET.ParseError:
        print("Error parsing XML file.")
    except ValueError as ve:
        print("Validation error:", ve)

def search_on_ws():
    pass

def save_on_report(output_file, linea):
    with open(output_file, mode="a", newline="", encoding="utf-8") as f:
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
        df = read_xml_to_csv(input_xml_file, output_file)
        dataframe_to_csv(df, output_file)
        validate_custom_rules(input_xml_file, output_file)
