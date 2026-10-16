import os
import importlib.util

def load_utils_module ():
    utils_path = os.path.join (os.path.dirname (__file__), "..", "bimdots_connection", "utils.py")
    spec = importlib.util.spec_from_file_location ("bimdots_connection_utils", utils_path)
    module = importlib.util.module_from_spec (spec)
    spec.loader.exec_module (module)
    return module

utils = load_utils_module ()

def test_get_addon_version ():
    assert utils.get_addon_version ({ "version": (2, 0, 0) }) == "2.0.0"
    assert utils.get_addon_version ({ "version": (1, 12) }) == "1.12"

def test_get_addon_version_missing ():
    assert utils.get_addon_version ({}) == ""

def test_write_log (capsys):
    utils.write_log ("Hello")
    assert capsys.readouterr ().out == "[Bimdots Connection] Hello\n"
