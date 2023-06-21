#!/usr/bin/env python
"""Simple server for Nullboard"""

# TODO:
# - Handle request data if the mime type is correctly set to JSON

from json import loads  # Necessary to get the revision number
from os import getenv
from os import makedirs
from os.path import isdir
from os.path import isfile
from os.path import join as pathjoin
from re import match as re_match
from secrets import token_hex

from flask import Flask
from flask import Response
from flask import request
from flask.logging import create_logger
from dotenv import load_dotenv

load_dotenv()

BACKUP_PATH = getenv("NBBKP_PATH", "./nbbkp")  # Default path for backup files
ENC = getenv("NBBKP_ENC", "UTF-8")  # Default encoding for backup files
BIND_ADDR = getenv("NBBKP_BIND_ADDR", "127.0.0.1")
BIND_PORT = int(getenv("NBBKP_BIND_PORT", "5000"))
TOKEN_FILE = getenv("NBBKP_TOKEN_FILE", "tokens.db")
ADMIN_PWD = getenv("NBBKP_ADMIN_PWD", "YourVerySecurePassWd")  # For accessing the admin area.

APP = Flask(__name__)
APP.logger = create_logger(APP)


def format_flask_response(response, new_values, keep_status=False):
  """Formats a response with new values. Necessary to keep set headers"""
  if not isinstance(response, Response):
    raise TypeError(f"Expected Flask Response object, got {type(response)}.")
  if isinstance(new_values, tuple):
    data, code = new_values
  else:
    data, code = str(new_values), 200
  response.set_data(data)
  if not keep_status:
    response.status_code = code
  return response


def base36encodehex(hexnr):
  """From https://stackoverflow.com/a/1181924"""
  try:
    number = int(hexnr, 16)
  except ValueError:
    APP.logger.info("%s isn't a hexadecimal number", hexnr)

  alphabet, base36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", ''

  while number:
    number, i = divmod(number, 36)
    base36 = alphabet[i] + base36

  return base36 or alphabet[0]


def generate_token():
  """Generate a random 16 characters string, of mixed upper case and numbers,
     grouped in groups of 4, separated by dashes"""
  # 256^10 < 36^16 < 256^11
  token = base36encodehex(token_hex(11))[:16]
  token = token.zfill(16)
  # From https://stackoverflow.com/a/22571558
  return '-'.join(map(''.join, zip(*[iter(token)]*4)))


def search_token(token, file):
  """Search for lines starting with <token> in <file>"""
  with open(file, 'r', encoding=ENC) as fhdlr:
    while line := fhdlr.readline():
      if line.startswith(f"{token} "):
        return line
  return False


def search_user(user, file):
  """Search for lines starting with <token> in <file>"""
  with open(file, 'r', encoding=ENC) as fhdlr:
    while line := fhdlr.readline():
      if line.strip().endswith(f" {user}"):
        return line
  return False


def format_token(token):
  """Format a token according to a syntax"""
  if not re_match("^([0-9A-Z]{4}-){4}$", f"{token}-"):
    raise ValueError(f"Token '{token}' does not conform to token format")
  return token


def validate_token(token):
  """Simple check to verify if a token exists"""
  return bool(search_token(token, pathjoin(BACKUP_PATH, TOKEN_FILE)))


def new_token(data):
  """Writes a new token to the on-disk list and return it"""
  if "user" not in data:
    APP.logger.info("No 'user' parameter passed in request")
    return "No 'user' parameter passed in request", 400
  user = data["user"]
  if search_user(user, pathjoin(BACKUP_PATH, TOKEN_FILE)):
    APP.logger.info("User '%s' already exists", user)
    return f"User {user} already exists", 403
  token = generate_token()
  while search_token(token, pathjoin(BACKUP_PATH, TOKEN_FILE)):
    APP.logger.info("Token conflilct with '%s', regenerating", token)
    token = generate_token()
  with open(pathjoin(BACKUP_PATH, TOKEN_FILE), 'a', encoding=ENC) as fhdlr:
    APP.logger.info("Writing '%s %s' to %s", token, user,
                    pathjoin(BACKUP_PATH, TOKEN_FILE))
    fhdlr.write(f"{token} {user}\n")
  return token


def get_token(data):
  """Get a token from a user name"""
  if "user" not in data:
    APP.logger.info("No 'user' parameter passed in request")
    return "No 'user' parameter passed in request", 400
  user = data["user"]
  if found := search_user(user, pathjoin(BACKUP_PATH, TOKEN_FILE)):
    APP.logger.info("User '%s' found, returning token", user)
    return found.split(" ")[0]
  APP.logger.info("User '%s' not found, returning 404", user)
  return "Not Found", 404


def list_tokens(_):
  """List all tokens without names"""
  tokens = []
  APP.logger.info("Listing all tokens")
  with open(pathjoin(BACKUP_PATH, TOKEN_FILE), 'r', encoding=ENC) as fhdlr:
    while line := fhdlr.readline():
      tokens.append(line.split(" ")[0])
  return '\n'.join(tokens)


