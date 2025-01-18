""" String """
import re
import unicodedata


def clean_html(raw_html: str) -> str:
    """
    Function Clean Html
    :param raw_html:
    :return: str
    """
    if isinstance(raw_html, str) and len(raw_html) > 0:
        remove_tag = re.compile(r'<[^>]+>|[\'\"]')
        string = remove_tag.sub('', raw_html)

        string = (
            unicodedata.normalize("NFKD", string)
            .encode("ascii", "ignore")
            .decode("utf-8")
            .strip()
        )
        return string.upper()
    return raw_html


def clean_ean(string: str) -> int:
    """
    Function Clean EAN
    :param string:
    :return: int
    """
    if string is None or not (string and string.strip()):
        return 0
    ean = re.sub('[^0-9]+', '', str(string))
    return int(ean) if ean.isnumeric() else 0


def format_zip_code(string: str) -> str:
    """
    Function Format Zip Code
    :param string:
    :return: str
    """
    return '{}-{}'.format(string[0:5], string[5:8]) if len(string) == 8 else string


def slug(string: str) -> str:
    """
    Function Slug
    :param string:
    :return: str
    """
    s = string.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s


def check_subdomain(domain: str) -> str:
    """
    Function Check Subdomain
    :param domain:
    :return: str
    """
    validate_http = domain.replace(
        'https://', ''
    ).replace('http://', '')
    validate_domain = validate_http.split('.')

    origin = f'https://{validate_http}' \
        if len(validate_domain) > 3 or len(validate_domain) in range(1, 2) \
        else f'https://www.{validate_http}'
    return origin
