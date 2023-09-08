# validate_xml_sie.py

import argparse
import datetime
import os
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from configparser import ConfigParser

import lxml.etree as ET
import pandas as pd
from suds.client import Client
from tqdm import tqdm

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
    parser.add_argument(
        "-u",
        "--use_threads",
        action="store_true",
        help="use threads",
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

def create_report_file(input_xml_file, xsd_file, xsd_check, renapo_check, use_threads):
        lineas=[]
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
        output_file = "./output_files/{datetime}_report.csv".format(
            datetime=now,input_xml_file=input_xml_file)

        comment = "# Input XML File:" + input_xml_file
        lineas.append(comment)
        comment = "# XSD File:" + xsd_file
        lineas.append(comment)
        comment = "# xsd_check:" + str(xsd_check)
        lineas.append(comment)
        comment = "# renapo_check:" + str(renapo_check)
        lineas.append(comment)
        comment = "# use_threads:" + str(use_threads)
        lineas.append(comment)

        with open(output_file, mode="w+", newline="", encoding="utf-8") as f:
            for linea in lineas:
                f.write(linea+ "\n")

        print(f"\n\tReport File:\t{output_file}", end="\n\n")
        comment = "# Report File: " + output_file
        save_on_report(output_file, comment)

        return output_file

def check_xml_input_file(input_xml_file, output_file):
    xml_file_path = os.path.join("./")
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


def read_xml_tree(input_xml_file):
    # Parse XML
    xml_file_path = os.path.join("./", input_xml_file)

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    return root


def read_xml_to_dataframe(root):
    style.change_color(style.WHITE)
    linea_reporte = "Exporting XML file to dataframe"
    print(linea_reporte)

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
    style.change_color(style.WHITE)
    linea_reporte = "Exporting dataframe to CSV File"
    print(linea_reporte)

    now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    output_csv_file = "./output_files/{datetime}_dataframe.csv".format(
        datetime=now)

    df.to_csv(output_csv_file, encoding="utf-8")

    linea_reporte = "# Output CSV File generated: " + output_csv_file

    style.change_color(style.GREEN)
    print(f"\t{linea_reporte}")
    save_on_report(output_file, linea_reporte)


def validate_vs_xsd(input_xml_file, xsd_file, xsd_check, output_file):
    #Validate XML against XSD
    style.change_color(style.WHITE)
    linea_reporte = "# Validating XML VS XSD Definition file..."
    print(linea_reporte)
    save_on_report(output_file, linea_reporte)

    if not user_args.xsd_check:
        linea_reporte = "# ...parameter xsd_check=False. Won't check vs XSD File"
        style.change_color(style.YELLOW)
        print(f"{linea_reporte}", end="\n")
        save_on_report(output_file, linea_reporte)
        return

    try:
        style.change_color(style.WHITE)
        linea_reporte = "# ...parameter xsd_check=True. Initiate check vs XSD File"
        print(f"{linea_reporte}", end="\n")
        save_on_report(output_file, linea_reporte)

        xml_file_path = os.path.join("./", input_xml_file)
        xsd_file_path = os.path.join("./archivo_xsd/", xsd_file)

        xmlschema = ET.XMLSchema(ET.parse(xsd_file_path))
        tree = ET.parse(xml_file_path)

        if xmlschema.validate(tree):
            style.change_color(style.GREEN)
            linea_reporte = "# XML CORRECTO vs Definición XSD"
        else:
            style.change_color(style.RED)
            linea_reporte = "# XML MAL FORMADO contra definición XSD"

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

def validate_custom_rules(root, renapo_gender_dict, renapo_state_dict, output_file):
    style.change_color(style.WHITE)
    linea_reporte = "# Validating Custom Rules (CURP values)"
    print(f"\t{linea_reporte}", end="\n")
    save_on_report(output_file, linea_reporte)

    try:
        num_registros = 0
        num_incidencias = 0
        renapo_gender_dict = dict(renapo_gender_dict)
        renapo_state_dict = dict(renapo_state_dict)
        # Validate specific tag elements
        for registro in root.findall(".//EMPLEADO"):
            num_registros += 1
            lista_incidencias = []

            # Extract CURP value
            curp_element = registro.find("CURP").text

            if curp_element is None:
                num_incidencias += 1
                raise ValueError("CURP element not found in XML on record # " + str(num_registros))

            curp_value = curp_element

            #print("Buscando CURP: " + curp_value )
            if curp_value:
                # Extract CURP value
                nombre_xml      = registro.find("NOMBRE").text
                ap_paterno_xml  = registro.find("APELLIDO_PATERNO").text
                ap_materno_xml  = registro.find("APELLIDO_MATERNO").text
                sexo_xml        = registro.find("SEXO").text
                lugar_nac_xml   = registro.find("LUGAR_NACIMIENTO").text
                dia_nac_xml     = registro.find("DIA_NACIMIENTO").text
                mes_nac_xml     = registro.find("MES_NACIMIENTO").text
                anio_nac_xml    = registro.find("ANIO_NACIMIENTO").text

                nombre_xml      = nombre_xml.replace("#", "Ñ")
                ap_paterno_xml  = ap_paterno_xml.replace("#", "Ñ")
                if ap_materno_xml:
                    ap_materno_xml  = ap_materno_xml.replace("#", "Ñ")

                lugar_nac_curp = str(curp_value[11:13])
                if renapo_state_dict[lugar_nac_curp] != lugar_nac_xml:
                    incidencia = curp_element + "|Lugar de nacimiento XML: " + lugar_nac_xml + ", doesn't match CURP XML value: " + lugar_nac_curp
                    lista_incidencias.append(incidencia)

                sexo_curp = str(curp_value[10:11])
                if renapo_gender_dict[sexo_curp] != sexo_xml:
                    incidencia = curp_element + "|Sexo XML: " + sexo_xml + ", doesn't match CURP XML value: " + sexo_curp
                    lista_incidencias.append(incidencia)

                dia_nac_curp = curp_value[8:10]
                if dia_nac_curp != dia_nac_xml:
                    incidencia = curp_element + "|Día Nacimiento XML: " + dia_nac_xml + ", doesn't match CURP XML value: " + dia_nac_curp
                    lista_incidencias.append(incidencia)

                mes_nac_curp = curp_value[6:8]
                if mes_nac_curp != mes_nac_xml:
                    incidencia = curp_element + "|Mes Nacimiento XML: " + mes_nac_xml + ", doesn't match CURP XML value: " + mes_nac_curp
                    lista_incidencias.append(incidencia)

                anio_nac_curp = curp_value[4:6]
                dif_homonimia = curp_value[16:17]

                if dif_homonimia.isdigit() == True:
                    anio_nac_curp = 1900 + int(anio_nac_curp)
                else:
                    anio_nac_curp = 2000 + int(anio_nac_curp)

                if anio_nac_curp != int(anio_nac_xml):
                    incidencia = curp_element + "|Año Nacimiento XML: " + str(anio_nac_xml) + ", doesn't match calculated CURP XML value: " + str(anio_nac_curp)
                    lista_incidencias.append(incidencia)

                for incidencia in lista_incidencias:
                    num_incidencias += 1
                    style.change_color(style.RED)
                    #print(incidencia)
                    save_on_report(output_file, incidencia)

        style.change_color(style.WHITE)
        linea_reporte = "#Total Records on XML: " + str(num_registros) + "|Total Errors on XML: " + str(num_incidencias)
        print(f"{linea_reporte}", end="\n\n")
        save_on_report(output_file, linea_reporte)

    except FileNotFoundError:
        print("XML file not found.")
    except ET.ParseError:
        print("Error parsing XML file.")
    except ValueError as ve:
        print("Validation error:", ve)

def create_queue(root):
    data_queue = queue.Queue()
    total_curps = len(root.findall(".//EMPLEADO"))
    progreso = tqdm(total = total_curps,desc = "Recuperando",leave = True, unit = 'Reg')

    for curp in root.findall(".//EMPLEADO"):
        progreso.update()
        data_list = []
        curp_value      = curp.find("CURP").text
        nombre_xml      = curp.find("NOMBRE").text
        ap_paterno_xml  = curp.find("APELLIDO_PATERNO").text
        ap_materno_xml  = curp.find("APELLIDO_MATERNO").text
        sexo_xml        = curp.find("SEXO").text
        lugar_nac_xml   = curp.find("LUGAR_NACIMIENTO").text
        dia_nac_xml     = curp.find("DIA_NACIMIENTO").text
        mes_nac_xml     = curp.find("MES_NACIMIENTO").text
        anio_nac_xml    = curp.find("ANIO_NACIMIENTO").text

        nombre_xml      = nombre_xml.replace("#", "Ñ")
        ap_paterno_xml  = ap_paterno_xml.replace("#", "Ñ")
        if ap_materno_xml:
            ap_materno_xml  = ap_materno_xml.replace("#", "Ñ")

        data_list.append(curp_value)
        data_list.append(nombre_xml)
        data_list.append(ap_paterno_xml)
        data_list.append(ap_materno_xml)
        data_list.append(sexo_xml)
        data_list.append(lugar_nac_xml)
        data_list.append(dia_nac_xml)
        data_list.append(mes_nac_xml)
        data_list.append(anio_nac_xml)

        data_queue.put(data_list)
    progreso.close()
    return data_queue

def search_on_ws(urlWSRENAPO, root, renapo_check, use_threads, output_file):
    # Use WS RENAPO?
    style.change_color(style.WHITE)
    linea_reporte = "# Search data on WS RENAPO..."
    print(linea_reporte)
    save_on_report(output_file, linea_reporte)

    if not renapo_check:
        linea_reporte = "# ...parameter renapo_check=False. Won't check vs WS"
        style.change_color(style.YELLOW)
        print(f"\t{linea_reporte}", end="\n")
        save_on_report(output_file, linea_reporte)
        return

    # Use threads?
    style.change_color(style.WHITE)
    linea_reporte = "# Check vs WS RENAPO. Check thread option..."
    print(f"{linea_reporte}", end="\n")
    save_on_report(output_file, linea_reporte)

    # Get all the data from xml to search on WS and compare results
    data_list = create_queue(root)
    style.change_color(style.WHITE)
    if use_threads:
        linea_reporte = "# ...parameter use_threads=True. Will use threads"
        print(f"\t{linea_reporte}", end="\n")
        save_on_report(output_file, linea_reporte)

        create_threads(data_list, output_file, urlWSRENAPO)
    else:
        style.change_color(style.YELLOW)
        linea_reporte = "# ...parameter use_threads=False. Won't use threads"
        print(f"\t{linea_reporte}", end="\n")
        save_on_report(output_file, linea_reporte)

        style.change_color(style.GREEN)

        with tqdm(total=data_list.qsize(), desc = "Consultando", leave=True, unit = "queries") as pbar:
            consultaWS(data_list, pbar, output_file, ws_renapo_url)

def create_threads(data_list_threads, output_file, ws_renapo_url):
    threads = os.cpu_count() + 6

    linea_reporte = "# Using " + str(threads) + " thread(s)"
    style.change_color(style.GREEN)
    print(f"{linea_reporte}", end="\n")
    save_on_report(output_file, linea_reporte)

    with tqdm(total=data_list_threads.qsize(), desc="Consultando", leave=True, unit="queries") as pbar:
        with ThreadPoolExecutor(max_workers = threads, thread_name_prefix="WS_queries") as ex:
            futures = [ex.submit(consultaWS, data_list_threads, pbar, output_file, ws_renapo_url) for i in range(threads)]

def consultaWS(data_list, pbar, output_file, urlWSRENAPO):
    while not data_list.empty():
        try:
            style.change_color(style.WHITE)
            # Update the progress bar
            pbar.update(1)
            total_records = data_list.qsize()
            record_data = data_list.get_nowait()
            data_list.task_done()
            curp_value        = record_data[0]
            nombre_xml        = record_data[1]
            ap_paterno_xml    = record_data[2]
            ap_materno_xml    = record_data[3]
            sexo_xml          = record_data[4]
            lugar_nac_xml     = record_data[5]
            dia_nac_xml       = record_data[6]
            mes_nac_xml       = record_data[7]
            anio_nac_xml      = record_data[8]

            style.change_color(style.GREEN)

            cliente = Client(urlWSRENAPO, cache=None)
            cliente.set_options(location=urlWSRENAPO)
            response_ws_renapo = cliente.service.ConsultaDatosCURP(curp_value)

            # ... process the response_ws_renapo ...
            if response_ws_renapo.CodigoError == 0:
                if nombre_xml != response_ws_renapo.Nombres:
                    incidencia = curp_value + "|NOMBRE(S) in XML: " + nombre_xml + ", doesn't match RENAPO response: " + response_ws_renapo.Nombres
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)

                if ap_paterno_xml != response_ws_renapo.Apellido1:
                    incidencia = curp_value + "|APELLIDO_PATERNO in XML: " + ap_paterno_xml + ", doesn't match RENAPO response: " + response_ws_renapo.Apellido1
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)

                if ap_materno_xml != response_ws_renapo.Apellido2:
                    if response_ws_renapo.Apellido2 == None:
                        incidencia = curp_value + "|APELLIDO_MATERNO in XML: " + ap_materno_xml + ", doesn't match RENAPO response: NULL"
                    else:
                        incidencia = curp_value + "|APELLIDO_MATERNO in XML: " + ap_materno_xml + ", doesn't match RENAPO response: " + response_ws_renapo.Apellido2
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)

                lugar_nac_curp = curp_value[11:13]
                if renapo_state_dict[lugar_nac_curp] != lugar_nac_xml:
                    incidencia = curp_value + "|Lugar de nacimiento: " + lugar_nac_xml + ", doesn't match RENAPO response: " + lugar_nac_curp
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)

                sexo_curp = curp_value[10:11]
                if renapo_gender_dict[sexo_curp] != sexo_xml:
                    incidencia = curp_value + "|Sexo: " + sexo_xml + ", doesn't match RENAPO response: " + sexo_curp
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)

                dia_nac_curp = curp_value[8:10]
                if dia_nac_curp != dia_nac_xml:
                    incidencia = curp_value + "|Día Nacimiento: " + dia_nac_xml + ", doesn't match RENAPO response: " + dia_nac_curp
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)

                mes_nac_curp = curp_value[6:8]
                if mes_nac_curp != mes_nac_xml:
                    incidencia = curp_value + "|Mes Nacimiento: " + mes_nac_xml + ", doesn't match RENAPO response: " + mes_nac_curp
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)

                anio_nac_curp = curp_value[4:6]
                dif_homonimia = curp_value[16:17]

                if dif_homonimia.isdigit():
                    anio_nac_curp = 1900 + int(anio_nac_curp)
                else:
                    anio_nac_curp = 2000 + int(anio_nac_curp)

                if anio_nac_curp != int(anio_nac_xml):
                    incidencia = curp_value + "|Año Nacimiento XML: " + str(anio_nac_xml) + ", doesn't match RENAPO response: " + str(anio_nac_curp)
                    record_data.append(incidencia)
                    save_on_report(output_file, incidencia)
            else:
                incidencia = curp_value + "|No data from WS-RENAPO"
                record_data.append(incidencia)
                save_on_report(output_file, incidencia)

        except Exception as mensaje:
            incidencia = curp_value + "|Error? (WS-RENAPO)"
            style.change_color(style.RED)
            print(incidencia)
            record_data.append(incidencia)
            save_on_report(output_file, record_data)

