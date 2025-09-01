# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/messenger/formatters/service_channel.py
import logging
from adisp import adisp_async, adisp_process
from constants import LOOTBOX_TOKEN_PREFIX
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import BattleResultsFormatter
from messenger.formatters.service_channel import WaitItemsSyncFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.server_events import IEventsCache
from soft_exception import SoftException
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger_common.wt_constants import WT_TEAMS
from white_tiger.gui.white_tiger_gui_constants import WT_QUEST_BOSS_GROUP_ID, HUNTER_QUEST_CHAINS
_logger = logging.getLogger(__name__)

class WTTicketTokenWithdrawnFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = 'wtTicketTokenWithdrawn'
    __economicsCtrl = dependency.descriptor(IEconomicsController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        data = message.data
        isSynced = yield self._waitForSyncItems()
        if isSynced and data:
            token = data['token']
            amountDelta = data['amount_delta']
            if amountDelta >= 0:
                raise SoftException('Unexpected ticket amount to withdraw')
            strRes = R.strings.white_tiger_lobby.notifications
            if token == self.__economicsCtrl.getTicketTokenName():
                text = backport.text(strRes.ticketToken.withdrawn.body(), ticketsCount=str(self.__economicsCtrl.getTicketCount()))
            elif token == self.__economicsCtrl.getQuickTicketTokenName():
                text = backport.text(strRes.quickBossTicketToken.withdrawn.body())
            else:
                raise SoftException('Unexpected ticket token')
            ctx = {'text': text,
             'description': ''}
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx=ctx)
            callback([MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))])
        else:
            callback([MessageData(None, None)])
        return


class WTBattleResultsFormatter(BattleResultsFormatter):
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    __eventsCache = dependency.descriptor(IEventsCache)
    _battleResultKeys = {-1: 'WTBattleResult',
     0: 'WTEBattleResult',
     1: 'WTBattleResult'}

    def _prepareFormatData(self, message):
        templateName, ctx = super(WTBattleResultsFormatter, self)._prepareFormatData(message)
        self.__fillWTSpecificCtx(message.data, ctx)
        return (templateName, ctx)

    def __fillWTSpecificCtx(self, battleResults, ctx):
        strRes = R.strings.white_tiger_lobby.notifications.battleResults
        mainResultName = 'victory' if battleResults.get('isWinner', -1) == 1 else 'defeat'
        ctx['mainResultName'] = backport.text(strRes.dyn(mainResultName).header())
        ctx['eventName'] = backport.text(strRes.eventName())
        team = battleResults.get('team', -1)
        if team == WT_TEAMS.BOSS_TEAM:
            teamName = backport.text(strRes.team.boss())
        elif team == WT_TEAMS.HUNTERS_TEAM:
            teamName = backport.text(strRes.team.hunters())
        else:
            teamName = ''
            _logger.warning('Unexpected team type: %r', team)
        ctx['teamName'] = teamName
        ctx['quests'] = ''
        completedQuestIDs = battleResults.get('completedQuestIDs', ())
        completedQuests = self.__eventsCache.getAllQuests(lambda q: q.getID() in completedQuestIDs)
        completedDailyQuestsCount = sum((1 for q in completedQuests.itervalues() if q.getGroupID() in HUNTER_QUEST_CHAINS or q.getGroupID() == WT_QUEST_BOSS_GROUP_ID))
        completedBattleQuests = {qname:quest for qname, quest in battleResults.get('detailedRewards', {}).items() if 'battle_quest' in qname}
        if completedDailyQuestsCount:
            ctx['quests'] = '<br>%s' % text_styles.main(backport.text(strRes.questCompleted(), questsCompleted=str(completedDailyQuestsCount)))
        ctx['stamps'] = ''
        ctx['lootboxes'] = ''
        lootboxesStrs = []
        earnedStampsCount = 0
        for _, quest in completedBattleQuests.items():
            tokens = quest.get('tokens', {})
            stampToken = self.__economicsCtrl.getStampTokenName()
            if stampToken in tokens:
                earnedStampsCount += tokens[stampToken].get('count', 0)
            for tID, tVal in tokens.items():
                if tID.startswith(LOOTBOX_TOKEN_PREFIX):
                    lootBox = self._itemsCache.items.tokens.getLootBoxByTokenID(tID)
                    if lootBox is not None:
                        lootboxesStrs.append(backport.text(strRes.lootboxes.wt_lootbox(), count=text_styles.expText(tVal.get('count', 0))))

        if earnedStampsCount > 0:
            ctx['stamps'] = '<br>%s' % text_styles.main(backport.text(strRes.stamp(), count=text_styles.expText(earnedStampsCount)))
        if lootboxesStrs:
            ctx['lootboxes'] = '<br>%s' % text_styles.main('<br>'.join(lootboxesStrs))
        return
