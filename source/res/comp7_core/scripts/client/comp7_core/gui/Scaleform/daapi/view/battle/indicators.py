# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/Scaleform/daapi/view/battle/indicators.py
import typing
from comp7_core.gui.Scaleform.daapi.view.meta.Comp7ReconFlightMeta import Comp7ReconFlightMeta
from constants import DIRECT_DETECTION_TYPE
from helpers.time_utils import MS_IN_SECOND
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator

class ReconFlightIndicator(Comp7ReconFlightMeta, SixthSenseIndicator):

    def getIndicatorTogglesByType(self):
        flightDuration = GUI_SETTINGS.reconFlightDuration / float(MS_IN_SECOND)
        return [(DIRECT_DETECTION_TYPE.SPECIAL_RECON,
          self.__toggleFlight,
          flightDuration,
          self.__isFlightEnabled)]

    def __toggleFlight(self, isVisible, _):
        if isVisible:
            self._sound.play()
            self.as_showS()
        else:
            self.as_hideS()

    def __isFlightEnabled(self):
        return True

    __toggleFlight = typing.cast(SixthSenseIndicator.ToggleType, __toggleFlight)
    __isFlightEnabled = typing.cast(SixthSenseIndicator.EnabledType, __isFlightEnabled)
