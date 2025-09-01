# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_no_vehicles_screen.py
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.no_vehicles_screen_model import ErrorReason
from comp7.gui.impl.gen.view_models.views.lobby.no_vehicles_screen_model import NoVehiclesScreenModel
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState
from comp7.gui.impl.gen.view_models.views.lobby.year_model import YearState
from comp7_core.gui.impl.lobby.no_vehicles_screen import NoVehiclesScreen
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7NoVehiclesScreen(NoVehiclesScreen):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller

    @property
    def _modelClazz(self):
        return NoVehiclesScreenModel

    @property
    def _seasonStateClazz(self):
        return SeasonState

    @property
    def _yearStateClazz(self):
        return YearState

    @property
    def _errorReasonClazz(self):
        return ErrorReason

    @property
    def _seasonNameClazz(self):
        return SeasonName

    @property
    def _calendarDayTooltipID(self):
        return COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO
