import os
import shutil

from flask import safe_join


class PackageStore(object):
    def __init__(self, directory):
        self.directory = os.path.abspath(directory)

    def list_packages(self):
        return os.listdir(self.directory)

    def list_files(self, package):
        package_path = self._get_package_path(package)
        if not os.path.isdir(package_path):
            return

        for f in os.listdir(self._get_package_path(package)):
            yield dict(filename=f)

    def get_file(self, package, filename):
        """
        :returns: an open read-only file handle or ``None``
        """
        filepath = self._get_filepath(package, filename)
        if not os.path.isfile(filepath):
            return None

        return open(filepath, "rb")

    def add_file(self, package, filename, content):
        """
        :param content: either a python file object or string
        """
        path = self._get_file_path(package, filename)

        prefix = os.path.dirname(path)
        if not os.path.isdir(prefix):
            os.makedirs(prefix)

        with open(path, 'wb') as output:
            if hasattr(content, 'read'):
                content = shutil.copyfileobj(content, output)
            else:
                output.write(content)

    def _get_package_path(self, package):
        # TODO don't allow package name to contain path seperators
        return safe_join(self.directory, package)

    def _get_filepath(self, package, filename):
        """
        :returns: the path at which the file should be saved (even if it does
                  not exists)
        """
        # TODO don't allow path seperators in package or file name
        return safe_join(self._get_package_path(package), filename)
