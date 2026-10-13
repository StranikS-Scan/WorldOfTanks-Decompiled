# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/battle/event_stats_view_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.battle.event_stats_team_member_model import EventStatsTeamMemberModel
from halloween.gui.impl.gen.view_models.views.common.stat_column_settings_model import StatColumnSettingsModel

class EventStatsViewModel(ViewModel):
    __slots__ = ('onPlayerClick', 'onSendFriendRequest', 'onSendPlatoonInvitation', 'onRemoveFromBlacklist')

    def __init__(self, properties=4, commands=4):
        super(EventStatsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def columnSettings(self):
        return self._getViewModel(0)

    @staticmethod
    def getColumnSettingsType():
        return StatColumnSettingsModel

    def getTeam(self):
        return self._getArray(1)

    def setTeam(self, value):
        self._setArray(1, value)

    @staticmethod
    def getTeamType():
        return EventStatsTeamMemberModel

    def getContextMenuPlayerId(self):
        return self._getNumber(2)

    def setContextMenuPlayerId(self, value):
        self._setNumber(2, value)

    def getClientArenaIdx(self):
        return self._getNumber(3)

    def setClientArenaIdx(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(EventStatsViewModel, self)._initialize()
        self._addViewModelProperty('columnSettings', StatColumnSettingsModel())
        self._addArrayProperty('team', Array())
        self._addNumberProperty('contextMenuPlayerId', -1)
        self._addNumberProperty('clientArenaIdx', 0)
        self.onPlayerClick = self._addCommand('onPlayerClick')
        self.onSendFriendRequest = self._addCommand('onSendFriendRequest')
        self.onSendPlatoonInvitation = self._addCommand('onSendPlatoonInvitation')
        self.onRemoveFromBlacklist = self._addCommand('onRemoveFromBlacklist')
