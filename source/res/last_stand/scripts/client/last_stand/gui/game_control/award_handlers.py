# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/award_handlers.py
from __future__ import absolute_import
import logging
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from chat_shared import SYS_MESSAGE_TYPE
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from gui.game_control.AwardController import ServiceChannelHandler
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_story_point_controller import ILSStoryPointController
from last_stand.gui.shared.event_dispatcher import showAttachmentRewardWindow, showDifficultyView, showLootBoxMainViewInQueue, showStageRewardWindow, showNarrationWindowView
from last_stand_common.last_stand_constants import DifficultyMissionsSettings, MsgDataCacheKeys
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen import R
from gui import SystemMessages
from frameworks.wulf import WindowStatus
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.gui.ls_gui_constants import DIFFICULTY_LEVEL_TO_TOKEN, DIFFICULTY_TOKEN_TO_LEVEL, DifficultyLevel
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui import ls_account_settings as settings
_logger = logging.getLogger(__name__)

class LSAwardWindowHandler(ServiceChannelHandler):
    difficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsStoryPointCtrl = dependency.descriptor(ILSStoryPointController)
    lsCtrl = dependency.descriptor(ILSController)
    settingsCore = dependency.descriptor(ISettingsCore)
    guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, awardCtrl):
        super(LSAwardWindowHandler, self).__init__(SYS_MESSAGE_TYPE.lsRewardCongrats.index(), awardCtrl)

    def fini(self):
        if self.guiLoader and self.guiLoader.windowsManager:
            self.guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        super(LSAwardWindowHandler, self).fini()

    def start(self):
        super(LSAwardWindowHandler, self).start()
        self.guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def _needToShowAward(self, ctx):
        if not super(LSAwardWindowHandler, self)._needToShowAward(ctx):
            return False
        else:
            _, msg = ctx
            return any((msgKey in msg.data for msgKey in MsgDataCacheKeys.ALL)) and self.lsCtrl.isAvailable() if msg is not None and isinstance(msg.data, dict) else False

    def _showAward(self, ctx):
        _, message = ctx
        self._show(message.data or {})

    def _show(self, data):
        self._showDifficulty(data)
        self._showNarrationStoryPoint(data)
        self._showDifficultyMissions(data)
        self._showArtefacts(data)

    def _showDifficulty(self, data):
        difficulties = data.get(MsgDataCacheKeys.DIFFICULTIES, [])
        for tokenID in difficulties:
            difficulty = DIFFICULTY_TOKEN_TO_LEVEL.get(tokenID, DifficultyLevel.EASY)
            if difficulty == DifficultyLevel.EASY:
                return
            showDifficultyView(difficulty.value, useQueue=True)
            settings.setAwardUnlockedLevel(difficulty)
            difficultyKey = 'difficultyLevel_{}'.format(difficulty.value)
            difficultyUnlockedTitle = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.dyn(difficultyKey).title())
            difficultyUnlockedDescription = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.dyn(difficultyKey).description())
            SystemMessages.pushMessage(difficultyUnlockedTitle, type=SM_TYPE.lsDifficultyOpenMessage, priority=NotificationPriorityLevel.MEDIUM, messageData={'description': difficultyUnlockedDescription})

    def _showNarrationStoryPoint(self, data):
        storyPointsTokens = data.get(MsgDataCacheKeys.NARRATIVE_STORY_POINTS, [])
        for tokenID in storyPointsTokens:
            _, index = tokenID.split(':')
            self.lsStoryPointCtrl.selectedStoryPointID = self.lsStoryPointCtrl.getStoryPointIDByIndex(index)
            showNarrationWindowView(useQueue=True)

    def _showDifficultyMissions(self, data):
        difficultyMissions = data.get(MsgDataCacheKeys.DIFFICULTY_MISSISONS, [])
        for tokenID in difficultyMissions:
            _, difficulty, index, __ = tokenID.split(':')
            missionID = DifficultyMissionsSettings.DIFFICULTY_MISSISONS_QUEST_TPL.format(difficulty=difficulty, index=index)
            showStageRewardWindow(missionID, isReward=True, useQueue=True)

    def _showArtefacts(self, data):
        artefacts = data.get(MsgDataCacheKeys.ARTEFACTS, [])
        for artefactID in artefacts:
            showStageRewardWindow(artefactID, useQueue=True)
            attachments = self.lsArtifactsCtrl.getRareAttachmentsFromArtefact(artefactID)
            for element in attachments:
                self._showAttachmentView(element)

            if self.lsArtifactsCtrl.isArtefactHasLootBoxGift(artefactID):
                showLootBoxMainViewInQueue(self.lsCtrl.lootBoxesEvent)

    def _isFinalRewardArtefactToken(self, token):
        artefact = self.lsArtifactsCtrl.getArtefact(token)
        return self.lsArtifactsCtrl.isFinalArtefact(artefact) if artefact else False

    def _showAttachmentView(self, element):
        newC11nSectionHintClicked = self.settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.NEW_C11N_SECTION_HINT)
        showAttachmentRewardWindow(element, not newC11nSectionHintClicked, useQueue=True)

    def __onWindowStatusChanged(self, uniqueID, newState):
        if newState == WindowStatus.LOADED:
            window = self.guiLoader.windowsManager.getWindow(uniqueID)
            if window is None or window.content is None:
                return
            from last_stand.gui.impl.lobby.hangar_view import HangarView
            if isinstance(window.content, HangarView):
                self.__handleWindowStatus()
        return

    def __handleWindowStatus(self):
        self.guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        if self.__hasAnyNotShownAward():
            for item in self.difficultyCtrl.getLevelsInfo():
                if not item.isUnlock or item.level.value in settings.getSettings(AccountSettingsKeys.AWARD_UNLOCK_LEVELS):
                    continue
                self._show({MsgDataCacheKeys.DIFFICULTIES: [DIFFICULTY_LEVEL_TO_TOKEN.get(item.level)]})

    def __hasAnyNotShownAward(self):
        return any((item.level != DifficultyLevel.EASY and item.isUnlock and item.level.value not in settings.getSettings(AccountSettingsKeys.AWARD_UNLOCK_LEVELS) for item in self.difficultyCtrl.getLevelsInfo()))
