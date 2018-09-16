# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/log/config.py
import logging
import logging.config
import os
import resource_helper
from . import hooks
ENV_KEY = 'PY_LOGGING_CFG'
XML_CFG_FILE = 'logging.xml'

class LogConfigurator(logging.config.DictConfigurator):

    def clear(self):
        self.config.configurator = None
        self._clearConvertor(self.config)
        self.config.clear()
        self.importer = None
        return

    @classmethod
    def _clearConvertor(cls, convertor):
        if isinstance(convertor, dict):
            iterator = convertor.itervalues()
        elif isinstance(convertor, (tuple, list)):
            iterator = convertor
        else:
            return
        for item in iterator:
            cls._clearConvertor(item)
            convertor.configurator = None
            convertor.parent = None

        return


def setupFromXML(envKey=ENV_KEY, filename=XML_CFG_FILE, level=logging.INFO):
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
        configurator = LogConfigurator(config)
        configurator.configure()
        configurator.clear()
    else:
        root = logging.getLogger()
        root.setLevel(level)


def readXMLConfig(filename):
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
