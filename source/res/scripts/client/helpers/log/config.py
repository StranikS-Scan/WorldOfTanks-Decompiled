# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/log/config.py
import logging
import logging.config
import os
import resource_helper
from . import hooks
ENV_KEY = 'PY_LOGGING_CFG'
XML_CFG_FILE = 'logging.xml'

def setupFromXML(envKey=ENV_KEY, filename=XML_CFG_FILE, level=logging.WARNING):
    """ Setups logging configuration from xml file.
    :param envKey: string containing environment variable that contains
        relative path to configuration file that is started from "res" directory.
    :param filename: or string containing relative path to
        configuration file that is started from "res" directory.
    :param level: integer containing level of logging that will be applied
        if configuration file is not found.
    """
    value = os.getenv(envKey, '')
    if not value:
        value = filename
    if value:
        config = readXMLConfig(value)
    else:
        config = {}
    if config:
        if config.get('override_exception_hook', False):
            hooks.setupUserExceptionHook()
        logging.config.dictConfig(config)
    else:
        root = logging.getLogger()
        root.setLevel(level)


def readXMLConfig(filename):
    """ Reads XML file to load the logging configuration as dictionary.
    Note: Here is no any validation, validation will be applied
        if trying configure logging package.
    :param filename: string containing relative path to
          configuration file that is started from "res" directory.
    :return: dictionary containing logging configuration.
    """
    config = {}
    ctx, root = resource_helper.getRoot(filename, safe=False)
    if root is None:
        return config
    else:
        sectionCtx, section = resource_helper.getSubSection(ctx, root, 'common', safe=False)
        if section is not None:
            config.update(resource_helper.readDict(sectionCtx, section).value)
        for key in ('filters', 'formatters', 'handlers', 'loggers'):
            config[key] = _readConfigItem(key, ctx, root)

        resource_helper.purgeResource(filename)
        return config


def _readConfigItem(key, ctx, section):
    ctx, sub = resource_helper.getSubSection(ctx, section, key, safe=True)
    config = {}
    if sub is not None:
        for itemCtx, item in resource_helper.getIterator(ctx, sub):
            source = resource_helper.readDict(itemCtx, item)
            config[source.name] = source.value

    return config
