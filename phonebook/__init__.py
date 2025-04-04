from json import load as json_load
from os import environ
from os.path import abspath, dirname, join

import mariadb
from flask import Flask, jsonify, render_template, request

app = Flask("phonebook")


def _omm_pp_list():
    with open(join(abspath(dirname(dirname(__file__))), "omm_pp.json")) as f:
        return json_load(f)


def _freepbx_phonebook():
    db = mariadb.connect(
        user=environ["FREEPBX_DB_USER"],
        password=environ["FREEPBX_DB_PASS"],
        host=environ["FREEPBX_DB_HOST"],
        port=3306,
        database="asterisk",
    )

    result = {}

    # get actual extensions
    with db.cursor() as cur:
        cur.execute("SELECT extension, name FROM users;")
        for ext, name in cur:
            result[str(ext)] = name

    # get group calls (aka "ring groups")
    with db.cursor() as cur:
        cur.execute("SELECT grpnum, description FROM ringgroups;")
        for ext, name in cur:
            result[str(ext)] = name

    return result


@app.route("/")
def phonebook_html():
    return render_template(
        "phonebook.html",
        force_display_all=bool("all" in request.args),
        fpbx=_freepbx_phonebook(),
        omm=_omm_pp_list(),
    )


@app.route("/phonebook.xml")
def phonebook_xml():
    return render_template(
        "phonebook.xml",
        fpbx=_freepbx_phonebook(),
        omm=_omm_pp_list(),
    )


@app.route("/freepbx.json")
def phonebook_freepbx():
    return jsonify(_freepbx_phonebook())


@app.route("/omm.json")
def phonebook_omm():
    return jsonify(_omm_pp_list())
