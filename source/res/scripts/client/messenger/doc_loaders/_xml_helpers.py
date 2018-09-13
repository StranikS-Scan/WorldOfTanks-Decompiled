# Embedded file name: scripts/client/messenger/doc_loaders/_xml_helpers.py
import types
from helpers.html import translation as html_translation

def _convertVector3ToRGB(xmlCtx, rgb, msg):
    rgb = (int(rgb.x), int(rgb.y), int(rgb.z))
    for value in rgb:
        if value < 0 or value > 255:
            raise XMLError(xmlCtx, msg)

    return (rgb[0] << 16) + (rgb[1] << 8) + (rgb[2] << 0)


class XMLError(Exception):

    def __init__(self, ctx, message):
        super(XMLError, self).__init__()
        self.ctx = ctx
        self.message = message

    def __str__(self):
        return 'Error in {0:>s}. {1:>s}'.format(self.ctx, self.message)


class XMLCtx(object):

    def __init__(self, filePath, xpath = None):
        super(XMLCtx, self).__init__()
        self.__filePath = filePath
        if xpath is None:
            self.__xpath = []
        elif type(xpath) is types.ListType:
            self.__xpath = xpath
        else:
            raise ValueError, 'xpath must be list.'
        return

    def next(self, section):
        xpath = self.__xpath[:]
        xpath.append(section.name)
        return XMLCtx(self.__filePath, xpath)

    def prev(self):
        return XMLCtx(self.__filePath, self.__xpath[:-1])

    def __str__(self):
        path = self.__xpath[:]
        path.insert(0, self.__filePath)
        return '/'.join(path)


def readNoEmptyStr(xmlCtx, section, name, msg):
    value = section.readString(name)
    if not value:
        raise XMLError(xmlCtx, msg)
    return value


def readNoEmptyI18nStr(xmlCtx, section, name, msg):
    return html_translation(readNoEmptyStr(xmlCtx, section, name, msg))


def readRGB(xmlCtx, section, name, msg):
    return _convertVector3ToRGB(xmlCtx, section.readVector3(name), msg)


def readItem(xmlCtx, section, getter, converter = None, settings = None):
    name = readNoEmptyStr(xmlCtx, section, 'name', 'Item name is not defined')
    if 'value' not in section.keys():
        raise XMLError(xmlCtx, 'Item value is not defined')
    value = getattr(section, getter)('value')
    if converter is not None:
        value = converter(value)
    if settings is not None:
        if hasattr(settings, name):
            setattr(settings, name, value)
        else:
            raise XMLError(xmlCtx, 'Settings has not attribute {0:>s}'.format(name))
    return (name, value)


def readIntItem(xmlCtx, section, settings = None):
    return readItem(xmlCtx, section, 'readInt', settings=settings)


def readFloatItem(xmlCtx, section, settings = None):
    return readItem(xmlCtx, section, 'readFloat', settings=settings)


def readRGBItem(xmlCtx, section, settings = None):
    name, value = readItem(xmlCtx, section, 'readVector3', settings=settings)
    return (name, _convertVector3ToRGB(xmlCtx, value, 'Value is not valid'))


def readStringItem(xmlCtx, section, settings = None):
    return readItem(xmlCtx, section, 'readString', settings=settings)


def readUnicodeItem(xmlCtx, section, settings = None):
    return readItem(xmlCtx, section, 'readString', converter=lambda value: unicode(value, 'utf-8', 'ignore'), settings=settings)


def readI18nStringItem(xmlCtx, section, settings = None):
    name, value = readItem(xmlCtx, section, 'readString', converter=html_translation, settings=settings)
    return (name, value)
