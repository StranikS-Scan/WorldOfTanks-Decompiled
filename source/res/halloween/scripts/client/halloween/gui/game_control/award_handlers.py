# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/award_handlers.py
from __future__ import absolute_import
import logging
import typing
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from chat_shared import SYS_MESSAGE_TYPE
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.shared.notifications import NotificationPriorityLevel
from halloween.gui.impl.lobby.hw_helpers import getEnemyByArtefactID
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from helpers import dependency
from gui.game_control.AwardController import RecruitHandler, ServiceChannelHandler
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.gui.shared.event_dispatcher import showAttachmentRewardView, showDifficultyView, showKingRewardCongratsView, showDecryptWindowView, showTwitchConExchangeView, showBestiaryWindow, showStoryChoiceWindow, showOutroVideo
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen import R
from gui import SystemMessages
from frameworks.wulf import WindowStatus
from halloween.skeletons.difficulty_level_controller import IDifficultyLevelController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.gui.halloween_gui_constants import DifficultyLevel
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.gui import halloween_account_settings
if typing.TYPE_CHECKING:
    from halloween.gui.game_control.halloween_bestiary_controller import EnemyData
_logger = logging.getLogger(__name__)

class HWArtefactAwardWindowHandler(ServiceChannelHandler):
    hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    hwBestiaryCtrl = dependency.descriptor(IHalloweenBestiaryController)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, awardCtrl):
        super(HWArtefactAwardWindowHandler, self).__init__(SYS_MESSAGE_TYPE.hwArtefactRewardCongrats.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        if not super(HWArtefactAwardWindowHandler, self)._needToShowAward(ctx):
            return False
        else:
            _, msg = ctx
            if msg is not None and isinstance(msg.data, dict):
                tokenID = msg.data.get('tokenID')
                if tokenID is not None:
                    return True
            return False

    def _showAward(self, ctx):
        _, message = ctx
        tokenID = message.data.get('tokenID')
        artefactID = self.hwArtifactsCtrl.geArtefactIDFromOpenToken(tokenID)
        leftArtefactProgress = self.hwArtifactsCtrl.getMaxArtefactsProgress() - self.hwArtifactsCtrl.getCurrentArtefactProgress()
        isLastArtefact = leftArtefactProgress == 0
        showDecryptWindowView(artefactID, useQueue=True, isReward=True, disableOutro=isLastArtefact, disableLastArtefact=not isLastArtefact)
        if leftArtefactProgress == 1:
            showOutroVideo(useQueue=True)
        if self.hwArtifactsCtrl.isArtefactHasTwitchConCertificate(artefactID):
            showTwitchConExchangeView()
        attachments = self.hwArtifactsCtrl.getRareAttachmentsFromArtefact(artefactID)
        for element in attachments:
            self._showAttachmentView(element)

        if self._isKingRewardToken(artefactID):
            showStoryChoiceWindow()
            showKingRewardCongratsView(artefactID, useQueue=True)
        enemyData = getEnemyByArtefactID(artefactID)
        if enemyData:
            if leftArtefactProgress > 1:
                showBestiaryWindow(enemyIntCD=enemyData.intCD, useQueue=True)
            else:
                self.hwBestiaryCtrl.isBestiaryPostponed = True

    def _isKingRewardToken(self, artefactID):
        artefact = self.hwArtifactsCtrl.getArtefact(artefactID)
        return self.hwArtifactsCtrl.isFinalArtefact(artefact)

    def _showAttachmentView(self, element):
        newC11nSectionHintClicked = self.settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.NEW_C11N_SECTION_HINT)
        showAttachmentRewardView(element, not newC11nSectionHintClicked, useQueue=True)


class HWDifficultyAwardWindowHandler(ServiceChannelHandler):
    difficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    hwController = dependency.descriptor(IHalloweenController)
    guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, awardCtrl):
        super(HWDifficultyAwardWindowHandler, self).__init__(SYS_MESSAGE_TYPE.hwDifficultyRewardCongrats.index(), awardCtrl)
        self.__battleResultsWindowID = None
        return

    def _needToShowAward(self, ctx):
        if self.hwController.isEventPrb() and not self.__checkBattleResultOpened():
            return True
        self.guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        return False

    def _showAward(self, ctx):
        for item in self.difficultyCtrl.getLevelsInfo():
            if item.level == DifficultyLevel.EASY or not item.isUnlock:
                continue
            if item.level.value not in halloween_account_settings.getSettings(AccountSettingsKeys.AWARD_UNLOCK_LEVELS):
                showDifficultyView(item.level.value, useQueue=True)
                difficultyKey = 'difficultyLevel_{}'.format(item.level.value)
                difficultyUnlockedTitle = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.dyn(difficultyKey).title())
                difficultyUnlockedDescription = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.dyn(difficultyKey).description())
                SystemMessages.pushMessage(difficultyUnlockedTitle, type=SM_TYPE.hwDifficultyOpenMessage, priority=NotificationPriorityLevel.MEDIUM, messageData={'description': difficultyUnlockedDescription})
                halloween_account_settings.setAwardUnlockedLevel(item.level)
                return

    def __checkBattleResultOpened(self):
        battleResults = self.guiLoader.windowsManager.getViewByLayoutID(R.views.halloween.mono.lobby.battle_result())
        if battleResults is not None:
            self.__battleResultsWindowID = battleResults.getParentWindow().uniqueID
        return self.__battleResultsWindowID is not None

    def __onWindowStatusChanged(self, uniqueID, newState):
        if newState == WindowStatus.LOADED:
            window = self.guiLoader.windowsManager.getWindow(uniqueID)
            if window is None or window.content is None:
                return
            from halloween.gui.impl.lobby.hangar_view import HangarView
            if isinstance(window.content, HangarView):
                self.__handleWindowStatus()
        elif newState == WindowStatus.DESTROYED:
            if uniqueID == self.__battleResultsWindowID:
                self.__handleWindowStatus()
        return

    def __handleWindowStatus(self):
        self.__battleResultsWindowID = None
        self.guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        self.handle(None)
        return


class HWRecruitHandler(RecruitHandler):

    def __init__(self, awardCtrl):
        ServiceChannelHandler.__init__(self, SYS_MESSAGE_TYPE.hwInvoiceReceived.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        return ServiceChannelHandler._needToShowAward(self, ctx)
