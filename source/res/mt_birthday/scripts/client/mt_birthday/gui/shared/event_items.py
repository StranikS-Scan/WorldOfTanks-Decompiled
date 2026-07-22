# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/shared/event_items.py
import constants
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import QuestPostBattleInfo
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.event_items import Quest, IQuestBuilder
from mt_birthday.birthday_constants import isBirthdayQuestGiverQuest
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import TabId
from mt_birthday.gui.shared.event_dispatcher import showMainView

class _BirthdayQuestGiverPostBattleInfo(QuestPostBattleInfo):

    def _getProgresses(self, pCur, pPrev):
        progresses = super(_BirthdayQuestGiverPostBattleInfo, self)._getProgresses(pCur, pPrev)
        if len(progresses) == 1:
            progresses[0]['description'] = self.event.getDescription()
        return progresses

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData=None):
        info = super(_BirthdayQuestGiverPostBattleInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData)
        if info:
            info['questInfo'].update({'linkTooltip': backport.text(R.strings.mt_birthday.quests.linkBtn.birthdayQuestGiver())})
        return info


class BirthdayQuestGiverQuest(Quest):

    @classmethod
    def postBattleInfo(cls):
        return _BirthdayQuestGiverPostBattleInfo

    @classmethod
    def showMissionAction(cls):
        return showMainView(tabId=TabId.QUESTS)


class BirthdayQuestGiverQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.BATTLE_QUEST and isBirthdayQuestGiverQuest(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return BirthdayQuestGiverQuest(qID, data, progress)
