# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/quests_giver_view.py
import logging
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf.view.array import fillIntsArray
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.utils import playRecruitVoiceover
from gui.server_events.quests_progress_visitor import QuestsProgressVisitor
from gui.shared.utils.scheduled_notifications import AcyclicNotifier
from helpers import dependency
from items.components.tankmen_components import SPECIAL_VOICE_TAG
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import TabId
from skeletons.gui.game_control import ISpecialSoundCtrl
from mt_birthday.gui.birthday_helpers import isBirthdayOrdinaryQuest
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import updateQuestGiverQuestsModel, getQuestsRefreshTime, getQuestsFinishTimeLeft
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.quests_giver_view_model import QuestsGiverViewModel
from gui.impl.pub import ViewImpl
from mt_birthday.gui.impl.lobby.tooltips.golden_ticket_tooltip import GoldTicketTooltip
from mt_birthday.gui.impl.lobby.tooltips.quests_description_rules_tooltip import DescriptionRulesTooltip
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from shared_utils import first
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_TIMER_DELAY = 2

class QuestsGiverView(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __specialSounds = dependency.descriptor(ISpecialSoundCtrl)
    __slots__ = ('__tooltipData', '__questsProgressVisitor', '__notifier', '__sound')

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = QuestsGiverViewModel()
        self.__tooltipData = {}
        self.__questsProgressVisitor = QuestsProgressVisitor()
        self.__notifier = None
        self.__sound = None
        super(QuestsGiverView, self).__init__(settings)
        return

    def _getEvents(self):
        return ((self.__tankBirthdayController.onQuestsUpdated, self.__onQuestsUpdated),
         (self.viewModel.onTabVisited, self.__onTabVisited),
         (self.viewModel.onSoundClick, self.__onSoundClick),
         (self.viewModel.onTabActivate, self.__onTabActivate),
         (self.__questsProgressVisitor.onGroupsVisited, self.__onGroupsVisited),
         (self.__tankBirthdayController.onEventSettingsUpdated, self.__onQuestsUpdated))

    def _onLoading(self, *args, **kwargs):
        super(QuestsGiverView, self)._onLoading()
        self.buildQuests()

    def _finalize(self):
        super(QuestsGiverView, self)._finalize()
        self.__cancelNotifiers()
        self.__questsProgressVisitor.visit()
        self.__questsProgressVisitor.clear()
        if self.__sound and self.__sound.isPlaying:
            self.__sound.stop()
        self.__sound = None
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip():
            return GoldTicketTooltip()
        return DescriptionRulesTooltip(event.getArgument('minLevel', MIN_VEHICLE_LEVEL), event.getArgument('maxLevel', MAX_VEHICLE_LEVEL), event.getArgument('battleTypes', '')) if contentID == R.views.mt_birthday.lobby.tooltips.DescriptionRulesTooltip() else super(QuestsGiverView, self).createToolTipContent(event, contentID)

    def buildQuests(self):
        currentQuestFinish, currentChallengeFinish = (0, 0)
        quests, challenges = self.__tankBirthdayController.getQuestGiverBattleQuests()
        with self.viewModel.transaction() as tx:
            assignmentsQuests = tx.getAssignmentsQuests()
            assignmentsQuests.clear()
            challengeQuests = tx.getChallengeQuests()
            challengeQuests.clear()
            res = updateQuestGiverQuestsModel(assignmentsQuests, challengeQuests, quests, challenges, self.__tooltipData)
            minLevel, maxLevel, battleTypes, nextQuestUnlockDelta, nextChallengeUnlockDelta, firstActiveQuest = res
            if not challengeQuests or not assignmentsQuests:
                tx.setIsQuestsError(True)
            elif challengeQuests and assignmentsQuests:
                tx.setIsQuestsError(False)
            tx.setMinLevel(minLevel)
            tx.setMaxLevel(maxLevel)
            if not nextQuestUnlockDelta or not nextChallengeUnlockDelta:
                currentQuestFinish, currentChallengeFinish = getQuestsFinishTimeLeft(quests, challenges)
            tx.setTimeUpdate(nextQuestUnlockDelta or currentQuestFinish)
            tx.setTimeNewQuest(nextChallengeUnlockDelta or currentChallengeFinish)
            nextQuestUpdateDelta = min(nextChallengeUnlockDelta, nextQuestUnlockDelta)
            self.__startNotifiers(nextQuestUpdateDelta)
            if firstActiveQuest is None or isBirthdayOrdinaryQuest(firstActiveQuest.getID()) or not self.__tankBirthdayController.isTabTipsCompleted(TabId.QUESTS):
                tx.setDefaultTab(QuestsGiverViewModel.ASSIGNMENTS)
            else:
                tx.setDefaultTab(QuestsGiverViewModel.CHALLENGE)
            battleTypesModel = tx.getBattleTypes()
            battleTypesModel.clear()
            fillIntsArray(battleTypes, battleTypesModel)
            battleTypesModel.invalidate()
        return

    def __onTabActivate(self):
        currentQuestFinish, currentChallengeFinish = (0, 0)
        quests, challenges = self.__tankBirthdayController.getQuestGiverBattleQuests()
        nextQuestUnlock, nextChallengeUnlock = getQuestsRefreshTime(quests, challenges)
        if not nextChallengeUnlock or not nextQuestUnlock:
            currentQuestFinish, currentChallengeFinish = getQuestsFinishTimeLeft(quests, challenges)
        with self.viewModel.transaction() as tx:
            tx.setTimeUpdate(nextQuestUnlock or currentQuestFinish)
            tx.setTimeNewQuest(nextChallengeUnlock or currentChallengeFinish)

    def __startNotifiers(self, timeQuestsUpdate):
        if timeQuestsUpdate is None:
            return
        else:
            self.__cancelNotifiers()
            self.__notifier = AcyclicNotifier(lambda : timeQuestsUpdate + _TIMER_DELAY, self.__onQuestsUpdated)
            self.__notifier.startNotification()
            return

    def __cancelNotifiers(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier = None
        return

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def __onQuestsUpdated(self, *args):
        self.buildQuests()
        waitVisitedTabId = first(self.__questsProgressVisitor.getWaitVisitGroups(), None)
        self.__questsProgressVisitor.reuse()
        if waitVisitedTabId is not None:
            self.__addQuestsToVisited(waitVisitedTabId)
        return

    @args2params(int)
    def __onTabVisited(self, idTab):
        self.__questsProgressVisitor.visit()
        if not self.__questsProgressVisitor.isGroupVisited(idTab):
            self.__addQuestsToVisited(idTab)

    def __onSoundClick(self):
        characterVoiceOver = self.__specialSounds.getVoiceoverByTankmanTag(SPECIAL_VOICE_TAG.DR26_TIMURKA)
        if characterVoiceOver is None:
            return
        else:
            self.__toggleSoundAnimation(isActive=True)
            self.__sound = playRecruitVoiceover(characterVoiceOver)
            self.__sound.setCallback(self.__toggleSoundAnimation)
            return

    def __toggleSoundAnimation(self, sound=None, isActive=False):
        with self.viewModel.transaction() as tx:
            tx.setIsSoundAnimationActive(isActive)

    def __addQuestsToVisited(self, tabId):
        quests = self.__getTabQuests(tabId)
        if quests:
            self.__questsProgressVisitor.markQuestForVisitedFromQuestsModel(tabId, quests)

    def __onGroupsVisited(self, tabIds):
        for tabId in tabIds:
            quests = self.__getTabQuests(tabId)
            if quests:
                for questModel in quests:
                    for item in questModel.bonusCondition.getItems():
                        item.setEarned(0)

                quests.invalidate()

    def __getTabQuests(self, tabId):
        quests = None
        if tabId == QuestsGiverViewModel.ASSIGNMENTS:
            quests = self.viewModel.getAssignmentsQuests()
        elif tabId == QuestsGiverViewModel.CHALLENGE:
            quests = self.viewModel.getChallengeQuests()
        return quests

    @property
    def viewModel(self):
        return super(QuestsGiverView, self).getViewModel()
