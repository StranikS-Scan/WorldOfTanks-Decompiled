# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/battle_result_view_model.py
from frameworks.wulf import Array
from halloween.gui.impl.gen.view_models.views.lobby.base_capture_info_model import BaseCaptureInfoModel
from halloween.gui.impl.gen.view_models.views.lobby.battle_info_model import BattleInfoModel
from halloween.gui.impl.gen.view_models.views.lobby.common.base_quest_model import BaseQuestModel
from halloween.gui.impl.gen.view_models.views.lobby.common.base_team_member_model import BaseTeamMemberModel
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.stat_column_settings_model import StatColumnSettingsModel

class BattleResultViewModel(BaseViewModel):
    __slots__ = ('sendFriendRequest', 'sendPlatoonInvitation', 'removeFromBlacklist')

    def __init__(self, properties=13, commands=4):
        super(BattleResultViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleInfo(self):
        return self._getViewModel(2)

    @staticmethod
    def getBattleInfoType():
        return BattleInfoModel

    @property
    def playerInfo(self):
        return self._getViewModel(3)

    @staticmethod
    def getPlayerInfoType():
        return BaseTeamMemberModel

    @property
    def playerTeamColumnSettings(self):
        return self._getViewModel(4)

    @staticmethod
    def getPlayerTeamColumnSettingsType():
        return StatColumnSettingsModel

    @property
    def enemyTeamColumnSettings(self):
        return self._getViewModel(5)

    @staticmethod
    def getEnemyTeamColumnSettingsType():
        return StatColumnSettingsModel

    @property
    def baseCaptureInfo(self):
        return self._getViewModel(6)

    @staticmethod
    def getBaseCaptureInfoType():
        return BaseCaptureInfoModel

    def getTitle(self):
        return self._getString(7)

    def setTitle(self, value):
        self._setString(7, value)

    def getSubTitle(self):
        return self._getString(8)

    def setSubTitle(self, value):
        self._setString(8, value)

    def getPlayerTeam(self):
        return self._getArray(9)

    def setPlayerTeam(self, value):
        self._setArray(9, value)

    @staticmethod
    def getPlayerTeamType():
        return BaseTeamMemberModel

    def getEnemyTeam(self):
        return self._getArray(10)

    def setEnemyTeam(self, value):
        self._setArray(10, value)

    @staticmethod
    def getEnemyTeamType():
        return BaseTeamMemberModel

    def getQuests(self):
        return self._getArray(11)

    def setQuests(self, value):
        self._setArray(11, value)

    @staticmethod
    def getQuestsType():
        return BaseQuestModel

    def getContextMenuPlayerId(self):
        return self._getNumber(12)

    def setContextMenuPlayerId(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(BattleResultViewModel, self)._initialize()
        self._addViewModelProperty('battleInfo', BattleInfoModel())
        self._addViewModelProperty('playerInfo', BaseTeamMemberModel())
        self._addViewModelProperty('playerTeamColumnSettings', StatColumnSettingsModel())
        self._addViewModelProperty('enemyTeamColumnSettings', StatColumnSettingsModel())
        self._addViewModelProperty('baseCaptureInfo', BaseCaptureInfoModel())
        self._addStringProperty('title', '')
        self._addStringProperty('subTitle', '')
        self._addArrayProperty('playerTeam', Array())
        self._addArrayProperty('enemyTeam', Array())
        self._addArrayProperty('quests', Array())
        self._addNumberProperty('contextMenuPlayerId', -1)
        self.sendFriendRequest = self._addCommand('sendFriendRequest')
        self.sendPlatoonInvitation = self._addCommand('sendPlatoonInvitation')
        self.removeFromBlacklist = self._addCommand('removeFromBlacklist')
