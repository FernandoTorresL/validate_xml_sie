# XML-SIE files Validator (validate_xml_sie)
<a href="https://github.com/FernandoTorresL/validate_xml_sie/commits/main" target="_blank">![GitHub last commit](https://img.shields.io/github/last-commit/FernandoTorresL/validate_xml_sie)</a>

<a href="https://github.com/FernandoTorresL/validate_xml_sie" target="_blank">![GitHub repo size](https://img.shields.io/github/repo-size/FernandoTorresL/validate_xml_sie)</a>
## Project for IMSS, México. (Projecto personal para IMSS, México)

Validate XML files structure and data for use with SIE (IMSS) system.


## Introduction

This project is a project that will be operated by workers of the _Coordinación de Afiliación - División de Soporte a los Procesos de Afiliación_, an office on Instituto Mexicano del Seguro Social (IMSS, DIR, CA, DSPA)

This project must read a XML file, validate structure, validate data vs catalogs, and with the use of Web Service from RENAPO, validate data from a valid CURP's data.
With this project, users can validate and verify that the XML files are well formed and had valid data before send it to system SIE.

Before this project was implemented, this office only use a checklist and a specific Manual to build an XML file using the rules and values described there. This result on bad XML files or incorrect data that develop on several errors that SIE system raises. Now, using this project, we can save a lot of time and effort looking for wrong data, tag missing and so on.

### Technology used

This project was build with the use of: 

- Python v?.??

## Installation

Create a Python virtual environment

OS X & Linux:

```sh
$ python -m venv ./venv
$ source ./venv/bin/activate
$ pip install --upgrade pip
$ pip3 install -r requirements.txt
(venv) $
```

Windows:

```sh
$ python -m venv venv
$ .\venv\Scripts\activate
$ pip3 install -r requirements.txt
(venv) $

```
> This prompt may vary if you use another shell configuration, like pk10

Later, to deactivate the virtual environment
OS X & Linux & Windows:

```sh
(venv) $ deactivate
$
```

## Run the project

```sh
python validate_xml_sie.py
```

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
