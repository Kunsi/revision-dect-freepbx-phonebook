#!/usr/bin/env python3

import re
from hashlib import md5
from json import dump
from os import environ
from os.path import abspath, dirname, join
from shutil import move

import requests

# Supress SSL certificate warnings for ssl_verify=False
import urllib3
from lxml import etree, html

USERNAME_FIELD = "g2"
PASSWORD_FIELD = "g3"
CRSF_FIELD = "password"

PATH = abspath(dirname(__file__))


from urllib3.util import create_urllib3_context

ctx = create_urllib3_context()
ctx.load_default_certs()
ctx.set_ciphers("AES128-GCM-SHA256")


class CustomSSLContextHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        self.ssl_context.check_hostname = False
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


class OMMCrawler:
    def __init__(self, hostname, username, password):
        self.session = requests.Session()
        urllib3.disable_warnings()
        self.session.verify = False
        self.session.adapters.pop("https://", None)
        self.session.mount("https://", CustomSSLContextHTTPAdapter(ctx))

        self.url = f"https://{hostname}"
        self.login_data = {
            USERNAME_FIELD: username,
            PASSWORD_FIELD: password,
            CRSF_FIELD: md5(password.encode()).hexdigest(),
        }
        self.logged_in = False

    def login(self):
        # if we have multiple dect masters, find out which one is the current master
        current_master_url = self.session.get(self.url, verify=False).url
        self.hostname = re.search(r"^(.*[\\\/])", current_master_url).group(0)[:-1]

        response = self.session.post(f"{self.url}/login_set.html", data=self.login_data)
        response.raise_for_status()

        # set cookie
        pass_value = re.search(r"(?<=pass=)\d+(?=;)", response.text).group(0)
        self.session.cookies.set("pass", pass_value)
        self.logged_in = True

    def get_pp_status(self):
        if not self.logged_in:
            self.login()

        data = {}
        response = self.session.get(f"{self.url}/pp_list.html")
        response.raise_for_status()
        tree = html.fromstring(response.text)
        xpath_results = tree.xpath('//tr[@class="l0" or @class="l1"]')

        for result in xpath_results:
            try:
                result.xpath("td[1]/img/@alt")[0]
            except Exception:
                # the form above is also a table, but doesn't have any
                # images in column 1
                continue

            user_name = result.xpath("td[5]/text()")[0]
            user_extension = result.xpath("td[6]/text()")[0]

            user_subscribed = False
            user_active = False
            try:
                user_subscribed = result.xpath("td[8]/img/@alt")[0] == "yes"
                user_active = result.xpath("td[9]/img/@alt")[0] == "yes"
            except Exception:
                pass

            data[str(user_extension)] = {
                "name": user_name,
                "is_active": user_active,
                "is_subscribed": user_subscribed,
            }
        return data


if __name__ == "__main__":
    omm = OMMCrawler(
        environ["OMM_HOST"],
        environ["OMM_USER"],
        environ["OMM_PASS"],
    )
    status = omm.get_pp_status()
    with open(join(PATH, "omm_pp.json.tmp"), "w") as f:
        dump(status, f)
    move(
        join(PATH, "omm_pp.json.tmp"),
        join(PATH, "omm_pp.json"),
    )
