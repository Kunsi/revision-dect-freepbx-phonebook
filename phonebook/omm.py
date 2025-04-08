from json import load as json_load
from os.path import abspath, dirname, join


def omm_pp_list():
    with open(join(abspath(dirname(dirname(__file__))), "omm_pp.json")) as f:
        return json_load(f)
