# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/award_handlers.py
import types
import logging
from chat_shared import SYS_MESSAGE_TYPE
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from gui.game_control.AwardController import CustomizationRewardHandler, ServiceChannelHandler
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.gui.shared.event_dispatcher import showAttachmentRewardWindow, showDifficultyView, showKingRewardCongratsView, showDecryptWindowView
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen import R
from gui import SystemMessages
from frameworks.wulf import WindowStatus
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.gui.ls_gui_constants import DIFFICULTY_LEVEL_TO_TOKEN, DIFFICULTY_TOKEN_TO_LEVEL, DifficultyLevel, QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from last_stand_common.last_stand_constants import TOKEN_DIFFICULTY_LEVEL_TO_QUEUE_TYPE
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui import ls_account_settings as settings
_logger = logging.getLogger(__name__)

class LSArtefactAwardWindowHandler(ServiceChannelHandler):
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)

    def __init__(self, awardCtrl):
        super(LSArtefactAwardWindowHandler, self).__init__(SYS_MESSAGE_TYPE.lsArtefactRewardCongrats.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        if not super(LSArtefactAwardWindowHandler, self)._needToShowAward(ctx):
            return False
        else:
            _, msg = ctx
            if msg is not None and isinstance(msg.data, types.DictType):
                tokenID = msg.data.get('tokenID')
                if tokenID is not None:
                    return True
            return False

    def _showAward(self, ctx):
        _, message = ctx
        tokenID = message.data.get('tokenID')
        artefactID = self.lsArtifactsCtrl.geArtefactIDFromOpenToken(tokenID)
        showDecryptWindowView(artefactID, useQueue=True, isReward=True)
        if self._isFinalRewardArtefactToken(tokenID):
            showKingRewardCongratsView(useQueue=True)

    def _isFinalRewardArtefactToken(self, token):
        artefact = self.lsArtifactsCtrl.getArtefact(self.lsArtifactsCtrl.geArtefactIDFromOpenToken(token))
        return self.lsArtifactsCtrl.isFinalArtefact(artefact) if artefact else False


class LSDifficultyAwardWindowHandler(ServiceChannelHandler):
    difficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    lsCtrl = dependency.descriptor(ILSController)
    guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, awardCtrl):
        super(LSDifficultyAwardWindowHandler, self).__init__(SYS_MESSAGE_TYPE.lsDifficultyRewardCongrats.index(), awardCtrl)
        self.ctx = None
        return

    def fini(self):
        self.ctx = None
        if self.guiLoader and self.guiLoader.windowsManager:
            self.guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        super(LSDifficultyAwardWindowHandler, self).fini()
        return

    def start(self):
        super(LSDifficultyAwardWindowHandler, self).start()
        self.guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def _showAward(self, ctx):
        self.ctx = ctx

    def _show(self, data):
        difficultyToken = data.get('tokenID')
        if difficultyToken is not None:
            difficulty = DIFFICULTY_TOKEN_TO_LEVEL.get(difficultyToken, DifficultyLevel.EASY)
            if difficulty == DifficultyLevel.EASY:
                return
            dailyWidget = self.lsCtrl.getModeSettings().dailyBonusSettings['difficultyTokenOpenDailyWidget']
            queueType = TOKEN_DIFFICULTY_LEVEL_TO_QUEUE_TYPE.get(dailyWidget)
            lvlOpenDaily = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType] if queueType else None
            showDifficultyView(difficulty.value, showDailyWidget=lvlOpenDaily == difficulty, useQueue=True)
            settings.setAwardUnlockedLevel(difficulty)
            difficultyKey = 'difficultyLevel_{}'.format(difficulty.value)
            difficultyUnlockedTitle = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.dyn(difficultyKey).title())
            difficultyUnlockedDescription = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.dyn(difficultyKey).description())
            SystemMessages.pushMessage(difficultyUnlockedTitle, type=SM_TYPE.lsDifficultyOpenMessage, priority=NotificationPriorityLevel.MEDIUM, messageData={'description': difficultyUnlockedDescription})
        return

    def __onWindowStatusChanged(self, uniqueID, newState):
        if newState == WindowStatus.LOADED:
            window = self.guiLoader.windowsManager.getWindow(uniqueID)
            if window is None or window.content is None:
                return
            from last_stand.gui.impl.lobby.hangar_view import HangarView
            if isinstance(window.content, HangarView):
                self.__handleWindowStatus()
        elif newState == WindowStatus.LOADING:
            window = self.guiLoader.windowsManager.getWindow(uniqueID)
            if window is None or window.content is None:
                return
            from last_stand.gui.impl.lobby.battle_result_view import BattleResultView
            if isinstance(window.content, BattleResultView) and self.lsCtrl.isEventPrb() and self.ctx:
                self.__handleWindowStatus()
        return

    def __handleWindowStatus(self):
        self.guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        if self.ctx:
            _, message = self.ctx
            self._show(message.data or {'tokenID': None})
            self.ctx = None
        elif self.__hasAnyNotShownAward():
            for item in self.difficultyCtrl.getLevelsInfo():
                if not item.isUnlock or item.level.value in settings.getSettings(AccountSettingsKeys.AWARD_UNLOCK_LEVELS):
                    continue
                self._show({'tokenID': DIFFICULTY_LEVEL_TO_TOKEN.get(item.level)})

        return

    def __hasAnyNotShownAward(self):
        return any((item.level != DifficultyLevel.EASY and item.isUnlock and item.level.value not in settings.getSettings(AccountSettingsKeys.AWARD_UNLOCK_LEVELS) for item in self.difficultyCtrl.getLevelsInfo()))


class LSCustomizationRewardHandler(CustomizationRewardHandler):
    _SYS_MESSAGE_TYPES = (SYS_MESSAGE_TYPE.lsInvoiceReceived.index(),)

    def _show(self, element, isFirstEntry):
        showAttachmentRewardWindow(element, isFirstEntry)
