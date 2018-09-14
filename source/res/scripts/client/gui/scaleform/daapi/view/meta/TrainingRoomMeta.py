# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TrainingRoomMeta.py
from gui.Scaleform.framework.entities.View import View

class TrainingRoomMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def showTrainingSettings(self):
        """
        :return :
        """
        self._printOverrideError('showTrainingSettings')

    def selectCommonVoiceChat(self, index):
        """
        :param index:
        :return :
        """
        self._printOverrideError('selectCommonVoiceChat')

    def selectObserver(self, isObserver):
        """
        :param isObserver:
        :return :
        """
        self._printOverrideError('selectObserver')

    def startTraining(self):
        """
        :return :
        """
        self._printOverrideError('startTraining')

    def swapTeams(self):
        """
        :return :
        """
        self._printOverrideError('swapTeams')

    def changeTeam(self, accID, slot):
        """
        :param accID:
        :param slot:
        :return :
        """
        self._printOverrideError('changeTeam')

    def closeTrainingRoom(self):
        """
        :return :
        """
        self._printOverrideError('closeTrainingRoom')

    def showPrebattleInvitationsForm(self):
        """
        :return :
        """
        self._printOverrideError('showPrebattleInvitationsForm')

    def onEscape(self):
        """
        :return :
        """
        self._printOverrideError('onEscape')

    def canSendInvite(self):
        """
        :return Boolean:
        """
        self._printOverrideError('canSendInvite')

    def canChangeSetting(self):
        """
        :return Boolean:
        """
        self._printOverrideError('canChangeSetting')

    def canChangePlayerTeam(self):
        """
        :return Boolean:
        """
        self._printOverrideError('canChangePlayerTeam')

    def canStartBattle(self):
        """
        :return Boolean:
        """
        self._printOverrideError('canStartBattle')

    def canAssignToTeam(self, team):
        """
        :param team:
        :return Boolean:
        """
        self._printOverrideError('canAssignToTeam')

    def canDestroyRoom(self):
        """
        :return Boolean:
        """
        self._printOverrideError('canDestroyRoom')

    def getPlayerTeam(self, accID):
        """
        :param accID:
        :return int:
        """
        self._printOverrideError('getPlayerTeam')

    def as_setObserverS(self, isObserver):
        """
        :param isObserver:
        :return :
        """
        return self.flashObject.as_setObserver(isObserver) if self._isDAAPIInited() else None

    def as_updateCommentS(self, commentStr):
        """
        :param commentStr:
        :return :
        """
        return self.flashObject.as_updateComment(commentStr) if self._isDAAPIInited() else None

    def as_updateMapS(self, arenaTypeID, maxPlayersCount, arenaName, title, arenaSubType, descriptionStr):
        """
        :param arenaTypeID:
        :param maxPlayersCount:
        :param arenaName:
        :param title:
        :param arenaSubType:
        :param descriptionStr:
        :return :
        """
        return self.flashObject.as_updateMap(arenaTypeID, maxPlayersCount, arenaName, title, arenaSubType, descriptionStr) if self._isDAAPIInited() else None

    def as_updateTimeoutS(self, roundLenString):
        """
        :param roundLenString:
        :return :
        """
        return self.flashObject.as_updateTimeout(roundLenString) if self._isDAAPIInited() else None

    def as_setTeam1S(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setTeam1(data) if self._isDAAPIInited() else None

    def as_setTeam2S(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setTeam2(data) if self._isDAAPIInited() else None

    def as_setOtherS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setOther(data) if self._isDAAPIInited() else None

    def as_setInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInfo(data) if self._isDAAPIInited() else None

    def as_setArenaVoipChannelsS(self, arenaVoipChannels):
        """
        :param arenaVoipChannels:
        :return :
        """
        return self.flashObject.as_setArenaVoipChannels(arenaVoipChannels) if self._isDAAPIInited() else None

    def as_disableStartButtonS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_disableStartButton(value) if self._isDAAPIInited() else None

    def as_disableControlsS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_disableControls(value) if self._isDAAPIInited() else None

    def as_startCoolDownVoiceChatS(self, time):
        """
        :param time:
        :return :
        """
        return self.flashObject.as_startCoolDownVoiceChat(time) if self._isDAAPIInited() else None

    def as_startCoolDownObserverS(self, time):
        """
        :param time:
        :return :
        """
        return self.flashObject.as_startCoolDownObserver(time) if self._isDAAPIInited() else None

    def as_startCoolDownSettingS(self, time):
        """
        :param time:
        :return :
        """
        return self.flashObject.as_startCoolDownSetting(time) if self._isDAAPIInited() else None

    def as_startCoolDownSwapButtonS(self, time):
        """
        :param time:
        :return :
        """
        return self.flashObject.as_startCoolDownSwapButton(time) if self._isDAAPIInited() else None

    def as_setPlayerStateInTeam1S(self, uid, stateString, vContourIcon, vShortName, vLevel, igrType):
        """
        :param uid:
        :param stateString:
        :param vContourIcon:
        :param vShortName:
        :param vLevel:
        :param igrType:
        :return :
        """
        return self.flashObject.as_setPlayerStateInTeam1(uid, stateString, vContourIcon, vShortName, vLevel, igrType) if self._isDAAPIInited() else None

    def as_setPlayerStateInTeam2S(self, uid, stateString, vContourIcon, vShortName, vLevel, igrType):
        """
        :param uid:
        :param stateString:
        :param vContourIcon:
        :param vShortName:
        :param vLevel:
        :param igrType:
        :return :
        """
        return self.flashObject.as_setPlayerStateInTeam2(uid, stateString, vContourIcon, vShortName, vLevel, igrType) if self._isDAAPIInited() else None

    def as_setPlayerStateInOtherS(self, uid, stateString, vContourIcon, vShortName, vLevel, igrType):
        """
        :param uid:
        :param stateString:
        :param vContourIcon:
        :param vShortName:
        :param vLevel:
        :param igrType:
        :return :
        """
        return self.flashObject.as_setPlayerStateInOther(uid, stateString, vContourIcon, vShortName, vLevel, igrType) if self._isDAAPIInited() else None

    def as_setPlayerTagsInTeam1S(self, uid, tags):
        """
        :param uid:
        :param tags:
        :return :
        """
        return self.flashObject.as_setPlayerTagsInTeam1(uid, tags) if self._isDAAPIInited() else None

    def as_setPlayerTagsInTeam2S(self, uid, tags):
        """
        :param uid:
        :param tags:
        :return :
        """
        return self.flashObject.as_setPlayerTagsInTeam2(uid, tags) if self._isDAAPIInited() else None

    def as_setPlayerTagsInOtherS(self, uid, tags):
        """
        :param uid:
        :param tags:
        :return :
        """
        return self.flashObject.as_setPlayerTagsInOther(uid, tags) if self._isDAAPIInited() else None

    def as_enabledCloseButtonS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_enabledCloseButton(value) if self._isDAAPIInited() else None
