from os import environ

from flask import Flask, jsonify, render_template, request

from .freepbx import freepbx_phonebook
from .omm import omm_pp_list

app = Flask("phonebook")


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
