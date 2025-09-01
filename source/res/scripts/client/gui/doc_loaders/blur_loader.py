# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/blur_loader.py
import ResMgr
from items import _xml
XML_PATH = 'gui/blur_settings.xml'

def readBlurSettings(xmlConfigPath=XML_PATH):
    rootSection = ResMgr.openSection(xmlConfigPath)
    if rootSection is None:
        _xml.raiseWrongXml(None, xmlConfigPath, 'invalid blur XML config')
    settings = {viewName:{param:reader(viewSection[param]) for param, reader in _PARAMS.items() if param in viewSection.keys()} for viewName, viewSection in rootSection.items()}
    defaults = settings.pop('_defaults')
    defaultKeys = set(defaults)
    for viewSettings in settings.values():
        missingParams = defaultKeys - set(viewSettings)
        viewSettings.update({p:defaults[p] for p in missingParams})

    return settings


def _readAlphaParams(section):
    return {p:section.readFloat(p) for p in ('center', 'start', 'end')}


def _readDirection(section):
    return {p:section.readBool(p) for p in ('top', 'right', 'bottom', 'left')}


def _readParams(section):
    return {p:section.readInt(p) for p in ('hstart', 'hend', 'vstart', 'vend')}


def _readHorizontalParams(section):
    return {p:section.readInt(p) for p in ('leftStart', 'leftEnd', 'rightStart', 'rightEnd')}


def _readVerticalParams(section):
    return {p:section.readInt(p) for p in ('topStart', 'topEnd', 'bottomStart', 'bottomEnd')}


def _readHorizontalAlphas(section):
    return {p:section.readFloat(p) for p in ('leftStart', 'leftEnd', 'rightStart', 'rightEnd')}


def _readVerticalAlphas(section):
    return {p:section.readFloat(p) for p in ('topStart', 'topEnd', 'bottomStart', 'bottomEnd')}


def _readType(section):
    return {'regular': 0,
     'radial': 1,
     'spinning': 2}[section.asWideString]


_PARAMS = {'type': _readType,
 'dispatches': lambda section: section.asInt,
 'applienceType': lambda section: section.asInt,
 'applienceRadius': lambda section: section.asInt,
 'intensity': lambda section: section.asInt,
 'center': lambda section: section.asVector2,
 'mipsCount': lambda section: section.asInt,
 'alphaParams': _readAlphaParams,
 'direction': _readDirection,
 'params': _readParams,
 'horizontalParams': _readHorizontalParams,
 'verticalParams': _readVerticalParams,
 'horizontalAlphas': _readHorizontalAlphas,
 'verticalAlphas': _readVerticalAlphas}
