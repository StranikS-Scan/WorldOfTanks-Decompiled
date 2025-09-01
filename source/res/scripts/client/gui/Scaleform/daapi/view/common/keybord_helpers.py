# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/keybord_helpers.py
import typing
from collections import namedtuple
import BigWorld
import CommandMapping
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from helpers.i18n import makeString

class _HotKeysInfo(namedtuple('_HotKeysInfo', ('vKey', 'keyName'))):

    def asDict(self):
        return {'vKey': self.vKey,
         'keyName': self.keyName}


def getHotKeyList(command):
    keys = [ makeString(READABLE_KEY_NAMES.key(vKey)) for vKey in _getHotKeyVkList(command) ]
    return keys


def getHotKeysInfo(command):
    return [ _HotKeysInfo(vKey, makeString(READABLE_KEY_NAMES.key(vKey))) for vKey in _getHotKeyVkList(command) ]


def _getHotKeyVkList(command):
    key, satelliteKeys = CommandMapping.g_instance.getCommandKeys(command)
    keys = [ BigWorld.keyToString(satelliteKey) for satelliteKey in satelliteKeys ]
    keys.append(BigWorld.keyToString(key))
    return keys
