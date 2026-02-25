# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold/tooltips/stronghold_main_widget_tooltip.py
from frameworks.wulf import ViewSettings
from gui.clans.clan_cache import g_clanCache
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.stronghold.tooltips.stronghold_main_widget_tooltip_model import StrongholdMainWidgetTooltipModel
from gui.impl.lobby.stronghold.stronghold_helpers import getClanSeasonProgressLevel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel

class StrongholdMainWidgetTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.stronghold.tooltips.StrongholdMainWidgetTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = StrongholdMainWidgetTooltipModel()
        super(StrongholdMainWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(StrongholdMainWidgetTooltip, self).getViewModel()

    @replaceNoneKwargsModel
    def _onLoading(self, model=None):
        super(StrongholdMainWidgetTooltip, self)._onLoading()
        model.setProgressionLevel(getClanSeasonProgressLevel())
        isRunning = g_clanCache.strongholdEventProvider.isSeasonRunning()
        if not isRunning:
            model.setIsEventActive(False)
            return
        else:
            eventSettings = g_clanCache.strongholdEventProvider.getSettings()
            if eventSettings is None:
                model.setIsDataAvailable(False)
                return
            model.setSprintType(eventSettings.getSprintType())
            sprintNumber = eventSettings.getSprintNumber()
            if sprintNumber:
                model.setSprintNumber(sprintNumber)
            model.setSprintStartDate(str(eventSettings.getVisibleStartDate()))
            model.setSprintEndDate(str(eventSettings.getVisibleEndDate()))
            model.setIsInClan(g_clanCache.isInClan)
            model.setIsDataAvailable(True)
            if g_clanCache.strongholdEventProvider.isSeasonEnding():
                model.setIsEventActive(False)
            else:
                model.setIsEventActive(True)
            return
