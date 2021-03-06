import re
from urlparse import urlsplit

from bs4 import BeautifulSoup
import requests
from urlparse import urldefrag, urljoin


class PyPI(object):
    def __init__(self, index="http://pypi.python.org/simple"):
        self._index = index

    def list_packages(self):
        resp = requests.get(self._index)

        soup = BeautifulSoup(resp.content)

        for link in soup.find_all("a"):
            yield link.text

    def list_files(self, package, ):
        package_uri = "%s/%s/" % (self._index, package)
        resp = requests.get(package_uri)

        soup = BeautifulSoup(resp.content)

        for link in soup.find_all("a"):
            if 'rel' in link.attrs:
                rel = link.attrs.get('rel')[0]
            else:
                rel = None

            filename = link.text

            file_uri, frag = urldefrag(link.attrs['href'])
            file_uri = urljoin(package_uri, file_uri)

            mo = re.match(r"^md5=([a-fA-F0-9]{32})$", frag)
            md5 = mo.group(1) if mo else None

            yield dict(filename=filename,
                       remote_uri=file_uri,
                       rel=rel,
                       md5=md5)
