import os

from flask import Blueprint, Flask, current_app, url_for
from flask import render_template, send_file, abort

from lopypi.store import PackageStore
from lopypi.pypi import PyPI

import mimetypes


views = Blueprint('proxy', __name__, template_folder="templates")


@views.route("/simple/", methods=['GET'])
def list_packages():
    """
    """
    pypi = current_app.config['pypi']

    packages = (dict(name=name,
                     uri=url_for('proxy.list_files', package=name))
                for name in pypi.list_packages())
    return render_template("package_list.html", packages=packages)


@views.route("/simple/<package>/", methods=['GET'])
def list_files(package):
    """
    """
    pypi = current_app.config['pypi']
    store = current_app.config['cached_file_store']

    files = list(pypi.list_files(package))
    map(lambda f: f.update({'uri': url_for('proxy.get_file',
                                           package=package,
                                           filename=f['filename'])}),
        files)
    return render_template("file_list.html",
                           package=package,
                           files=files)


@views.route("/packages/<package>/<filename>", methods=["GET"])
def get_file(package, filename):
    """
    """
    pypi = current_app.config['pypi']
    store = current_app.config['cached_file_store']

    f = store.get_file(package, filename)

    if not f:
        uri = pypi.get_file_uri(package, filename)
        if not uri:
            abort(404)
        # TODO should be async
        # TODO fix simultaneous downloads of same packae
        # TODO give option of redirecting instead of saving
        with urllib2.urlopen(uri) as download:
            store.add_file(package, filename, download)

        f = store.get_file(package, filename)

    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None and filename.endswith(".egg"):
        content_type = "application/zip"

    return send_file(f, mimetype=content_type)


def create_app(package_dir, pypi_url):
    app = Flask(__name__)
    if not os.path.isdir(package_dir):
        os.mkdirs(package_dir)
    app.config['cached_file_store'] = PackageStore(package_dir)
    app.config['pypi'] = PyPI(pypi_url)
    app.register_blueprint(views)
    return app
