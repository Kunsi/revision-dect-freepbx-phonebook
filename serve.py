#!/usr/bin/env python3

from os import environ
from os.path import abspath, dirname, join

ROOT = dirname(abspath(__file__))

environ.setdefault("FREEPBX_DB_HOST", "10.1.3.3")
environ.setdefault("FREEPBX_DB_USER", "phonebook")

from phonebook import app

app.run(
    debug=True,
    host="0.0.0.0",
    threaded=True,
    port=8000,
)
