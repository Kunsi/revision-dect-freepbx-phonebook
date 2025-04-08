from os import environ

import mariadb


def freepbx_phonebook():
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
