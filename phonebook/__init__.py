from json import load as json_load
from os import environ
from os.path import abspath, dirname, join

from flask import Flask, jsonify, render_template, request

app = Flask("phonebook")


def omm_pp_list():
    with open(join(abspath(dirname(dirname(__file__))), "omm_pp.json")) as f:
        return json_load(f)


def freepbx_phonebook():
    with open(join(abspath(dirname(dirname(__file__))), "freepbx.json")) as f:
        return json_load(f)


@app.route("/")
def phonebook_html():
    return render_template(
        "phonebook.html",
        force_display_all=bool("all" in request.args),
        fpbx=freepbx_phonebook(),
        omm=omm_pp_list(),
    )


@app.route("/phonebook.xml")
def phonebook_xml():
    return render_template(
        "phonebook.xml",
        fpbx=freepbx_phonebook(),
        omm=omm_pp_list(),
    )


@app.route("/freepbx.json")
def phonebook_freepbx():
    return jsonify(freepbx_phonebook())


@app.route("/omm.json")
def phonebook_omm():
    return jsonify(omm_pp_list())
