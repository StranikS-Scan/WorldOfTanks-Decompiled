# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/providers/base_dynamic_gui_provider.py
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from battle_modifiers_common import BattleModifiers, BattleParams, getGlobalModifiers
from constants import ARENA_BONUS_TYPE, IS_DEVELOPMENT
from gui.hangar_presets.obsolete.hangar_presets_getters import IPresetsGetter, EmptyPresetsGetter
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.entity import BasePrbEntity
    from gui.impl.lobby.missions.missions_helpers import IMissionsGuiHelper
    from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import ILobbyHeaderControlsHelper

class IHangarDynamicGuiProvider(object):

    def createAllBonusTypes(self):
        raise NotImplementedError

    def createByPrbEntity(self, prbEntity):
        raise NotImplementedError

    def getBattleModifiers(self):
        raise NotImplementedError

    def getBonusCapsOverrides(self):
        raise NotImplementedError

    def getLobbyHeaderHelper(self):
        raise NotImplementedError

    def getMissionsHelper(self):
        raise NotImplementedError

    def getPresetsGetter(self):
        raise NotImplementedError

    def getSuggestedBonusType(self):
        raise NotImplementedError


class EmptyHangarDynamicGuiProvider(IHangarDynamicGuiProvider):
    _DEFAULT_BATTLE_MODIFIERS = BattleModifiers()
    _DEFAULT_PRESETS_GETTER = EmptyPresetsGetter()

    @classmethod
    def getDefaultBattleModifiers(cls):
        return getGlobalModifiers() if IS_DEVELOPMENT else cls._DEFAULT_BATTLE_MODIFIERS

    @classmethod
    def getDefaultBonusCapsOverrides(cls):
        return BONUS_CAPS.OVERRIDE_BONUS_CAPS or {}

    @classmethod
    def getDefaultLobbyHeaderHelper(cls):
        return None

    @classmethod
    def getDefaultMissionsHelper(cls):
        return None

    @classmethod
    def getDefaultPresetsGetter(cls):
        return cls._DEFAULT_PRESETS_GETTER

    @classmethod
    def getDefaultSuggestedBonusType(cls):
        return ARENA_BONUS_TYPE.UNKNOWN

    def createAllBonusTypes(self):
        return {}

    def createByPrbEntity(self, prbEntity):
        return self

    def getBattleModifiers(self):
        return self.getDefaultBattleModifiers()

    def getBonusCapsOverrides(self):
        return self.getDefaultBonusCapsOverrides()

    def getLobbyHeaderHelper(self):
        return self.getDefaultLobbyHeaderHelper()

    def getMissionsHelper(self):
        return self.getDefaultMissionsHelper()

    def getPresetsGetter(self):
        return self.getDefaultPresetsGetter()

    def getSuggestedBonusType(self):
        return self.getDefaultSuggestedBonusType()


class BaseHangarDynamicGuiProvider(EmptyHangarDynamicGuiProvider):
    _BONUS_TYPES = (ARENA_BONUS_TYPE.UNKNOWN,)
    _LOBBY_HEADER_HELPER = None
    _MISSIONS_HELPER = None

    def __init__(self, config):
        self._config = config

    def getBonusCapsOverrides(self):
        return self.getBattleModifiers()(BattleParams.BONUS_CAPS_OVERRIDES, self.getDefaultBonusCapsOverrides())

    def getLobbyHeaderHelper(self):
        return self._LOBBY_HEADER_HELPER

    def getMissionsHelper(self):
        return self._MISSIONS_HELPER

    def getSuggestedBonusType(self):
        return self._BONUS_TYPES[0]

    def createAllBonusTypes(self):
        return {bonusType:self for bonusType in self._BONUS_TYPES if bonusType != ARENA_BONUS_TYPE.UNKNOWN}
