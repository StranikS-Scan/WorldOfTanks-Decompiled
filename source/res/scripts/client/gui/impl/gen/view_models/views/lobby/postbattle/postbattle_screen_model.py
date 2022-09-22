# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/postbattle_screen_model.py
from frameworks.wulf import ViewModel
from gui.impl.lobby.postbattle.wrappers.user_detailed_stats_model import UserDetailedStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.common_stats_model import CommonStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.events.events_stats_model import EventsStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.team_stats_model import TeamStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.user_status_model import UserStatusModel
from gui.impl.gen.view_models.views.lobby.postbattle.widgets_model import WidgetsModel

class PostbattleScreenModel(ViewModel):
    __slots__ = ('onChangeCurrentTab', 'onWidgetClick')
    PERSONAL_TAB = 'personalTab'
    TEAM_TAB = 'teamTab'
    DETAILS_TAB = 'detailsTab'
    QUESTS_TAB = 'questsTab'
    PREMIUM_TYPE_NONE = 0
    PREMIUM_TYPE_BASIC = 1
    PREMIUM_TYPE_PLUS = 2
    ARENA_TYPE_UNKNOWN = 0
    ARENA_TYPE_REGULAR = 1
    ARENA_TYPE_TRAINING = 2
    ARENA_TYPE_TOURNAMENT = 4
    ARENA_TYPE_TOURNAMENT_REGULAR = 14
    ARENA_TYPE_TOURNAMENT_CLAN = 15

    def __init__(self, properties=8, commands=2):
        super(PostbattleScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def common(self):
        return self._getViewModel(0)

    @staticmethod
    def getCommonType():
        return CommonStatsModel

    @property
    def team(self):
        return self._getViewModel(1)

    @staticmethod
    def getTeamType():
        return TeamStatsModel

    @property
    def events(self):
        return self._getViewModel(2)

    @staticmethod
    def getEventsType():
        return EventsStatsModel

    @property
    def details(self):
        return self._getViewModel(3)

    @staticmethod
    def getDetailsType():
        return UserDetailedStatsModel

    @property
    def userStatus(self):
        return self._getViewModel(4)

    @staticmethod
    def getUserStatusType():
        return UserStatusModel

    @property
    def widgets(self):
        return self._getViewModel(5)

    @staticmethod
    def getWidgetsType():
        return WidgetsModel

    def getAccountType(self):
        return self._getNumber(6)

    def setAccountType(self, value):
        self._setNumber(6, value)

    def getArenaType(self):
        return self._getNumber(7)

    def setArenaType(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(PostbattleScreenModel, self)._initialize()
        self._addViewModelProperty('common', CommonStatsModel())
        self._addViewModelProperty('team', TeamStatsModel())
        self._addViewModelProperty('events', EventsStatsModel())
        self._addViewModelProperty('details', UserDetailedStatsModel())
        self._addViewModelProperty('userStatus', UserStatusModel())
        self._addViewModelProperty('widgets', WidgetsModel())
        self._addNumberProperty('accountType', 0)
        self._addNumberProperty('arenaType', 0)
        self.onChangeCurrentTab = self._addCommand('onChangeCurrentTab')
        self.onWidgetClick = self._addCommand('onWidgetClick')
