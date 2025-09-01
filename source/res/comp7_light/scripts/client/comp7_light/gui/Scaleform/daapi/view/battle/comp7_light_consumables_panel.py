# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/battle/comp7_light_consumables_panel.py
from comp7_core.gui.Scaleform.daapi.view.battle.consumables_panel import Comp7CoreConsumablesPanel
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightConsumablesPanel(Comp7CoreConsumablesPanel):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    @property
    def _modeController(self):
        return self.__comp7LightController
