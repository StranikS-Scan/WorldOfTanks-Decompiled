# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/comp7_prime_time_view.py
from comp7.gui.comp7_constants import PREBATTLE_ACTION_NAME
from comp7_core.gui.Scaleform.daapi.view.lobby.comp7_core_prime_time_view import Comp7CorePrimeTimeView
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7PrimeTimeView(Comp7CorePrimeTimeView):
    _RES_STATUS_ROOT = R.strings.comp7_ext.primeTimeView.status
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _getController(self):
        return self.__comp7Ctrl

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.COMP7

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.COMP7

    @property
    def _seasonNameClazz(self):
        return SeasonName
