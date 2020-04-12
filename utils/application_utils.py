# -*- coding: utf-8 -*-
import importlib


def auto_loader(installed_apps=None, filename=None, parameter=None):
    if not all([installed_apps, filename]):
        raise ValueError('INSTALLED_APPS: {0} filename: {1} must be set!'
                         ''.format(installed_apps, filename))
    all_list = []
    imports = ['{0}.{1}'.format(i, filename) for i in installed_apps]
    import_files = [module for module in map(importlib.import_module, imports)]
    if parameter:
        for file_name in import_files:
            if parameter and hasattr(file_name, parameter):
                try:
                    all_list += getattr(file_name, parameter)
                except TypeError:
                    all_list.append(getattr(file_name, parameter))
            else:
                raise ValueError('Not find in app: {0} '
                                 'module: {1} '
                                 'attribute: {2}'.format(installed_apps, filename, parameter))
    else:
        all_list = import_files
    return all_list
