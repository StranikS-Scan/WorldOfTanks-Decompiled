# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/data/default_alt_key_data.py
from collections import namedtuple
import typing
from gui.shared.tooltips.advanced.data.advanced_constants import MODULE_MOVIES
if typing.TYPE_CHECKING:
    from typing import Tuple
    from gui.shared.gui_items.fitting_item import FittingItem
AltKeyData = namedtuple('AltKeyData', ('swfName', 'header', 'description'))

class DefaultAltKeyData(object):

    @classmethod
    def getData(cls, item):
        result = []
        for mechanicName in cls._getMechanicKeys(item):
            result.append(AltKeyData(swfName=cls._getSwfName(item, mechanicName), header=cls._getHeader(item, mechanicName), description=cls._getDescriptionKey(item, mechanicName)))

        return tuple(result)

    @classmethod
    def _getMechanicKeys(cls, item):
        return (item.getGUIEmblemID(),)

    @staticmethod
    def _getHeader(item, mechanicName):
        return item.userType

    @classmethod
    def _getSwfName(cls, item, mechanicName):
        return MODULE_MOVIES.get(mechanicName)

    @classmethod
    def _getDescriptionKey(cls, item, mechanicName):
        return mechanicName
