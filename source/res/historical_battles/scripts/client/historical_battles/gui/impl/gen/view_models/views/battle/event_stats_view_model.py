# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/battle/event_stats_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.battle.event_stats_info_model import EventStatsInfoModel
from historical_battles.gui.impl.gen.view_models.views.battle.event_stats_team_member_model import EventStatsTeamMemberModel
from historical_battles.gui.impl.gen.view_models.views.common.stat_column_settings_model import StatColumnSettingsModel

class EventStatsViewModel(ViewModel):
    __slots__ = ('onPlayerClick',)

    def __init__(self, properties=4, commands=1):
        super(EventStatsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def info(self):
        return self._getViewModel(0)

    @property
    def columnSettings(self):
        return self._getViewModel(1)

    def getIsHeaderVisible(self):
        return self._getBool(2)

    def setIsHeaderVisible(self, value):
        self._setBool(2, value)

    def getTeam(self):
        return self._getArray(3)

    def setTeam(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(EventStatsViewModel, self)._initialize()
        self._addViewModelProperty('info', EventStatsInfoModel())
        self._addViewModelProperty('columnSettings', StatColumnSettingsModel())
        self._addBoolProperty('isHeaderVisible', False)
        self._addArrayProperty('team', Array())
        self.onPlayerClick = self._addCommand('onPlayerClick')
