#!/usr/bin/env python
"""Simple server for Nullboard"""

from json import loads  # Necessary to get the revision number
from os import makedirs
from os.path import isdir
from os.path import join as pathjoin
from flask import Flask
from flask import Response
from flask import request
from flask.logging import create_logger


BACKUP_PATH = "./nbbkp"  # Default path for backup files
ENC = 'UTF-8'  # Default encoding for backup files
BIND_ADDR = '127.0.0.1'
BIND_PORT = 5000
APP = Flask(__name__)
APP.logger = create_logger(APP)


@APP.route("/config", methods=['OPTIONS'])
def options_config():
  """Route for OPTIONS /config"""
  resp = Response("")
  resp.headers['allow'] = "PUT"
  resp.headers["Access-Control-Allow-Origin"] = "*"
  resp.headers["Access-Control-Allow-Headers"] = "X-Access-Token"
  resp.headers["Access-Control-Allow-Methods"] = "PUT"
  return resp


@APP.route("/config", methods=['PUT'])
def put_config():
  """Route for PUT /config"""
  resp = Response("true")
  resp.headers["Access-Control-Allow-Origin"] = "*"

  if not isdir(BACKUP_PATH):
    makedirs(BACKUP_PATH)

  file_path = pathjoin(BACKUP_PATH, 'app-config.json')
  if 'conf' in request.form:
    with open(file_path, 'w', encoding=ENC) as fhdlr:
      fhdlr.write(request.form['conf'])
    APP.logger.info("Wrote conf to %s", file_path)
  return resp


@APP.route("/board/<int:bid>", methods=['OPTIONS'])
def options_board(*_, **__):
  """Route for OPTIONS /board/<board_id>"""
  resp = Response("")
  resp.headers['allow'] = "PUT, DELETE"
  resp.headers["Access-Control-Allow-Origin"] = "*"
  resp.headers["Access-Control-Allow-Headers"] = "X-Access-Token"
  resp.headers["Access-Control-Allow-Methods"] = "PUT, DELETE"
  return resp


@APP.route("/board/<int:bid>", methods=['PUT'])
def put_board(bid):
  """Route for PUT /board/<board_id>"""
  resp = Response("true")
  resp.headers["Access-Control-Allow-Origin"] = "*"

  work_path = pathjoin(BACKUP_PATH, str(bid))
  if not isdir(work_path):
    makedirs(work_path)

  try:
    revnr = int(loads(request.form['data'])['revision'])
  except (KeyError, ValueError):
    APP.logger.info("Incorrectly formatted request data.")
    return "Incorrectly formatted request data.", 400

  file_paths = {'data': pathjoin(work_path, f"rev-{revnr:08d}.nbx"),
                'meta': pathjoin(work_path, 'meta.json')}
  for key, file_path in file_paths.items():
    if key in request.form:
      with open(file_path, 'w', encoding=ENC) as fhdlr:
        fhdlr.write(request.form[key])
      APP.logger.info("Wrote board %s to %s", key, file_path)
  return resp


@APP.route("/board/<int:bid>", methods=['DELETE'])
def delete_board(bid):
  """Route for DELETE /board/<board_id>"""
  resp = Response("true")
  resp.headers["Access-Control-Allow-Origin"] = "*"

  work_path = pathjoin(BACKUP_PATH, str(bid))
  if not isdir(work_path):
    makedirs(work_path)

  file_path = pathjoin(work_path, 'board-deleted')
  with open(file_path, 'w', encoding=ENC) as fhdlr:
    fhdlr.write("true")
  APP.logger.info("Deleted board %d", bid)
  return resp


def main():
  """Main function"""
  if not isdir(BACKUP_PATH):
    makedirs(BACKUP_PATH)
  APP.run(BIND_ADDR, BIND_PORT)


if __name__ == "__main__":
  main()
