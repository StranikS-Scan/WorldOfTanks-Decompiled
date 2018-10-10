# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/common_extras.py
from items import _xml
from constants import IS_CLIENT, IS_BOT
import importlib
from debug_utils import LOG_DEBUG

def readExtras(xmlCtx, section, subsectionName, moduleName):
    try:
        mod = importlib.import_module(moduleName)
    except ImportError:
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
        className = (clientName if IS_CLIENT or IS_BOT else serverName).strip()
        classObj = getattr(mod, className, None)
        if classObj is None:
            _xml.raiseWrongXml(ctx, '', "class '%s' is not found in '%s'" % (className, mod.__name__))
        extra = classObj(extraName, len(extras), xmlCtx[1], extraSection)
        extras.append(extra)
        extrasDict[extraName] = extra

    if len(extras) > 200:
        _xml.raiseWrongXml(xmlCtx, subsectionName, 'too many extras')
    return (tuple(extras), extrasDict)
