import os

from flask import Flask, jsonify, request, send_from_directory


PARADROP_DATA_DIR = os.environ.get("PARADROP_DATA_DIR", "/tmp")
PORT = int(os.environ.get("PORT", 5000))

server = Flask(__name__, static_url_path="")


@server.route("/")
def get_index():
    return server.send_static_file("index.html")


@server.route("/output/<path:path>")
def send_output_file(path):
    return send_from_directory(PARADROP_DATA_DIR, path)


def run_server():
    server.run(host="0.0.0.0", port=PORT)
