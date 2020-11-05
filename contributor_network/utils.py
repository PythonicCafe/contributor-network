import csv
from urllib.request import urlopen

from lxml.html import document_fromstring


def repository_url_from_pypi(package):
    url = f"https://pypi.org/pypi/{package}"
    response = urlopen(url)
    html = response.read()
    tree = document_fromstring(html)
    # TODO: add other platforms like gitlab, bitbucket etc.
    urls = set(
        item
        for item in tree.xpath("//a[contains(@href, 'github.com')]/@href")
        if "/pypa/warehouse" not in item and "/pypa/.github" not in item
    )
    if not urls:
        return None
    elif len(urls) == 1:
        return list(urls)[0]
    else:
        for url in urls:
            if package.replace("-", "_") in url.replace("-", "_"):
                # Probably this one is correct
                # TODO: what if it has /issues?
                return url


def read_csv(filename):
    with open(filename) as fobj:
        reader = csv.DictReader(fobj)
        for row in reader:
            yield row


def transform(x, min_input, max_input, min_output, max_output):
    """Transform `x` from input range to output range"""
    if x < min_input or x > max_input:
        raise ValueError(f"Max allowed value: {max_input} (got: {x})")
    elif x == min_input:
        return min_output
    elif x == max_input:
        return max_output
    else:
        return (x - min_input) * (max_output - min_output) / (max_input - min_input) + min_output
