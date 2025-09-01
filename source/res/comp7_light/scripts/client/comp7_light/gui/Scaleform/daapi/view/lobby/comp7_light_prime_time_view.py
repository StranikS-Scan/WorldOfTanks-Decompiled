# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/comp7_light_prime_time_view.py
from comp7_core.gui.Scaleform.daapi.view.lobby.comp7_core_prime_time_view import Comp7CorePrimeTimeView
from comp7_light.gui.comp7_light_constants import PREBATTLE_ACTION_NAME
from comp7_light.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightPrimeTimeView(Comp7CorePrimeTimeView):
    _RES_STATUS_ROOT = R.strings.comp7_light.primeTimeView.status
    __comp7LightCtrl = dependency.descriptor(IComp7LightController)

    def _getController(self):
        return self.__comp7LightCtrl

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.COMP7_LIGHT

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.COMP7_LIGHT

    @property
    def _seasonNameClazz(self):
        return SeasonName
