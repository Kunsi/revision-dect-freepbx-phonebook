from json import load as json_load
from os.path import abspath, dirname, join
from xml.etree import ElementTree

import qrcode
import qrcode.image.svg
from flask import Flask, Response, abort, jsonify, render_template, request

app = Flask("phonebook")


def _phonebook_as_list(force_display_all=False):
    fpbx = freepbx_phonebook()
    omm = omm_pp_list()

    result = []

    for number, name in sorted(fpbx.items()):
        should_be_shown = force_display_all
        is_active = True
        omm_info = omm.get(number, {})

        if not omm_info:
            should_be_shown = True

        if omm_info.get("is_subscribed", True):
            should_be_shown = True

        if omm_info.get("is_active", True) is False:
            is_active = False

        result.append(
            {
                "number": number,
                "name": name,
                "is_active": is_active,
                "should_be_shown": should_be_shown,
            }
        )

    return result


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

    image = qrcode.make(request.args["url"], image_factory=qrcode.image.svg.SvgImage)
    svg_data = ElementTree.tostring(image.get_image()).decode()
    return Response(svg_data, content_type="image/svg+xml")


@app.route("/")
def phonebook_html():
    force_display_all = bool("all" in request.args) or request.args.get("qr")
    phonebook = _phonebook_as_list(force_display_all=force_display_all)

    has_hidden_numbers = not all([i["should_be_shown"] for i in phonebook])

    return render_template(
        "phonebook.html",
        phonebook=phonebook,
        has_hidden_numbers=has_hidden_numbers,
        qr=request.args.get("qr"),
    )


@app.route("/phonebook.xml")
def phonebook_xml():
    return render_template(
        "phonebook.xml",
        phonebook=_phonebook_as_list(force_display_all=True),
    )


@app.route("/freepbx.json")
def phonebook_freepbx():
    return jsonify(freepbx_phonebook())


@app.route("/omm.json")
def phonebook_omm():
    return jsonify(omm_pp_list())
