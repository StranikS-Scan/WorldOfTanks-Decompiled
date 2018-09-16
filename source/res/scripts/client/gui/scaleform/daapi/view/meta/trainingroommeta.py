# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TrainingRoomMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.View import View

class TrainingRoomMeta(View):

    def showTrainingSettings(self):
        self._printOverrideError('showTrainingSettings')

    def selectCommonVoiceChat(self, index):
        self._printOverrideError('selectCommonVoiceChat')

    def selectObserver(self, isObserver):
        self._printOverrideError('selectObserver')

    def startTraining(self):
        self._printOverrideError('startTraining')

    def swapTeams(self):
        self._printOverrideError('swapTeams')

    def changeTeam(self, accID, slot):
        self._printOverrideError('changeTeam')

    def closeTrainingRoom(self):
        self._printOverrideError('closeTrainingRoom')

    def showPrebattleInvitationsForm(self):
        self._printOverrideError('showPrebattleInvitationsForm')

    def onEscape(self):
        self._printOverrideError('onEscape')

    def canSendInvite(self):
        self._printOverrideError('canSendInvite')

    def canChangeSetting(self):
        self._printOverrideError('canChangeSetting')

    def canChangePlayerTeam(self):
        self._printOverrideError('canChangePlayerTeam')

    def canStartBattle(self):
        self._printOverrideError('canStartBattle')

    def canAssignToTeam(self, team):
        self._printOverrideError('canAssignToTeam')

    def canDestroyRoom(self):
        self._printOverrideError('canDestroyRoom')

    def getPlayerTeam(self, accID):
        self._printOverrideError('getPlayerTeam')

    def as_setObserverS(self, isObserver):
        return self.flashObject.as_setObserver(isObserver) if self._isDAAPIInited() else None

    def as_updateCommentS(self, commentStr):
        return self.flashObject.as_updateComment(commentStr) if self._isDAAPIInited() else None

    def as_updateMapS(self, arenaTypeID, maxPlayersCount, arenaName, title, arenaSubType, descriptionStr):
        return self.flashObject.as_updateMap(arenaTypeID, maxPlayersCount, arenaName, title, arenaSubType, descriptionStr) if self._isDAAPIInited() else None

    def as_updateTimeoutS(self, roundLenString):
        return self.flashObject.as_updateTimeout(roundLenString) if self._isDAAPIInited() else None

    def as_setTeam1S(self, data):
        """
        :param data: Represented by TrainingRoomTeamVO (AS)
        """
        return self.flashObject.as_setTeam1(data) if self._isDAAPIInited() else None

    def as_setTeam2S(self, data):
        """
        :param data: Represented by TrainingRoomTeamVO (AS)
        """
        return self.flashObject.as_setTeam2(data) if self._isDAAPIInited() else None

    def as_setOtherS(self, data):
        """
        :param data: Represented by TrainingRoomTeamVO (AS)
        """
        return self.flashObject.as_setOther(data) if self._isDAAPIInited() else None

    def as_setInfoS(self, data):
        """
        :param data: Represented by TrainingRoomInfoVO (AS)
        """
        return self.flashObject.as_setInfo(data) if self._isDAAPIInited() else None

    def as_setArenaVoipChannelsS(self, arenaVoipChannels):
        return self.flashObject.as_setArenaVoipChannels(arenaVoipChannels) if self._isDAAPIInited() else None

    def as_disableStartButtonS(self, value):
        return self.flashObject.as_disableStartButton(value) if self._isDAAPIInited() else None

    def as_disableControlsS(self, value):
        return self.flashObject.as_disableControls(value) if self._isDAAPIInited() else None

    def as_startCoolDownVoiceChatS(self, time):
        return self.flashObject.as_startCoolDownVoiceChat(time) if self._isDAAPIInited() else None

    def as_startCoolDownObserverS(self, time):
        return self.flashObject.as_startCoolDownObserver(time) if self._isDAAPIInited() else None

    def as_startCoolDownSettingS(self, time):
        return self.flashObject.as_startCoolDownSetting(time) if self._isDAAPIInited() else None

    def as_startCoolDownSwapButtonS(self, time):
        return self.flashObject.as_startCoolDownSwapButton(time) if self._isDAAPIInited() else None

    def as_setPlayerStateInTeam1S(self, uid, stateString, vContourIcon, vShortName, vLevel, igrType):
        return self.flashObject.as_setPlayerStateInTeam1(uid, stateString, vContourIcon, vShortName, vLevel, igrType) if self._isDAAPIInited() else None

    def as_setPlayerStateInTeam2S(self, uid, stateString, vContourIcon, vShortName, vLevel, igrType):
        return self.flashObject.as_setPlayerStateInTeam2(uid, stateString, vContourIcon, vShortName, vLevel, igrType) if self._isDAAPIInited() else None

    def as_setPlayerStateInOtherS(self, uid, stateString, vContourIcon, vShortName, vLevel, igrType):
        return self.flashObject.as_setPlayerStateInOther(uid, stateString, vContourIcon, vShortName, vLevel, igrType) if self._isDAAPIInited() else None

    def as_setPlayerTagsInTeam1S(self, uid, tags):
        """
        :param tags: Represented by Array (AS)
        """
        return self.flashObject.as_setPlayerTagsInTeam1(uid, tags) if self._isDAAPIInited() else None

    def as_setPlayerTagsInTeam2S(self, uid, tags):
        """
        :param tags: Represented by Array (AS)
        """
        return self.flashObject.as_setPlayerTagsInTeam2(uid, tags) if self._isDAAPIInited() else None

    def as_setPlayerTagsInOtherS(self, uid, tags):
        """
        :param tags: Represented by Array (AS)
        """
        return self.flashObject.as_setPlayerTagsInOther(uid, tags) if self._isDAAPIInited() else None

    def as_enabledCloseButtonS(self, value):
        return self.flashObject.as_enabledCloseButton(value) if self._isDAAPIInited() else None
