# Embedded file name: scripts/client/gui/doc_loaders/__init__.py
from items import _xml

def readDict(xmlCtx, section, subsectionName, converter = lambda value: value.asString):
    result = {}
    for name, value in _xml.getChildren(xmlCtx, section, subsectionName):
        result[name] = converter(value)

    return result
