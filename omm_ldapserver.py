#!/usr/bin/env python3

import logging
import socketserver

import ldapserver
from ldapserver.exceptions import (
    LDAPUnavailable,
)
from ldapserver.schema import RFC2307BIS_SCHEMA, RFC2798_SCHEMA

from phonebook.freepbx import freepbx_phonebook
from phonebook.omm import omm_pp_list

logging.basicConfig(level=logging.INFO)

BASE_DN = "dc=revision"


class UffdLDAPRequestHandler(ldapserver.LDAPRequestHandler):
    dn_base = BASE_DN
    supports_sasl_plain = True

    # just always accept usernames and passwords, yolo!
    def do_bind_simple_authenticated(self, dn, password):
        return True

    def do_bind_sasl_plain(self, identity, password, authzid=None):
        return True

    def do_search(self, baseobj, scope, filterobj):
        yield from super().do_search(baseobj, scope, filterobj)
        yield from self.do_search_static()
        yield from self.do_search_users(baseobj, scope, filterobj)

    def do_search_static(self):
        base_attrs = {
            "objectClass": ["top", "dcObject", "organization"],
            "structuralObjectClass": ["organization"],
        }
        for rdnassertion in self.dn_base[0]:
            base_attrs[rdnassertion.attribute] = [rdnassertion.value]
        yield self.subschema.ObjectEntry(self.dn_base, **base_attrs)
        yield self.subschema.ObjectEntry(
            self.subschema.DN("ou=users") + self.dn_base,
            ou=["users"],
            objectClass=["top", "organizationalUnit"],
            structuralObjectClass=["organizationalUnit"],
        )

    def do_search_users(self, baseobj, scope, filterobj):
        template = self.subschema.EntryTemplate(
            self.subschema.DN(self.dn_base, ou="users"),
            "uid",
            structuralObjectClass=["inetorgperson"],
            objectClass=[
                "top",
                "inetorgperson",
                "organizationalperson",
                "person",
                "posixaccount",
            ],
            cn=ldapserver.WILDCARD,
            # displayname=ldapserver.WILDCARD,
            givenname=ldapserver.WILDCARD,
            # homeDirectory=ldapserver.WILDCARD,
            # mail=ldapserver.WILDCARD,
            sn=[" "],
            uid=ldapserver.WILDCARD,
            telephoneNumber=ldapserver.WILDCARD,
            # uidNumber=ldapserver.WILDCARD,
        )
        if not template.match_search(baseobj, scope, filterobj):
            return

        try:
            omm = omm_pp_list()
            fpbx = freepbx_phonebook()
        except Exception as e:
            logging.exception("error while getting users")
            raise LDAPUnavailable(f"could not get users: {e!r}")

        logging.info(f"Have {len(fpbx)} users in FreePBX and {len(omm)} users in OMM")
        for nbr, name in fpbx.items():
            if omm.get(nbr, {}).get("is_subscribed", True):
                if not omm.get(nbr, {}).get("is_active", True):
                    name = f"[XX] {name}"
                logging.debug(f"{name=} {nbr=} {omm.get(nbr)=}")
                yield template.create_entry(
                    nbr,
                    cn=[name],
                    # displayname=[name],
                    givenname=[name],
                    # homeDirectory=[f"/home/{nbr}"],
                    # mail=[f"{nbr}@example.com"],
                    uid=[nbr],
                    telephoneNumber=[nbr],
                    # uidNumber=[nbr],
                )


def make_requesthandler():
    class RequestHandler(UffdLDAPRequestHandler):
        pass

    dn_base = RequestHandler.subschema.DN.from_str(BASE_DN)
    RequestHandler.dn_base = dn_base
    RequestHandler.bind_password = None
    return RequestHandler


if __name__ == "__main__":
    RequestHandler = make_requesthandler()
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 3389), RequestHandler)
    server.serve_forever()
