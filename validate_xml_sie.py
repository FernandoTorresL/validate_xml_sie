# validate_xml_sie.py
"""

Returns:

"""

import argparse
import datetime
import os
import queue
import re
import urllib
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser

import lxml.etree as ET
import pandas as pd
from suds.client import Client
from tqdm import tqdm

import style

RENAPO_GENDER_DICT = {"H": "1", "M": "2"}

RENAPO_STATE_DICT = {
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

SEXO_PATTERN = r"[12]"
LUG_NAC_PATTERN = r"(0[1-9]|[1-2][0-9]|3[0-2])|35"
DIA_PATTERN = r"(0[1-9]|1[0-9]|2[0-9]|3[0-1])"
MES_PATTERN = r"(0[1-9]|1[0-2])"
ANIO_PATTERN = r"([1][9][0-9][0-9])|([2][0][0-9][0-9])"
DESC_OCUP_PATTERN = r"(MEDIO SUPERIOR|SUPERIOR|POSGRADO|EDUCACION A DISTANCIA)"
CP_PATTERN = r"([0-9]{5})"
NOMBRE_PATTERN = r"[A-Z# ]+$"
CURP_PATTERN = (
    r"([A-Z]{4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[HM]"
    r"(AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)"
    r"[A-Z]{3}[0-9A-Z]\d)"
)


def read_user_cli_args():
    """Handles the CLI user interactions.

    Returns:
        argparse.Namespace: Populated namespace object
    """
    parser = argparse.ArgumentParser(
        description="validate xml file and xml tags vs a Web Service data"
    )

    parser.add_argument(
        "xml_file",
        nargs="+",
        type=str,
        help="enter the xml filename",
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


def _get_ws_url():
    config = ConfigParser()
    config.read("secrets.ini")
    return config["urls"]["ws_url"]


def _get_wsdl_filename():
    config = ConfigParser()
    config.read("secrets.ini")
    return config["files"]["wsdl_filename"]


def _get_xsd_file():
    config = ConfigParser()
    config.read("secrets.ini")
    return config["files"]["xsd_file"]


def create_report_file(
    xml_filename,
    xsd_filename,
    xsd_check,
    renapo_check,
    use_threads,
):
    """Create output report file.

    Returns:
        .csv filename with timestamp on output_files folder
    """
    lineas = []
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    output_filename = f"./output_files/{timestamp}_report.csv"

    comment = "# Input XML File:" + xml_filename
    lineas.append(comment)
    comment = "# XSD File:" + xsd_filename
    lineas.append(comment)
    comment = "# xsd_check:" + str(xsd_check)
    lineas.append(comment)
    comment = "# renapo_check:" + str(renapo_check)
    lineas.append(comment)
    comment = "# use_threads:" + str(use_threads)
    lineas.append(comment)

    with open(output_filename, mode="w+", newline="", encoding="utf-8") as f:
        for linea in lineas:
            f.write(linea + "\n")

    print(f"\n\tReport File:\t{output_filename}", end="\n\n")
    comment = "# Report File: " + output_filename
    save_on_report(output_filename, comment)

    return output_filename


def check_xml_input_file(input_xml, output_filename):
    """Check if xml file exists

    Returns:
        True or False
    """
    xml_file_path = os.path.join("./")
    file_exist = False

    for filename in os.listdir(xml_file_path):
        if filename.endswith(".xml") and filename == input_xml:
            file_exist = True

    if not file_exist:
        style.change_color(style.RED)
        linea_reporte = xml_file_path + "/"
        linea_reporte += input_xml + "|File not found."
        print(f"\t{linea_reporte}")

        save_on_report(output_filename, linea_reporte)

    return file_exist


def read_xml_tree(input_xml_filename):
    """

    Returns:

    """
    # Parse XML
    xml_file_path = os.path.join("./", input_xml_filename)

    tree = ET.parse(xml_file_path)
    root_xml = tree.getroot()

    return root_xml


def read_xml_to_dataframe(root_xml):
    """

    Returns:

    """
    style.change_color(style.WHITE)
    linea_reporte = "Exporting XML file to dataframe"
    print(linea_reporte)

    # Extract data
    data = []
    for elem in root_xml:
        row = {}
        for subelem in elem:
            row[subelem.tag] = subelem.text
        data.append(row)

    df_datos = pd.DataFrame(data)

    return df_datos


def dataframe_to_csv(df_info, output_filename):
    """

    Returns:

    """

    style.change_color(style.WHITE)
    linea_reporte = "Exporting dataframe to CSV File"
    print(linea_reporte)

    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    output_csv_file = f"./output_files/{timestamp}_dataframe.csv"

    df_info.to_csv(output_csv_file, encoding="utf-8")

    linea_reporte = "# Output CSV File generated: " + output_csv_file

    style.change_color(style.GREEN)
    print(f"\t{linea_reporte}")
    save_on_report(output_filename, linea_reporte)


def validate_vs_xsd(input_xml, xsd_filename, xsd_check, output_filename):
    """

    Returns:

    """

    # Validate XML against XSD
    style.change_color(style.WHITE)
    linea_reporte = "# Validating XML VS XSD Definition file..."
    print(linea_reporte)
    save_on_report(output_filename, linea_reporte)

    if not xsd_check:
        linea_reporte = "# ...xsd_check=False. Won't check vs XSD File"
        style.change_color(style.YELLOW)
        print(f"{linea_reporte}", end="\n")
        save_on_report(output_filename, linea_reporte)
        return

    try:
        style.change_color(style.WHITE)
        linea_reporte = "# ...xsd_check=True. Initiate check vs XSD File"
        print(f"{linea_reporte}", end="\n")
        save_on_report(output_filename, linea_reporte)

        xml_file_path = os.path.join("./", input_xml)
        xsd_file_path = os.path.join("./archivo_xsd/", xsd_filename)

        xmlschema = ET.XMLSchema(ET.parse(xsd_file_path))
        tree = ET.parse(xml_file_path)

        if xmlschema.validate(tree):
            style.change_color(style.GREEN)
            linea_reporte = "# XML CORRECTO vs Definición XSD"
        else:
            style.change_color(style.RED)
            linea_reporte = "# XML MAL FORMADO contra definición XSD"

        print(f"\t{linea_reporte}")
        save_on_report(output_filename, linea_reporte)

    except FileNotFoundError:
        style.change_color(style.RED)
        print("File not found.")
    except ET.ParseError:
        style.change_color(style.RED)
        print("Error parsing XML file.")
    except ValueError as ve:
        style.change_color(style.RED)
        print("Validation error:", ve)


def valida_curp(data):
    """

    Returns:

    """

    curp_ex = re.compile(CURP_PATTERN)
    return bool(curp_ex.fullmatch(data))


def valida_sexo(data):
    """

    Returns:

    """

    sexo_ex = re.compile(SEXO_PATTERN)
    return bool(sexo_ex.fullmatch(data))


def valida_lug_nac(data):
    """

    Returns:

    """

    lug_nac_ex = re.compile(LUG_NAC_PATTERN)
    return bool(lug_nac_ex.fullmatch(data))


def valida_dia(data):
    """

    Returns:

    """

    dia_ex = re.compile(DIA_PATTERN)
    return bool(dia_ex.fullmatch(data))


def valida_mes(data):
    """

    Returns:

    """

    mes_ex = re.compile(MES_PATTERN)
    return bool(mes_ex.fullmatch(data))


def valida_anio(data):
    """

    Returns:

    """

    anio_ex = re.compile(ANIO_PATTERN)
    return bool(anio_ex.fullmatch(data))


def valida_desc_ocupa(data):
    """

    Returns:

    """

    des_ocupa_ex = re.compile(DESC_OCUP_PATTERN)
    return bool(des_ocupa_ex.fullmatch(data))


def valida_cp(data):
    """

    Returns:

    """

    cp_ex = re.compile(CP_PATTERN)
    return bool(cp_ex.fullmatch(data))


def valida_nomb_ap(data):
    """

    Returns:

    """

    nombre_ex = re.compile(NOMBRE_PATTERN)
    return bool(nombre_ex.fullmatch(data))


def validate_custom_rules(root_data, output_filename):
    """

    Returns:

    """

    style.change_color(style.WHITE)
    linea_reporte = "# Validating Custom Rules (CURP values)"
    print(f"\t{linea_reporte}", end="\n")
    save_on_report(output_filename, linea_reporte)

    try:
        num_registros = 0
        num_incidencias = 0
        renapo_gender_dic = dict(RENAPO_GENDER_DICT)
        renapo_state_dic = dict(RENAPO_STATE_DICT)
        # Validate specific tag elements
        for registro in root_data.findall(".//EMPLEADO"):
            num_registros += 1
            lista_incidencias = []

            # Extract CURP value
            curp_element = registro.find("CURP").text

            if curp_element is None:
                num_incidencias += 1
                msg_error = "CURP element not found in XML on record # " + str(
                    num_registros
                )
                raise ValueError(msg_error)

            curp_value = curp_element

            # print("Buscando CURP: " + curp_value )
            if curp_value:
                # Extract CURP value
                tramite_xml = registro.find("TRAMITE").text
                nss_xml = registro.find("NSS").text
                dv_xml = registro.find("DIGITO_VERIFICADOR").text
                nombre_xml = registro.find("NOMBRE").text
                ap_paterno_xml = registro.find("APELLIDO_PATERNO").text
                ap_materno_xml = registro.find("APELLIDO_MATERNO").text
                sexo_xml = registro.find("SEXO").text
                lugar_nac_xml = registro.find("LUGAR_NACIMIENTO").text
                dia_nac_xml = registro.find("DIA_NACIMIENTO").text
                mes_nac_xml = registro.find("MES_NACIMIENTO").text
                anio_nac_xml = registro.find("ANIO_NACIMIENTO").text
                nomb_padre_xml = registro.find("NOMBRE_PADRE").text
                ap_pat_padre_xml = registro.find("APELLIDO_PATERNO_PADRE").text
                ap_mat_padre_xml = registro.find("APELLIDO_MATERNO_PADRE").text
                nomb_madre_xml = registro.find("NOMBRE_MADRE").text
                ap_pat_madre_xml = registro.find("APELLIDO_PATERNO_MADRE").text
                ap_mat_madre_xml = registro.find("APELLIDO_MATERNO_MADRE").text
                dia_ing_xml = registro.find("DIA_INGRESO").text
                mes_ing_xml = registro.find("MES_INGRESO").text
                anio_ing_xml = registro.find("ANIO_INGRESO").text
                sal_base_xml = registro.find("SALARIO_BASE").text
                jor_sem_xml = registro.find("JORNADA_SEMANA").text
                t_salario_xml = registro.find("TIPO_SALARIO").text
                ocupacion_xml = registro.find("OCUPACION").text
                desc_ocupa_xml = registro.find("DESCRIPCION_OCUPACION").text
                t_trabajo_xml = registro.find("TIPO_TRABAJO").text
                cp_xml = registro.find("CODIGO_POSTAL").text
                tramitado_xml = registro.find("TRAMITADO").text

                if tramite_xml != "0":
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <TRAMITE>: "
                        + str(tramite_xml)
                        + ", must be 0"
                    )
                    lista_incidencias.append(incidencia)

                if nss_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <NSS>: "
                        + str(nss_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                if dv_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <DIGITO_VERIFICADOR>: "
                        + str(dv_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                # nombre_xml = nombre_xml.replace("#", "Ñ")
                if nombre_xml is not None:
                    if not valida_nomb_ap(nombre_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <NOMBRE>: "
                            + str(nombre_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if ap_paterno_xml is not None:
                    if not valida_nomb_ap(ap_paterno_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <APELLIDO_PATERNO>: "
                            + str(ap_paterno_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)
                else:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <APELLIDO_PATERNO>: "
                        + str(ap_paterno_xml)
                        + ", it's not valid"
                    )
                    lista_incidencias.append(incidencia)

                if ap_materno_xml is not None:
                    if not valida_nomb_ap(ap_materno_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <APELLIDO_MATERNO>: "
                            + str(ap_materno_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if sexo_xml is not None:
                    if not valida_sexo(sexo_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <SEXO>: "
                            + str(sexo_xml)
                            + ", must be 1 or 2"
                        )
                        lista_incidencias.append(incidencia)

                if lugar_nac_xml is not None:
                    if not valida_lug_nac(lugar_nac_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <LUGAR_NACIMIENTO>: "
                            + str(lugar_nac_xml)
                            + ", must be 01-32, 35"
                        )
                        lista_incidencias.append(incidencia)

                if dia_nac_xml is not None:
                    if not valida_dia(dia_nac_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <DIA_NACIMIENTO>: "
                            + str(dia_nac_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if mes_nac_xml is not None:
                    if not valida_mes(mes_nac_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <MES_NACIMIENTO>: "
                            + str(mes_nac_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if anio_nac_xml is not None:
                    if not valida_anio(anio_nac_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <ANIO_NACIMIENTO>: "
                            + str(anio_nac_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                # Padres Data
                if nomb_padre_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <NOMBRE_PADRE>: "
                        + str(nomb_padre_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                if ap_pat_padre_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <APELLIDO_PATERNO_PADRE>: "
                        + str(ap_pat_padre_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                if ap_mat_padre_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <APELLIDO_MATERNO_PADRE>: "
                        + str(ap_mat_padre_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                if nomb_madre_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <NOMBRE_MADRE>: "
                        + str(nomb_madre_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                if ap_pat_madre_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <APELLIDO_PATERNO_MADRE>: "
                        + str(ap_pat_madre_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                if ap_mat_madre_xml is not None:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <APELLIDO_MATERNO_MADRE>: "
                        + str(ap_mat_madre_xml)
                        + ", must be NULL"
                    )
                    lista_incidencias.append(incidencia)

                # Datos de ingreso
                if dia_ing_xml is not None:
                    if not valida_dia(dia_ing_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <DIA_INGRESO>: "
                            + str(dia_ing_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if mes_ing_xml is not None:
                    if not valida_mes(mes_ing_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <MES_INGRESO>: "
                            + str(mes_ing_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if anio_ing_xml is not None:
                    if not valida_anio(anio_ing_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <ANIO_INGRESO>: "
                            + str(anio_ing_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if sal_base_xml != "0000.00":
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <SALARIO_BASE>: "
                        + str(sal_base_xml)
                        + ", must be 0000.00"
                    )
                    lista_incidencias.append(incidencia)

                if jor_sem_xml != "0":
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <JORNADA_SEMANA>: "
                        + str(jor_sem_xml)
                        + ", must be 0"
                    )
                    lista_incidencias.append(incidencia)

                if t_salario_xml != "1":
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <TIPO_SALARIO>: "
                        + str(t_salario_xml)
                        + ", must be 0"
                    )
                    lista_incidencias.append(incidencia)

                if ocupacion_xml != "ESTUDIANTE":
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <OCUPACION>: "
                        + str(ocupacion_xml)
                        + ", must be ESTUDIANTE"
                    )
                    lista_incidencias.append(incidencia)

                if desc_ocupa_xml is not None:
                    if not valida_desc_ocupa(desc_ocupa_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <DESCRIPCION_OCUPACION>: "
                            + str(desc_ocupa_xml)
                            + ", must be "
                            + "MEDIO SUPERIOR|"
                            + "SUPERIOR|"
                            + "POSGRADO|"
                            + "EDUCACION A DISTANCIA"
                        )
                        lista_incidencias.append(incidencia)

                if t_trabajo_xml != "2":
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <TIPO_TRABAJO>: "
                        + str(t_trabajo_xml)
                        + ", must be 2"
                    )
                    lista_incidencias.append(incidencia)

                if cp_xml is not None:
                    if not valida_cp(cp_xml):
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <CODIGO_POSTAL>: "
                            + str(cp_xml)
                            + ", it's not valid"
                        )
                        lista_incidencias.append(incidencia)

                if tramitado_xml != "0":
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <TRAMITADO>: "
                        + str(tramitado_xml)
                        + ", must be 0"
                    )
                    lista_incidencias.append(incidencia)

                # Validate CURP
                if valida_curp(curp_element):
                    lugar_nac_curp = str(curp_value[11:13])
                    if renapo_state_dic[lugar_nac_curp] != lugar_nac_xml:
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <LUGAR_NACIMIENTO>: "
                            + str(lugar_nac_xml)
                            + ", doesn't match value on xml tag <CURP>: "
                            + lugar_nac_curp
                        )
                        lista_incidencias.append(incidencia)

                    sexo_curp = str(curp_value[10:11])
                    if renapo_gender_dic[sexo_curp] != sexo_xml:
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <SEXO>: "
                            + str(sexo_xml)
                            + ", doesn't match value on xml tag <CURP>: "
                            + sexo_curp
                        )
                        lista_incidencias.append(incidencia)

                    dia_nac_curp = curp_value[8:10]
                    if dia_nac_curp != dia_nac_xml:
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <DIA_NACIMIENTO>: "
                            + str(dia_nac_xml)
                            + ", doesn't match value on xml tag <CURP>: "
                            + dia_nac_curp
                        )
                        lista_incidencias.append(incidencia)

                    mes_nac_curp = curp_value[6:8]
                    if mes_nac_curp != mes_nac_xml:
                        incidencia = (
                            curp_element
                            + "|Value on xml tag <MES_NACIMIENTO>: "
                            + str(mes_nac_xml)
                            + ", doesn't match value on xml tag <CURP>: "
                            + mes_nac_curp
                        )
                        lista_incidencias.append(incidencia)

                    if anio_nac_xml is not None and anio_nac_xml.isdigit():
                        anio_nac_curp = curp_value[4:6]
                        dif_homonimia = curp_value[16:17]

                        if dif_homonimia.isdigit() is True:
                            anio_nac_curp = 1900 + int(anio_nac_curp)
                        else:
                            anio_nac_curp = 2000 + int(anio_nac_curp)

                        if anio_nac_curp != int(anio_nac_xml):
                            incidencia = (
                                curp_element
                                + "|Value on xml tag <ANIO_NACIMIENTO>: "
                                + str(anio_nac_xml)
                                + ", doesn't match calculated value"
                                + " on xml tag <CURP>: "
                                + str(anio_nac_curp)
                            )
                            lista_incidencias.append(incidencia)
                else:
                    incidencia = (
                        curp_element
                        + "|Value on xml tag <CURP>: "
                        + str(curp_element)
                        + ", isn't a valid CURP pattern"
                    )
                    lista_incidencias.append(incidencia)

                for incidencia in lista_incidencias:
                    num_incidencias += 1
                    style.change_color(style.RED)
                    # print(incidencia)
                    save_on_report(output_filename, incidencia)

        style.change_color(style.WHITE)
        linea_reporte = (
            "#Total Records: "
            + str(num_registros)
            + "|Total Errors: "
            + str(num_incidencias)
        )
        print(f"{linea_reporte}", end="\n\n")
        save_on_report(output_filename, linea_reporte)

    except FileNotFoundError:
        print("XML file not found.")
    except ET.ParseError:
        print("Error parsing XML file.")
    except ValueError as ve:
        print("Validation error:", ve)


def create_queue(root_xml):
    """

    Returns:

    """

    data_queue = queue.Queue()
    total_curps = len(root_xml.findall(".//EMPLEADO"))
    progreso = tqdm(
        total=total_curps,
        desc="Recuperando",
        leave=True,
        unit="Reg",
    )

    for curp in root_xml.findall(".//EMPLEADO"):
        progreso.update()
        data_list = []
        curp_value = curp.find("CURP").text
        nombre_xml = curp.find("NOMBRE").text
        ap_paterno_xml = curp.find("APELLIDO_PATERNO").text
        ap_materno_xml = curp.find("APELLIDO_MATERNO").text
        sexo_xml = curp.find("SEXO").text
        lugar_nac_xml = curp.find("LUGAR_NACIMIENTO").text
        dia_nac_xml = curp.find("DIA_NACIMIENTO").text
        mes_nac_xml = curp.find("MES_NACIMIENTO").text
        anio_nac_xml = curp.find("ANIO_NACIMIENTO").text

        nombre_xml = nombre_xml.replace("#", "Ñ")
        ap_paterno_xml = ap_paterno_xml.replace("#", "Ñ")
        if ap_materno_xml:
            ap_materno_xml = ap_materno_xml.replace("#", "Ñ")

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


def search_on_ws(
    url_ws_renapo,
    wsdl_file,
    root_xml,
    renapo_check,
    use_threads,
    output_filename,
):
    """

    Returns:

    """

    # Use WS RENAPO?
    style.change_color(style.WHITE)
    linea_reporte = "# Search data on WS RENAPO..."
    print(linea_reporte)
    save_on_report(output_filename, linea_reporte)

    if not renapo_check:
        linea_reporte = "# ...parameter renapo_check=False. Won't check vs WS"
        style.change_color(style.YELLOW)
        print(f"\t{linea_reporte}", end="\n")
        save_on_report(output_filename, linea_reporte)
        return

    # Use threads?
    style.change_color(style.WHITE)
    linea_reporte = "# Check vs WS RENAPO. Check thread option..."
    print(f"{linea_reporte}", end="\n")
    save_on_report(output_filename, linea_reporte)

    # Get all the data from xml to search on WS and compare results
    data_list = create_queue(root_xml)
    style.change_color(style.WHITE)
    if use_threads:
        linea_reporte = "# ...parameter use_threads=True. Will use threads"
        print(f"\t{linea_reporte}", end="\n")
        save_on_report(output_filename, linea_reporte)

        create_threads(data_list, output_filename, url_ws_renapo)
    else:
        style.change_color(style.YELLOW)
        linea_reporte = "# ...parameter use_threads=False. Won't use threads"
        print(f"\t{linea_reporte}", end="\n")
        save_on_report(output_filename, linea_reporte)

        style.change_color(style.GREEN)

        with tqdm(
            total=data_list.qsize(),
            desc="Consultando",
            leave=True,
            unit="queries",
        ) as pbar:
            consulta_ws(
                data_list,
                pbar,
                output_filename,
                url_ws_renapo,
                wsdl_file,
            )


def create_threads(data_list_threads, output_filename, ws_url_renapo):
    """

    Returns:

    """

    threads = os.cpu_count()

    linea_reporte = "# Using " + str(threads) + " thread(s)"
    style.change_color(style.GREEN)
    print(f"{linea_reporte}", end="\n")
    save_on_report(output_filename, linea_reporte)

    with tqdm(
        total=data_list_threads.qsize(),
        desc="Consultando",
        leave=True,
        unit="queries",
    ) as pbar:
        with ThreadPoolExecutor(
            max_workers=threads, thread_name_prefix="WS_queries"
        ) as ex:
            futures = [
                ex.submit(
                    consulta_ws,
                    data_list_threads,
                    pbar,
                    output_file,
                    ws_url_renapo,
                    wsdl_filename,
                )
                for i in range(threads)
            ]


def consulta_ws(data_list, pbar, output_filename, ws_url_renapo, wsdl_file):
    """

    Returns:

    """

    while not data_list.empty():
        try:
            style.change_color(style.WHITE)
            # Update the progress bar
            pbar.update(1)
            # total_records = data_list.qsize()
            record_data = data_list.get_nowait()
            data_list.task_done()
            curp_value = record_data[0]
            nombre_xml = record_data[1]
            ap_paterno_xml = record_data[2]
            ap_materno_xml = record_data[3]
            sexo_xml = record_data[4]
            lugar_nac_xml = record_data[5]
            dia_nac_xml = record_data[6]
            mes_nac_xml = record_data[7]
            anio_nac_xml = record_data[8]

            style.change_color(style.GREEN)

            path_to_wsdl = urllib.parse.urljoin(
                "file:",
                urllib.request.pathname2url(
                    os.path.abspath(wsdl_file),
                ),
            )

            cliente = Client(path_to_wsdl)
            cliente.set_options(location=ws_url_renapo)
            response_ws = cliente.service.ConsultaDatosCURP(curp_value)

            # ... process the response_ws ...
            if response_ws.CodigoError == 0:
                nombre_xml = nombre_xml.replace("#", "Ñ")
                if nombre_xml != response_ws.Nombres:
                    incidencia = (
                        curp_value
                        + "|NOMBRE(S) in XML: "
                        + nombre_xml
                        + ", doesn't match RENAPO response: "
                        + response_ws.Nombres
                    )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)

                if ap_paterno_xml is not None:
                    ap_paterno_xml = ap_paterno_xml.replace("#", "Ñ")
                if ap_paterno_xml != response_ws.Apellido1:
                    incidencia = (
                        curp_value
                        + "|APELLIDO_PATERNO in XML: "
                        + ap_paterno_xml
                        + ", doesn't match RENAPO response: "
                        + response_ws.Apellido1
                    )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)

                if ap_materno_xml is not None:
                    ap_materno_xml = ap_materno_xml.replace("#", "Ñ")
                if ap_materno_xml != response_ws.Apellido2:
                    if response_ws.Apellido2 is None:
                        incidencia = (
                            curp_value
                            + "|APELLIDO_MATERNO in XML: "
                            + ap_materno_xml
                            + ", doesn't match RENAPO response: NULL"
                        )
                    else:
                        incidencia = (
                            curp_value
                            + "|APELLIDO_MATERNO in XML: NULL, "
                            + "doesn't match RENAPO response: "
                            + response_ws.Apellido2
                        )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)

                lugar_nac_curp = curp_value[11:13]
                if RENAPO_STATE_DICT[lugar_nac_curp] != lugar_nac_xml:
                    incidencia = (
                        curp_value
                        + "|Lugar de nacimiento: "
                        + lugar_nac_xml
                        + ", doesn't match RENAPO response: "
                        + lugar_nac_curp
                    )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)

                sexo_curp = curp_value[10:11]
                if RENAPO_GENDER_DICT[sexo_curp] != sexo_xml:
                    incidencia = (
                        curp_value
                        + "|Sexo: "
                        + sexo_xml
                        + ", doesn't match RENAPO response: "
                        + sexo_curp
                    )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)

                dia_nac_curp = curp_value[8:10]
                if dia_nac_curp != dia_nac_xml:
                    incidencia = (
                        curp_value
                        + "|Día Nacimiento: "
                        + dia_nac_xml
                        + ", doesn't match RENAPO response: "
                        + dia_nac_curp
                    )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)

                mes_nac_curp = curp_value[6:8]
                if mes_nac_curp != mes_nac_xml:
                    incidencia = (
                        curp_value
                        + "|Mes Nacimiento: "
                        + mes_nac_xml
                        + ", doesn't match RENAPO response: "
                        + mes_nac_curp
                    )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)

                anio_nac_curp = curp_value[4:6]
                dif_homonimia = curp_value[16:17]

                if dif_homonimia.isdigit():
                    anio_nac_curp = 1900 + int(anio_nac_curp)
                else:
                    anio_nac_curp = 2000 + int(anio_nac_curp)

                if anio_nac_curp != int(anio_nac_xml):
                    incidencia = (
                        curp_value
                        + "|Año Nacimiento XML: "
                        + str(anio_nac_xml)
                        + ", doesn't match RENAPO response: "
                        + str(anio_nac_curp)
                    )
                    record_data.append(incidencia)
                    save_on_report(output_filename, incidencia)
            else:
                incidencia = curp_value + "|No data from WS-RENAPO"
                record_data.append(incidencia)
                save_on_report(output_filename, incidencia)

        except Exception as mensaje:
            incidencia = curp_value + "|Error? (WS-RENAPO)" + mensaje
            style.change_color(style.RED)
            print(incidencia)
            record_data.append(incidencia)
            save_on_report(output_filename, incidencia)


def save_on_report(output_filename, linea):
    """

    Returns:

    """

    with open(output_filename, mode="a", newline="", encoding="utf-8") as f:
        f.write(linea + "\n")


if __name__ == "__main__":
    # Get user parameters
    read_user_cli_args()
    user_args = read_user_cli_args()

    style.change_color(style.BLUE)
    print(f"\tParameters:{user_args.xml_file}, ")
    print(f"{user_args.xsd_check}, ")
    print(f"{user_args.renapo_check}, ")
    print(f"{user_args.use_threads}, ", end="\n\n")

    print(f"\tParameter xml_file:\t{user_args.xml_file}", end="\n")
    print(f"\tParameter xsd_check:\t{user_args.xsd_check}", end="\n")
    print(f"\tParameter renapo_check:\t{user_args.renapo_check}", end="\n")
    print(f"\tParameter use_thread:\t{user_args.use_threads}", end="\n\n")

    # Testing getting a secret
    input_xml_file = user_args.xml_file[0]
    print(f"\tInput XML File:\t{input_xml_file}", end="\n")

    ws_url = _get_ws_url()
    print(f"\tURL WS:\t{ws_url}", end="\n")

    wsdl_filename = _get_wsdl_filename()
    print(f"\tLocal WSDL Filename:\t{wsdl_filename}", end="\n")

    xsd_file = _get_xsd_file()
    print(f"\tXSD File:\t{xsd_file}", end="\n")

    # Create output file and save params
    output_file = create_report_file(
        input_xml_file,
        xsd_file,
        user_args.xsd_check,
        user_args.renapo_check,
        user_args.use_threads,
    )

    # Check that XML File exist
    if check_xml_input_file(input_xml_file, output_file):
        # Validate vs XSD file
        validate_vs_xsd(
            input_xml_file,
            xsd_file,
            user_args.xsd_check,
            output_file,
        )

        # Read XML
        root = read_xml_tree(input_xml_file)

        # Transform to dataframe
        df = read_xml_to_dataframe(root)

        # Transform to csv
        dataframe_to_csv(df, output_file)

        # Validate vs Custom Rules
        validate_custom_rules(
            root,
            output_file,
        )

        # Validate vs WS
        search_on_ws(
            ws_url,
            wsdl_filename,
            root,
            user_args.renapo_check,
            user_args.use_threads,
            output_file,
        )
