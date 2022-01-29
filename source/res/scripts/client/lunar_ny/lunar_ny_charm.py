# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_charm.py
import typing
from typing import Dict
from items import lunar_ny
from items.components.lunar_ny_constants import CharmBonuses
from lunar_ny.lunar_ny_constants import CHARM_TYPE_BY_TYPE_NAME
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmType

class LunarNYCharm(object):
    __slots__ = ('__totalCount', '__unseenCount', '__countInSlots', '__descriptor')

    def __init__(self, itemId, totalCount, unseenCount, countInSlots):
        super(LunarNYCharm, self).__init__()
        self.__descriptor = lunar_ny.g_cache.charms[itemId]
        self.__totalCount = totalCount
        self.__unseenCount = unseenCount
        self.__countInSlots = countInSlots

    def __str__(self):
        result = 'LunarNYCharm(itemId={itemId}, totalCount={totalCount}, unseenCount={unseenCount}, countInSlots={countInSlots})'
        return result.format(itemId=self.__descriptor.id, totalCount=self.__totalCount, unseenCount=self.__unseenCount, countInSlots=self.__countInSlots)

    def getID(self):
        return self.__descriptor.id

    def getCountInStorage(self):
        return self.__totalCount

    def getUnseenCount(self):
        return self.__unseenCount

    def getCountInSlots(self):
        return self.__countInSlots

    def getBonuses(self):
        return self.__descriptor.bonuses

    def getItemType(self):
        return CHARM_TYPE_BY_TYPE_NAME[self.__descriptor.type]

    @staticmethod
    def computeSum(*args):
        result = CharmBonuses.getDefaultBonuses()
        for bonus in args:
            for key, value in bonus.iteritems():
                result[key] = round(result[key] + value, 4)

        return result
