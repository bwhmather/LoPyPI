import os
import mimetypes

from flask import Blueprint, Flask, current_app, url_for
from flask import render_template, send_file, abort

from lopypi.store import PackageStore


views = Blueprint('local', __name__, template_folder="templates")


@views.route("/simple/", methods=['GET'])
def list_packages():
    """
    """
    store = current_app.config['local_file_store']

    packages = (dict(name=name,
                     uri=url_for('local.list_files', package=name))
                for name in store.list_packages())
    return render_template("package_list.html", packages=packages)


@views.route("/simple/<package>/", methods=['GET'])
def list_files(package):
    """
    """
    store = current_app.config['local_file_store']

    files = list(store.list_files(package))
    map(lambda f: f.update({'uri': url_for('local.get_file',
                                           package=package,
                                           filename=f['filename'])}),
        files)

    return render_template("file_list.html",
                           package=package,
                           files=files)


@views.route("/packages/<package>/<filename>", methods=['GET'])
def get_file(package, filename):
    """
    """
    store = current_app.config['local_file_store']

    f = store.get_file(package, filename)
    if not f:
        abort(404)

    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None and filename.endswith(".egg"):
        content_type = "application/zip"

    return send_file(f, mimetype=content_type)


def create_app(package_dir):
    app = Flask(__name__)
    if not os.path.isdir(package_dir):
        os.makedirs(package_dir)
    app.config['local_file_store'] = PackageStore(package_dir)
    app.register_blueprint(views)
    return app
