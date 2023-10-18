# XML-SIE files Validator (validate_xml_sie)
<a href="https://github.com/FernandoTorresL/validate_xml_sie/commits/main" target="_blank">![GitHub last commit](https://img.shields.io/github/last-commit/FernandoTorresL/validate_xml_sie)</a>

<a href="https://github.com/FernandoTorresL/validate_xml_sie" target="_blank">![GitHub repo size](https://img.shields.io/github/repo-size/FernandoTorresL/validate_xml_sie)</a>
## Project for IMSS, México. (Projecto personal para IMSS, México)

Validate XML files structure and data for use with SIE (IMSS) system.


## Introduction

This project is a project that will be operated by workers of the _Coordinación de Afiliación - División de Soporte a los Procesos de Afiliación_, an office on Instituto Mexicano del Seguro Social (IMSS, DIR, CA, DSPA).

This project must read a XML file, validate structure, validate data vs catalogs, and with the use of Web Service from RENAPO, validate data from a valid CURP's data.
With this project, users can validate and verify that the XML files are well formed and had valid data before send it to system SIE.

Before this project was implemented, this office only use a checklist and a specific Manual to build an XML file using the rules and values described there. This result on bad XML files or incorrect data that develop on several errors that SIE system raises. Now, using this project, we can save a lot of time and effort looking for wrong data, tag missing and so on.

### Technology used

This project was build with the use of: 

- Python v3.11.4

## Installation

Create a Python virtual environment

OS X & Linux:

```sh
$ cd validate_xml_sie
$ python -m venv ./venv
$ source ./venv/bin/activate
$ pip install --upgrade pip
$ pip3 install -r requirements.txt
(venv) $
```

Windows:
```sh
$ cd validate_xml_sie
$ python -m venv venv
$ .\venv\Scripts\activate
$ pip3 install -r requirements.txt
(venv) $
```

Windows 10 with Git bash terminal:
```sh
$ cd validate_xml_sie
$ python -m venv venv
$ source ./venv/Scripts/activate
$ pip3 install -r requirements.txt
(venv) $
```

Windows 10 with powershell terminal:
```sh
PS> cd validate_xml_sie
PS> python -m venv venv
PS> .\.venv\Scripts\Activate.ps1
PS> pip3 install -r requirements.txt
(.venv) PS>
```

Windows 10 with WSL shell:
```sh
user@pc_name: cd validate_xml_sie
user@pc_name: python3 -m venv venv
user@pc_name: source venv/bin/activate
user@pc_name: pip install --upgrade pip
user@pc_name: pip3 install -r requirements.txt
(venv) user@pc_name:
```

> This prompt may vary if you use another shell configuration, like pk10 or git bash

Later, to deactivate the virtual environment
OS X & Linux & Windows:

```sh
(venv) $ deactivate
$
```

## View help and arguments

```sh
python3 validate_xml_sie.py --help
```

```sh
usage: validate_xml_sie.py [-h] [-x] [-r] [-u] xml_file [xml_file ...]

validate xml file and xml tags vs a Web Service data

positional arguments:
  xml_file            enter the xml filename

options:
  -h, --help          show this help message and exit
  -x, --xsd_check     check xml file vs xsd definition file
  -r, --renapo_check  check xml data vs WS RENAPO
  -u, --use_threads   use threads
``````
> If using another Python version try: python validate_xml_sie.py --help

## Run the project

Before run this project, edit or copy the following files:

* archivo_xsd/<xsd_filename>.xsd
* secrets.ini (Edit here variable xsd_file with <xsd_filename>.xsd)

* archivo_wsdl/<wsdl_filename>.wsdl
* secrets.ini (Edit here variable wsdl_filename with <wsdl_filename>.wsdl)

* secrets.ini (Edit here variable ws_url with the Web Service URL)

Then, you can execute the program:

```sh
python validate_xml_sie.py <xml_filename.xml> -x -r -u
```

## Example

```sh
python validate_xml_sie.py Example.xml --xsd_check --renapo_check --use_threads
```

### Example output:

```sh
Parameters:(['Example.xml'], True, True, True)

	Parameter xml_file:	['Example.xml']
	Parameter xsd_check:	True
	Parameter renapo_check:	True
	Parameter use_thread:	True

	Input XML File:	Example.xml
	URL WS:	<WS URL>
	Local WSDL Filename:	archivo_wsdl/WSDL_file.wsdl
	XSD File:	xsd_file.xsd

	Report File:	./output_files/2023_09_13_132424_report.csv

# Validating XML VS XSD Definition file...
# ...parameter xsd_check=True. Initiate check vs XSD File
	# XML CORRECTO vs Definición XSD
Exporting XML file to dataframe
Exporting dataframe to CSV File
	Output CSV File generated: ./output_files/2023_09_13_132425_dataframe.csv
	# Validating Custom Rules (CURP values)
#Total Records: 5697|Total Errors: 2

# Search data on WS RENAPO...
# Check vs WS RENAPO. Check thread option...
Recuperando: 100%|█████████████████████████████████████████████████████████████████████████████| 5697/5697 [00:00<00:00, 47339.61Reg/s]
	# ...parameter use_threads=True. Will use threads
# Using 8 thread(s)
Consultando: 100%|████████████████████████████████████████████████████████████████████████████| 5697/5697 [07:15<00:00, 13.07queries/s]
```

### Output files

* ./output_files/<time_stamp>_dataframe.csv, CSV file with the data extracted from xml file
* ./output_files/<time_stamp>_report.csv, CSV file with errors description and details

## Contributing to this repo

1. Fork it (<https://github.com/FernandoTorresL/validate_xml_sie/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

---

<div align="center">
    <a href="https://fertorresmx.dev/">
      <img height="150em" src="https://raw.githubusercontent.com/FernandoTorresL/FernandoTorresL/main/media/FerTorres-dev1.png">
  </a>
</div>



#### Follow me 
[fertorresmx.dev](https://fertorresmx.dev/)

#### :globe_with_meridians: [Twitter](https://twitter.com/FerTorresMx), [Instagram](https://www.instagram.com/fertorresmx/): @fertorresmx
