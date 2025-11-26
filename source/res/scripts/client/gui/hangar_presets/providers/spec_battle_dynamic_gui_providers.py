# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/providers/spec_battle_dynamic_gui_providers.py
import typing
from collections import namedtuple
from constants import QUEUE_TYPE, ARENA_GUI_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.obsolete.hangar_presets_getters import SpecBattlePresetsGetter
from gui.hangar_presets.providers.base_dynamic_gui_provider import EmptyHangarDynamicGuiProvider
from gui.hangar_presets.providers.default_dynamic_gui_provider import BaseHangarDynamicGuiProvider
from gui.impl.lobby.missions.missions_helpers import DefaultMissionsGuiHelper
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.legacy.entity import BaseLegacyEntity
SpecBattleGuiSettings = namedtuple('SpecBattleGuiSettings', ('bonusType', 'modifiersGetter', 'lobbyHelper', 'missionsHelper'))
DEFAULT_SPEC_GUI_SETTINGS = SpecBattleGuiSettings(ARENA_BONUS_TYPE.UNKNOWN, EmptyHangarDynamicGuiProvider.getDefaultBattleModifiers, DefaultLobbyHeaderHelper, DefaultMissionsGuiHelper)

class SpecBattleHangarDynamicGuiProvider(BaseHangarDynamicGuiProvider):
    GUI_TYPE_TO_SPEC_SETTINGS = {}

    def __init__(self, config, guiType=ARENA_GUI_TYPE.UNKNOWN):
        super(SpecBattleHangarDynamicGuiProvider, self).__init__(config)
        guiTypesPresets = config.modes.get(QUEUE_TYPE.SPEC_BATTLE, {})
        self._presetGetter = SpecBattlePresetsGetter(config.presets.get(guiTypesPresets.get(guiType)), guiType)
        self._guiSettings = self.GUI_TYPE_TO_SPEC_SETTINGS.get(guiType, DEFAULT_SPEC_GUI_SETTINGS)

    def createAllBonusTypes(self):
        return {settings.bonusType:SpecBattleHangarDynamicGuiProvider(self._config, guiType) for guiType, settings in self.GUI_TYPE_TO_SPEC_SETTINGS.iteritems()}

    def createByPrbEntity(self, prbEntity):
        return SpecBattleHangarDynamicGuiProvider(self._config, prbEntity.getSettings()['arenaGuiType'])

    def getBattleModifiers(self):
        return self._guiSettings.modifiersGetter()

    def getLobbyHeaderHelper(self):
        return self._guiSettings.lobbyHelper

    def getMissionsHelper(self):
        return self._guiSettings.missionsHelper

    def getPresetsGetter(self):
        return self._presetGetter

    def getSuggestedBonusType(self):
        return self._guiSettings.bonusType
