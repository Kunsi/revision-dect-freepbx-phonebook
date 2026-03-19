#!/usr/bin/env python3

from json import dump
from os import environ
from os.path import abspath, dirname, join
from shutil import move

import mariadb

PATH = abspath(dirname(__file__))


def fetch_freepbx():
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


if __name__ == "__main__":
    status = fetch_freepbx()
    with open(join(PATH, "freepbx.json.tmp"), "w") as f:
        dump(status, f)
    move(
        join(PATH, "freepbx.json.tmp"),
        join(PATH, "freepbx.json"),
    )
