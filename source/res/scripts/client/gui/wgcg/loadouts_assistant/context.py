# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/loadouts_assistant/context.py
from typing import List, Set
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
from gui.game_control.wotlda.constants import SupportedWotldaLoadoutType

class LoadoutsAssistantCtx(CommonWebRequestCtx):
    _LOADOUT_TYPES = set()

    def __init__(self, clientCacheUpdatedAt):
        super(LoadoutsAssistantCtx, self).__init__()
        self._clientCacheUpdatedAt = clientCacheUpdatedAt

    def getRequestType(self):
        return WebRequestDataType.WOTLDA_GET_LOADOUTS

    def getClientCacheUpdatedAt(self):
        return self._clientCacheUpdatedAt

    def getLoadoutTypes(self):
        return [ type_.value for type_ in self._LOADOUT_TYPES ]

    def getLoadoutTypesForRequest(self):
        return ','.join([ type_.value for type_ in self._LOADOUT_TYPES ])

    def isAuthorizationRequired(self):
        return True


class EasyTankEquipCtx(LoadoutsAssistantCtx):
    _LOADOUT_TYPES = {SupportedWotldaLoadoutType.EASY_TANK_EQUIP}


class GenericLoadoutAssistanceCtx(LoadoutsAssistantCtx):

    def addLoadoutTypes(self, types):
        self._LOADOUT_TYPES.update(types)
