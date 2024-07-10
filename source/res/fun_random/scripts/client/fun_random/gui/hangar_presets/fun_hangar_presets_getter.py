# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/hangar_presets/fun_hangar_presets_getter.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import FunRandomLobbyHeaderHelper
from gui.hangar_presets.hangar_gui_helpers import ifComponentInPreset
from gui.hangar_presets.hangar_presets_getters import BasePresetsGetter
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS

class FunRandomPresetsGetter(BasePresetsGetter, FunSubModesWatcher):
    __slots__ = ('__subModesPresets',)
    _QUEUE_TYPE = QUEUE_TYPE.FUN_RANDOM
    _BONUS_TYPES = (ARENA_BONUS_TYPE.FUN_RANDOM,)
    _LOBBY_HEADER_HELPER = FunRandomLobbyHeaderHelper

    def __init__(self, config):
        super(FunRandomPresetsGetter, self).__init__(config)
        self.__subModesPresets = config.modes[self._QUEUE_TYPE]

    @hasDesiredSubMode(abortAction='getDefaultBattleModifiers')
    def getBattleModifiers(self):
        return self.getDesiredSubMode().getModifiersDataProvider().getModifiers()

    @ifComponentInPreset(HANGAR_CONSTS.ALERT_MESSAGE, abortAction='getDefaultHangarAlertBlock')
    def getHangarAlertBlock(self, preset=None):
        return self.getDesiredSubMode().getAlertBlock()

    @hasDesiredSubMode()
    def getPreset(self):
        desiredSubModeImpl = self.getDesiredSubMode().getSubModeImpl()
        return self._config.presets.get(self.__subModesPresets.get(desiredSubModeImpl))
