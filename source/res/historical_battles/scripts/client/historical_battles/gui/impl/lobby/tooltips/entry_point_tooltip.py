# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/entry_point_tooltip.py
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.shared.tooltips import ToolTipBaseData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.entry_point_tooltip_model import EntryPointTooltipModel, PerformanceRiskEnum
from gui.impl.pub import ViewImpl
from historical_battles.gui.impl.lobby.mode_selector.items.historical_battles_mode_selector_item import PERFORMANCE_MAP
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache

class EntryPointTooltip(ViewImpl):
    __slots__ = ()
    _gameEventController = dependency.descriptor(IGameEventController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.EntryPointTooltip())
        settings.model = EntryPointTooltipModel()
        isEnabled = self._gameEventController.isEnabled()
        dateStart = self._gameEventController.getEventStartTime()
        dateFinish = self._gameEventController.getEventFinishTime()
        currPerformanceGroup = self._gameEventController.getPerformanceGroup()
        settings.model.setEventStartDate(int(dateStart))
        settings.model.setEventEndDate(int(dateFinish))
        settings.model.setPerformanceRisk(PERFORMANCE_MAP.get(currPerformanceGroup, PerformanceRiskEnum.LOWRISK))
        settings.model.setIsHardDisabled(not isEnabled)
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()


class EntryPointTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(EntryPointTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.ENTRY_POINT_TOOLTIP)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(EntryPointTooltip(), useDecorator=False)
