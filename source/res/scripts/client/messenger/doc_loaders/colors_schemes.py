# Embedded file name: scripts/client/messenger/doc_loaders/colors_schemes.py
from messenger.doc_loaders import _xml_helpers

def _readColors(xmlCtx, section, colorsNames, defName):
    result = {}
    notFound = colorsNames[:]
    for tagName, subSec in section.items():
        if tagName != 'color':
            raise _xml_helpers.XMLError(xmlCtx, 'Tag "{0:>s}" is invalid'.format(tagName))
        ctx = xmlCtx.next(subSec)
        name = _xml_helpers.readNoEmptyStr(ctx, subSec, 'name', 'Section "name" is not defined')
        if name not in colorsNames:
            raise _xml_helpers.XMLError(ctx, 'Name of color {0:>s} is invalid'.format(name))
        result[name] = _xml_helpers.readRGB(ctx, subSec, 'rgb', 'Color is invalid.')
        notFound.remove(name)

    if len(notFound):
        defColor = 0
        if defName in result:
            defColor = result[defName]
        for name in notFound:
            result[name] = defColor

    return result


def _readColorScheme(xmlCtx, section, colorScheme):
    names = colorScheme.getColorsNames()
    defName = colorScheme.getDefColorName()
    for tagName, subSec in section.items():
        if tagName == 'name':
            continue
        if tagName != 'item':
            raise _xml_helpers.XMLError(xmlCtx, 'Tag "{0:>s}" is invalid'.format(tagName))
        ctx = xmlCtx.next(subSec)
        name = _xml_helpers.readNoEmptyStr(ctx, subSec, 'name', 'Section "name" is not defined')
        colorsSec = subSec['colors']
        if not colorsSec:
            raise _xml_helpers.XMLError(ctx, 'Section "colors" is not defined')
        colorScheme[name] = _readColors(ctx.next(colorsSec), colorsSec, names, defName)


def load(xmlCtx, section, messengerSettings):
    for tagName, subSec in section.items():
        if tagName != 'colorScheme':
            raise _xml_helpers.XMLError(xmlCtx, 'Tag {0:>s} is invalid'.format(tagName))
        ctx = xmlCtx.next(subSec)
        name = _xml_helpers.readNoEmptyStr(ctx, subSec, 'name', 'Color scheme name is not defined')
        colorScheme = messengerSettings.getColorScheme(name)
        if colorScheme is not None:
            _readColorScheme(ctx, subSec, colorScheme)

    return
