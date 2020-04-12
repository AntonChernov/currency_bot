# -*- coding: utf-8 -*-
import importlib.util
import os


def conf(filename=None):
    spec = importlib.util.spec_from_file_location(
        os.environ.get('SETTINGSFILE', 'settings_base' if not filename else filename),
        os.environ.get('SETTINGSPATH', os.getcwd() + '/settings/{0}.py'.format(
            'settings_base' if not filename else filename))
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

settings = conf()