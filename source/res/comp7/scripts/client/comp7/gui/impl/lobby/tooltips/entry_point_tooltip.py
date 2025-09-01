# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/entry_point_tooltip.py
from comp7_core.gui.impl.lobby.tooltips.entry_point_tooltip import Comp7CoreEntryPointTooltip
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName as Comp7SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState as Comp7SeasonState
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.entry_point_tooltip_model import EntryPointTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7EntryPointTooltip(Comp7CoreEntryPointTooltip):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        settings = ViewSettings(R.views.comp7.mono.lobby.tooltips.entry_point_tooltip())
        settings.model = EntryPointTooltipModel()
        super(Comp7EntryPointTooltip, self).__init__(settings)

    @property
    def _modeController(self):
        return self.__comp7Controller

    @property
    def _seasonStateClazz(self):
        return Comp7SeasonState

    @property
    def _seasonNameClazz(self):
        return Comp7SeasonName

    def _getEvents(self):
        return super(Comp7EntryPointTooltip, self)._getEvents() + ((self.__comp7Controller.onComp7RanksConfigChanged, self.__onConfigChanged),)

    def __onConfigChanged(self):
        self._updateState()
