# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/hangar_presets/fun_hangar_presets_getter.py
from constants import QUEUE_TYPE
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from gui.hangar_presets.hangar_presets_getters import BasePresetsGetter

class FunRandomPresetsGetter(BasePresetsGetter, FunSubModesWatcher):
    __slots__ = ('__subModesPresets',)
    _QUEUE_TYPE = QUEUE_TYPE.FUN_RANDOM

    def __init__(self, config):
        super(FunRandomPresetsGetter, self).__init__(config)
        self.__subModesPresets = config.modes[self._QUEUE_TYPE]

    @hasDesiredSubMode()
    def getPreset(self):
        desiredSubModeImpl = self.getDesiredSubMode().getSubModeImpl()
        return self._presets.get(self.__subModesPresets.get(desiredSubModeImpl))