def save_on_report(output_file, linea):
    with open(output_file, mode="a", newline="", encoding="utf-8") as f:
        f.write(linea + "\n")


if __name__ == "__main__":

    renapo_gender_dict = {
                    "H": "1",
                    "M": "2"
                }

    renapo_state_dict = {
        "AS": "01",
        "BC": "02",
        "BS": "03",
        "CC": "04",
        "CH": "08",
        "CL": "05",
        "CM": "06",
        "CS": "07",
        "DF": "09",
        "DG": "10",
        "GR": "12",
        "GT": "11",
        "HG": "13",
        "JC": "14",
        "MC": "15",
        "MN": "16",
        "MS": "17",
        "NE": "35",
        "NL": "19",
        "NT": "18",
        "OC": "20",
        "PL": "21",
        "QR": "23",
        "QT": "22",
        "SL": "25",
        "SP": "24",
        "SR": "26",
        "TC": "27",
        "TL": "29",
        "TS": "28",
        "VZ": "30",
        "YN": "31",
        "ZS": "32",
        }

    # Get user parameters
    read_user_cli_args()
    user_args = read_user_cli_args()

    style.change_color(style.BLUE)
    print(f"\tParameters:{user_args.xml_file, user_args.xsd_check, user_args.renapo_check, user_args.use_threads}", end="\n\n")
    print(f"\tParameter xml_file:\t{user_args.xml_file}", end="\n")
    print(f"\tParameter xsd_check:\t{user_args.xsd_check}", end="\n")
    print(f"\tParameter renapo_check:\t{user_args.renapo_check}", end="\n")
    print(f"\tParameter use_thread:\t{user_args.use_threads}", end="\n\n")

    # Testing getting a secret
    input_xml_file = user_args.xml_file[0]
    print(f"\tInput XML File:\t{input_xml_file}", end="\n")

    ws_renapo_url = _get_ws_renapo_url()
    print(f"\tURL WS_RENAPO:\t{ws_renapo_url}", end="\n")

    xsd_file = _get_xsd_file()
    print(f"\tXSD File:\t{xsd_file}", end="\n")

    # Create output file and save params
    output_file = create_report_file(input_xml_file, xsd_file, user_args.xsd_check, user_args.renapo_check, user_args.use_threads)

    # Check that XML File exist
    if check_xml_input_file(input_xml_file, output_file):
        # Validate vs XSD file
        validate_vs_xsd(input_xml_file, xsd_file, user_args.xsd_check, output_file)

        # Read XML
        root = read_xml_tree(input_xml_file)

        # Transform to dataframe
        df = read_xml_to_dataframe(root)

        # Transform to csv
        dataframe_to_csv(df, output_file)

        # Validate vs Custom Rules
        validate_custom_rules(root, renapo_gender_dict, renapo_state_dict, output_file)

        # Validate vs WS
        search_on_ws(ws_renapo_url, root, user_args.renapo_check, user_args.use_threads, output_file)
