from json import load as json_load
from os.path import abspath, dirname, join
from xml.etree import ElementTree


import qrcode
import qrcode.image.svg
from flask import Flask, jsonify, render_template, request, Response

app = Flask("phonebook")


def omm_pp_list():
    with open(join(abspath(dirname(dirname(__file__))), "omm_pp.json")) as f:
        return json_load(f)


def freepbx_phonebook():
    with open(join(abspath(dirname(dirname(__file__))), "freepbx.json")) as f:
        return json_load(f)


@app.route("/qrcode")
def make_qrcode():
    if not request.args.get("url"):
        abort(404)

    image = qrcode.make(request.args['url'], image_factory=qrcode.image.svg.SvgImage)
    svg_data = ElementTree.tostring(image.get_image()).decode()
    return Response(svg_data, content_type="image/svg+xml")


@app.route("/")
def phonebook_html():
    return render_template(
        "phonebook.html",
        force_display_all=bool("all" in request.args),
        fpbx=freepbx_phonebook(),
        omm=omm_pp_list(),
        qr=request.args.get("qr"),
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
