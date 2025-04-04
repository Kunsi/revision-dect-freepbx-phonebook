from os import environ

import mariadb


class FreePBXPhonebook:
    def __init__(self):
        self.db = mariadb.connect(
            user=environ["FREEPBX_DB_USER"],
            password=environ["FREEPBX_DB_PASS"],
            host=environ["FREEPBX_DB_HOST"],
            port=3306,
            database="asterisk",
        )

    def phonebook(self):
        result = {}

        # get actual extensions
        with self.db.cursor() as cur:
            cur.execute("SELECT extension, name FROM users;")
            for ext, name in cur:
                result[str(ext)] = name

        # get group calls (aka "ring groups")
        with self.db.cursor() as cur:
            cur.execute("SELECT grpnum, description FROM ringgroups;")
            for ext, name in cur:
                result[str(ext)] = name

        return result
