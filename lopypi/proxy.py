import os
import mimetypes
import tempfile

import requests

from flask import Blueprint, Flask, current_app, url_for
from flask import render_template, send_file, abort, Response

from lopypi.store import PackageStore
from lopypi.pypi import PyPI


views = Blueprint('proxy', __name__, template_folder="templates")


@views.route("/simple/", methods=['GET'])
def list_packages():
    """
    """
    pypi = current_app.config['pypi']

    packages = list(pypi.list_packages())
    for package in packages:
        package['uri'] = url_for('proxy.list_files', package=package['name'])
    return render_template("package_list.html", packages=packages)


@views.route("/simple/<package>/", methods=['GET'])
def list_files(package):
    """
    """
    pypi = current_app.config['pypi']

    files = list(pypi.list_files(package))
    for f in files:
        f['uri'] = url_for('proxy.get_file',
                           package=package,
                           filename=f['filename'])

    return render_template("file_list.html",
                           package=package,
                           files=files)


@views.route("/packages/<package>/<filename>", methods=["GET"])
def get_file(package, filename):
    """
    """
    pypi = current_app.config['pypi']
    store = current_app.config['cached_file_store']

    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None and filename.endswith(".egg"):
        content_type = "application/zip"

    f = store.get_file(package, filename)
    if f:
        # file is already cached locally.  Send it
        return send_file(f, mimetype=content_type)

    ## request file from pypi and stream it to client and disk
    # get url of remote file
    files = pypi.list_files(package)
    file_info = filter(lambda f: f['filename'] == filename, files)
    if not len(file_info):
        abort(404)
    file_info = file_info[0]
    uri = file_info['remote_uri']

    # start download
    download = requests.get(uri, stream=True)
    if download.status_code != 200:
        # TODO
        download.close()
        abort(download.status_code)

    def generate():
        # TODO this is fucking ugly
        data_iter = download.iter_content(1024)
        outfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            for data in data_iter:
                outfile.write(data)
                yield data
        finally:
            for data in data_iter:
                outfile.write(data)
            outfile.seek(0)

            # TODO verify checksum
            store.add_file(package, filename, outfile)

    response = Response(generate(), mimetype=content_type)
    if 'content-length' in download.headers:
        response.content_length = download.headers['content-length']

    return response


def create_app(package_dir, pypi_url):
    app = Flask(__name__)
    if not os.path.isdir(package_dir):
        os.makedirs(package_dir)
    app.config['cached_file_store'] = PackageStore(package_dir)
    app.config['pypi'] = PyPI(pypi_url)
    app.register_blueprint(views)
    return app
