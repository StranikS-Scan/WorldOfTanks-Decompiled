# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/award_handlers.py
import logging
import types
import re
from chat_shared import SYS_MESSAGE_TYPE
from constants import INVOICE_ASSET
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from gui.game_control.AwardController import ServiceChannelHandler
from halloween.gui.impl.lobby.reward_screen_view import RewardScreenViewModel
from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
from halloween.hw_constants import QuestType, PhaseType, HWBonusesType, GLOBAL_PROGRESS_TANKMAN_QUEST, GLOBAL_PROGRESS_HW_XP_QUEST, PHASE_PATTERN
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.server_events.bonuses import DossierBonus
_logger = logging.getLogger(__name__)

class HWBattleQuestsRewardHandler(ServiceChannelHandler):
    goodiesCache = dependency.descriptor(IGoodiesCache)
    hwController = dependency.descriptor(IHalloweenProgressController)
    FIRST_QUEST_INDEX = 1
    SECOND_QUEST_INDEX = 2

    def __init__(self, awardCtrl):
        super(HWBattleQuestsRewardHandler, self).__init__(SYS_MESSAGE_TYPE.hwRewardCongrats.index(), awardCtrl)
        self._bonusesByQuestId = {}
        self._completedQuestIds = []
        self._completedPhaseQuestIds = []

    def _showAward(self, ctx):
        _, message = ctx
        self._completedQuestIds = message.data.get('completedQuestIDs')
        self._completedPhaseQuestIds = [ qId for qId in self._completedQuestIds if re.match(PHASE_PATTERN, qId) ]
        self._getGlobalProgressQuestBonuses(self._completedQuestIds)
        got_all_witches_medal = GLOBAL_PROGRESS_TANKMAN_QUEST in self._completedQuestIds
        if self._completedPhaseQuestIds:
            result = re.match(PHASE_PATTERN, self._completedPhaseQuestIds[0])
            phase = self.hwController.phasesHalloween.getPhaseByIndex(int(result.group(1)))
            completedPhaseQuests, gotAllWitches = self._getPhaseQuestsInfo(phase)
            for quest in sorted(completedPhaseQuests, key=lambda q: q.getID()):
                result = re.match(PHASE_PATTERN, quest.getID())
                bonuses = self._bonusesByQuestId[quest.getID()]
                if int(result.group(2)) == self.FIRST_QUEST_INDEX:
                    self._showRewardWindow(RewardScreenViewModel.TYPE_ALL_REWARDS, bonuses)
                if int(result.group(2)) == self.SECOND_QUEST_INDEX:
                    self._showRewardWindow(RewardScreenViewModel.TYPE_ONE_WITCH, bonuses, phase)
                    if gotAllWitches:
                        self._showRewardWindow(RewardScreenViewModel.TYPE_SHOW_CREW, None)
                        if got_all_witches_medal:
                            bonuses = self._bonusesByQuestId[GLOBAL_PROGRESS_TANKMAN_QUEST]
                            self._showRewardWindow(RewardScreenViewModel.TYPE_ALL_WITCHES, bonuses)

        if GLOBAL_PROGRESS_HW_XP_QUEST in self._completedQuestIds:
            bonuses = self._bonusesByQuestId[GLOBAL_PROGRESS_HW_XP_QUEST]
            self._showRewardWindow(RewardScreenViewModel.TYPE_XP_ACHIEVEMENT, bonuses)
        return

    def _showRewardWindow(self, screenType, bonuses=None, phase=None):
        from halloween.gui.shared.event_dispatcher import showRewardScreenWindow
        data = {'screenType': screenType,
         'phase': phase}
        showRewardScreenWindow(data, bonuses, useQueue=True)

    def _getGlobalProgressQuestBonuses(self, completedQuestIDs):
        for completedQuestID in completedQuestIDs:
            if completedQuestID not in [GLOBAL_PROGRESS_TANKMAN_QUEST, GLOBAL_PROGRESS_HW_XP_QUEST]:
                continue
            quest = self.eventsCache.getAllQuests().get(completedQuestID)
            if not quest:
                return {}
            bonusesType = getMissionInfoData(quest).getSubstituteBonuses()
            bonuses = []
            for bonusType in bonusesType:
                if not isinstance(bonusType, DossierBonus):
                    continue
                for item in bonusType.getValue().itervalues():
                    for key in item:
                        bonuses.append((None,
                         key[0],
                         key[1],
                         1))

            self._bonusesByQuestId[quest.getID()] = bonuses

        return

    def _getPhaseQuestsInfo(self, phase):
        gotAllWitches = False
        completedQuests = []
        phases = self.hwController.phasesHalloween.getPhasesByType(PhaseType.REGULAR)
        recievedWitchesCount = len([ ph for ph in phases if ph.hasPlayerTmanBonus() ])
        quests = phase.getQuestsByType(QuestType.HALLOWEEN)
        for quest in quests:
            if quest.getQuest().getID() in self._completedPhaseQuestIds:
                completedQuests.append(quest.getQuest())
                bonuses = [ bonus for bonus in quest.getBonusesInfo() ]
                if HWBonusesType.TANKMAN in [ b[1] for b in bonuses ]:
                    gotAllWitches = len(phases) == recievedWitchesCount
                self._bonusesByQuestId[quest.getQuest().getID()] = bonuses

        return (completedQuests, gotAllWitches)

    def _needToShowAward(self, ctx):
        if not super(HWBattleQuestsRewardHandler, self)._needToShowAward(ctx):
            return False
        else:
            _, msg = ctx
            if msg is not None and isinstance(msg.data, types.DictType):
                _, message = ctx
                globalHWqQests = [GLOBAL_PROGRESS_HW_XP_QUEST, GLOBAL_PROGRESS_TANKMAN_QUEST]
                completedQuestIds = message.data.get('completedQuestIDs')
                return any((qId for qId in completedQuestIds if re.match(PHASE_PATTERN, qId) or qId in globalHWqQests))
            return False


class HWInvoiceCrewBonusHandler(ServiceChannelHandler):
    hwController = dependency.descriptor(IHalloweenProgressController)
    AVAILABLE_TAGS = ['hw22.full_crew_reward', 'hw22.witch_reward']

    def __init__(self, awardCtrl):
        super(HWInvoiceCrewBonusHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)

    def _showAward(self, ctx):
        from halloween.gui.shared.event_dispatcher import showRewardScreenWindow
        invoiceData = ctx[1].data
        if invoiceData.get('assetType') in (INVOICE_ASSET.DATA, INVOICE_ASSET.PURCHASE) and 'tags' in invoiceData:
            if 'data' not in invoiceData:
                _logger.error('Invalid invoiceReceived data!')
        if any((tag for tag in invoiceData.get('tags', ()) if tag in self.AVAILABLE_TAGS)):
            phases = self.hwController.phasesHalloween.getPhasesByType(PhaseType.REGULAR)
            if len([ phase for phase in phases if phase.hasPlayerTmanBonus() ]) == len(phases):
                showRewardScreenWindow({'screenType': RewardScreenViewModel.TYPE_SHOW_CREW}, None, useQueue=True)
        return