def del_token(data):
  """Delete a token if the name matches"""
  if "user" not in data or "token" not in data:
    APP.logger.info("No 'user' or 'token' parameter passed in request")
    return "No 'user' or 'token' parameter passed in request", 400
  user = data["user"]
  token = data["token"]
  line = search_token(token, pathjoin(BACKUP_PATH, TOKEN_FILE))
  if not line:
    APP.logger.info("Token '%s' not found, returning 404", token)
    return "Not Found", 404
  if line.strip() == f"{token} {user}":
    APP.logger.info("Matching record found for user '%s' and token '%s', "
                    "deleting", user, token)
    with open(pathjoin(BACKUP_PATH, TOKEN_FILE), "r+", encoding=ENC) as fhdlr:
      line_offeset = 0
      while line != fhdlr.readline():
        line_offeset = fhdlr.tell()
      rest = fhdlr.read()
      fhdlr.seek(line_offeset)
      fhdlr.write(rest)
      fhdlr.truncate()
    return ""
  APP.logger.info("No matching record found for user '%s' and token '%s', "
                  "returning 403", user, token)
  return f"No matching record found for user '{user}' and token '{token}'", 403


@APP.route("/admin/<string:cmd>", methods=["POST"])
def admin(cmd):
  """Route for POST /admin/<command>"""
  valid_commands = {"new-token": new_token,
                    "get-token": get_token,
                    "list-tokens": list_tokens,
                    "del-token": del_token}

  resp = Response("true")
  resp.headers["Access-Control-Allow-Origin"] = "*"

  if "login" not in request.form or "password" not in request.form:
    return format_flask_response(resp, ("Access Denied", 401))

  login = request.form["login"]
  password = request.form["password"]

  if login != "admin" or password != ADMIN_PWD:
    return format_flask_response(resp, ("Access Denied", 401))

  if cmd not in valid_commands:
    return format_flask_response(resp, ("Invalid command", 400))

  return format_flask_response(resp, valid_commands[cmd](request.form))


@APP.route("/config", methods=["OPTIONS"])
def options_config():
  """Route for OPTIONS /config"""
  resp = Response("")
  resp.headers["allow"] = "PUT"
  resp.headers["Access-Control-Allow-Origin"] = "*"
  resp.headers["Access-Control-Allow-Headers"] = "X-Access-Token"
  resp.headers["Access-Control-Allow-Methods"] = "PUT"
  return resp


@APP.route("/config", methods=["PUT"])
def put_config():
  """Route for PUT /config"""
  resp = Response("true")
  resp.headers["Access-Control-Allow-Origin"] = "*"

  access_token = format_token(request.headers["X-Access-Token"])
  if not validate_token(access_token):
    resp = format_flask_response(resp, ("Access Denied", 401))
  else:
    work_path = pathjoin(BACKUP_PATH, access_token)
    if not isdir(work_path):
      makedirs(work_path)

    file_path = pathjoin(work_path, "app-config.json")
    if "conf" in request.form:
      with open(file_path, 'w', encoding=ENC) as fhdlr:
        fhdlr.write(request.form["conf"])
      APP.logger.info("Wrote conf to %s", file_path)
  return resp


@APP.route("/board/<int:bid>", methods=["OPTIONS"])
def options_board(*_, **__):
  """Route for OPTIONS /board/<board_id>"""
  resp = Response("")
  resp.headers["allow"] = "PUT, DELETE"
  resp.headers["Access-Control-Allow-Origin"] = "*"
  resp.headers["Access-Control-Allow-Headers"] = "X-Access-Token"
  resp.headers["Access-Control-Allow-Methods"] = "PUT, DELETE"
  return resp


@APP.route("/board/<int:bid>", methods=["PUT"])
def put_board(bid):
  """Route for PUT /board/<board_id>"""
  resp = Response("true")
  resp.headers["Access-Control-Allow-Origin"] = "*"

  access_token = format_token(request.headers["X-Access-Token"])
  if not validate_token(access_token):
    resp = format_flask_response(resp, ("Access Denied", 401))
  else:
    work_path = pathjoin(BACKUP_PATH, access_token, str(bid))
    if not isdir(work_path):
      makedirs(work_path)

    try:
      revnr = int(loads(request.form["data"])["revision"])
    except (KeyError, ValueError):
      APP.logger.info("Incorrectly formatted request data.")
      return format_flask_response(resp, ("Incorrectly formatted request data",
                                          400))

    file_paths = {"data": pathjoin(work_path, f"rev-{revnr:08d}.nbx"),
                  "meta": pathjoin(work_path, "meta.json")}
    for key, file_path in file_paths.items():
      if key in request.form:
        with open(file_path, 'w', encoding=ENC) as fhdlr:
          fhdlr.write(request.form[key])
        APP.logger.info("Wrote board %s to %s", key, file_path)
  return resp


@APP.route("/board/<int:bid>", methods=["DELETE"])
def delete_board(bid):
  """Route for DELETE /board/<board_id>"""
  resp = Response("true")
  resp.headers["Access-Control-Allow-Origin"] = "*"

  access_token = format_token(request.headers["X-Access-Token"])
  if not validate_token(access_token):
    resp = format_flask_response(resp, ("Access Denied", 401))
  else:
    work_path = pathjoin(BACKUP_PATH, access_token, str(bid))
    if not isdir(work_path):
      makedirs(work_path)

    file_path = pathjoin(work_path, "board-deleted")
    with open(file_path, 'w', encoding=ENC) as fhdlr:
      fhdlr.write("true")
    APP.logger.info("Deleted board %d", bid)
  return resp


def main():
  """Main function"""
  if not isdir(BACKUP_PATH):
    makedirs(BACKUP_PATH)
  if not isfile(pathjoin(BACKUP_PATH, TOKEN_FILE)):
    with open(pathjoin(BACKUP_PATH, TOKEN_FILE), 'a', encoding=ENC):
      pass
  APP.run(BIND_ADDR, BIND_PORT)


if __name__ == "__main__":
  main()
