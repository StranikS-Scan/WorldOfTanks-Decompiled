# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/common_extras.py
from items import _xml
from constants import IS_CLIENT, IS_EDITOR, IS_BOT
import importlib
from debug_utils import LOG_DEBUG
import collections

def readExtras(xmlCtx, section, subsectionName, moduleName, **kwargs):
    try:
        mod = importlib.import_module(moduleName)
    except ImportError as err:
        LOG_DEBUG('{}'.format(err))
        LOG_DEBUG('No module', moduleName)

    noneExtra = mod.NoneExtra('_NoneExtra', 0, '', None)
    extras = [noneExtra]
    extrasDict = {noneExtra.name: noneExtra}
    for extraName, extraSection in _xml.getChildren(xmlCtx, section, subsectionName):
        extraName = intern(extraName)
        ctx = (xmlCtx, subsectionName + '/' + extraName)
        if extrasDict.has_key(extraName):
            _xml.raiseWrongXml(ctx, '', 'name is not unique')
        clientName, sep, serverName = extraSection.asString.partition(':')
        className = (clientName if IS_CLIENT or IS_EDITOR or IS_BOT else serverName).strip()
        classObj = getattr(mod, className, None)
        if classObj is not None:
            classExtras = classObj(extraName, len(extras), xmlCtx[1], extraSection, **kwargs)
            if isinstance(classExtras, collections.Iterable):
                for extra in classExtras:
                    extrasDict[extra.name] = extra

                extras.extend(classExtras)
            else:
                extras.append(classExtras)
                extrasDict[extraName] = classExtras
        _xml.raiseWrongXml(ctx, '', "class '%s' is not found in '%s'" % (className, mod.__name__))

    if len(extras) > 200:
        _xml.raiseWrongXml(xmlCtx, subsectionName, 'too many extras')
    return (tuple(extras), extrasDict)
