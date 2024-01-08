import typing

import requests
import ratelimit
import readability
import bs4
import html2text
import warnings
import re


def read_file(file_path):
    """
    Read the content of an HTML file into a string.

    Args:
        file_path (str): Path to the HTML file.

    Returns:
        str: Content of the HTML file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_html_text(html_str, strike_tags: typing.Optional[list] = ["s", "strike", "del", "table"],
                  html_partial=False, to_single_line=False, **kwargs):
    """
    Args:
        html_str: file path
        strike_tags: the tags of strike html tags, default ["s", "strike", "del", "table"]
        html_partial: return only the div of the document, don't wrap
                             in html and body tags. see readability.Document().summary

    Returns: flat string with no \s{2,}, no \n, \t etc include, but only \s

    """

    readability_cls = readability.Document(html_str, **kwargs)

    html_content = readability_cls.summary(html_partial)

    # Parse the HTML with BeautifulSoup
    soup = bs4.BeautifulSoup(html_content, 'html.parser')

    # Find and remove all strikethrough text
    if strike_tags:
        try:
            for strike_tag in soup(strike_tags):
                strike_tag.decompose()
        except:
            warnings.warn('decompose of bs4 runs in error, automatically passed', ResourceWarning)

    # Convert the modified HTML to text
    h = html2text.HTML2Text()
    h.ignore_links = True
    result_text = h.handle(str(soup))
    # remove all \s+ to ' '
    if to_single_line:
        result_text = re.sub(r'\s+', ' ', result_text, flags=re.IGNORECASE)

    return result_text


@ratelimit.rate_limited(calls=15, period=90)
def download_secedgar(url, save_path='./sample.html'):
    heads = {'Host': 'www.sec.gov', 'Connection': 'close',
             'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-Requested-With': 'XMLHttpRequest',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
             }

    response = requests.get(url, headers=heads)
    response.raise_for_status()

    with open(save_path, 'wb') as f:
        f.write(response.content)
