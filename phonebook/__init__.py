from json import load as json_load
from os.path import abspath, dirname, join

from flask import Flask, jsonify, render_template, request

from .freepbx import FreePBXPhonebook

app = Flask("phonebook")

fpbx = FreePBXPhonebook()


def _omm_pp_list():
    with open(join(abspath(dirname(dirname(__file__))), "omm_pp.json")) as f:
        return json_load(f)


@app.route("/")
def phonebook_html():
    return render_template(
        "phonebook.html",
        force_display_all=bool("all" in request.args),
        fpbx=fpbx.phonebook(),
        omm=_omm_pp_list(),
    )


@app.route("/freepbx.json")
def phonebook_freepbx():
    return jsonify(fpbx.phonebook())


@app.route("/omm.json")
def phonebook_omm():
    return jsonify(_omm_pp_list())
