# validate_xml_sie.py

from configparser import ConfigParser


def _get_ws_renapo_url():
    """Fetch the WS-URL from your configuration file.

    Expects a configuration file named "secrets.ini" with structure:

        [urls]
        ws_url_renapo=<YOUR-WS_RENAPO-URL>
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["urls"]["ws_url_renapo"]

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

    # Testing getting a secret
    print(_get_ws_renapo_url())

    # Testing another secret
    config = ConfigParser()
    config.read("secrets.ini")
    print(config["files"]["input_file"])
