# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold/stronghold_main_widget.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventProgressionUrl
from gui.clans.clan_cache import g_clanCache
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.stronghold.stronghold_main_widget_model import StrongholdMainWidgetModel
from gui.impl.lobby.stronghold.stronghold_helpers import getClanSeasonProgressLevel, CLAN_SEASON_PROGRESS_PREFIX
from gui.impl.lobby.stronghold.tooltips.stronghold_main_widget_tooltip import StrongholdMainWidgetTooltip
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.shared import events, event_dispatcher, EVENT_BUS_SCOPE

class StrongholdMainWidgetComponent(InjectComponentAdaptor):
    __slots__ = ('__view',)

    def __init__(self):
        super(StrongholdMainWidgetComponent, self).__init__()
        self.__view = None
        return

    def _dispose(self):
        self.__view = None
        super(StrongholdMainWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = StrongholdMainWidget(flags=ViewFlags.VIEW)
        return self.__view


class StrongholdMainWidget(ViewImpl):
    __slots__ = ()

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.stronghold.StrongholdMainWidget())
        settings.flags = flags
        settings.model = StrongholdMainWidgetModel()
        super(StrongholdMainWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(StrongholdMainWidget, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(StrongholdMainWidget, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def createToolTipContent(self, event, contentID):
        return StrongholdMainWidgetTooltip() if contentID == R.views.lobby.stronghold.tooltips.StrongholdMainWidgetTooltip() else super(StrongholdMainWidget, self).createToolTipContent(event, contentID)

    def _getCallbacks(self):
        return (('stats.clanInfo', self.__onDataUpdated),)

    def _getListeners(self):
        return ((events.StrongholdEvent.STRONGHOLD_UPDATED, self.__onDataUpdated, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((g_playerEvents.onClientUpdated, self.__onTokensUpdate), (self.viewModel.onOpenStrongholdEventProgression, self.__onOpenStrongholdEventProgression))

    @replaceNoneKwargsModel
    def __fillModel(self, model=None):
        model.setProgressionLevel(getClanSeasonProgressLevel())
        model.setIsInClan(g_clanCache.isInClan)
        model.setIsActive(g_clanCache.strongholdEventProvider.isRunning())

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens', {})
        if not tokens:
            return
        if any((tokenID.startswith(CLAN_SEASON_PROGRESS_PREFIX) for tokenID, token in tokens.iteritems())):
            self.__fillModel()

    @staticmethod
    def __onOpenStrongholdEventProgression():
        event_dispatcher.showStrongholds(getStrongholdEventProgressionUrl())

    def __onDataUpdated(self, _):
        self.__fillModel()
