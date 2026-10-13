# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/game_control/AwardController.py
from __future__ import absolute_import
import logging
from collections import OrderedDict
from chat_shared import SYS_MESSAGE_TYPE
from dossiers2.ui.achievements import BADGES_BLOCK
from fort_rush.gui.shared.event_dispatcher import showAwardWindow
from fort_rush.helpers.utils import isFREventProgressionQuest
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from gui import SystemMessages
from gui.game_control import AwardController
from gui.game_control.AwardController import MultiTypeServiceChannelHandler
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger.formatters.service_channel import QuestAchievesFormatter, _processTankmanToken
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.system_messages import ISystemMessages
_logger = logging.getLogger(__name__)

class _FortRushQuestAchievesFormatter(QuestAchievesFormatter):

    @classmethod
    def _processTokens(cls, data):
        result = []
        for tokenName in data.get('tokens', {}):
            tankmanTokenResult = _processTankmanToken(tokenName)
            if tankmanTokenResult:
                result.append(tankmanTokenResult)

        return cls._SEPARATOR.join(result)

    @classmethod
    def _extractAchievements(cls, data):
        result = super(_FortRushQuestAchievesFormatter, cls)._extractAchievements(data)
        for dossierRecord in data.get('dossier', {}).values():
            achievementEntries = dossierRecord if not isinstance(dossierRecord, dict) else dossierRecord.items()
            for (block, name), _ in achievementEntries:
                if block == BADGES_BLOCK or not name:
                    continue
                factory = getAchievementFactory((block, name))
                if factory is None:
                    continue
                achievement = factory.create(value=0)
                if achievement is not None:
                    result.add(achievement.getUserName())

        return result


class FortRushPunishWindowHandler(AwardController.PunishWindowHandler):

    @property
    def channelType(self):
        return SYS_MESSAGE_TYPE.fortRushBattleResults.index()


class FortRushAwardsController(MultiTypeServiceChannelHandler):
    __ctrl = dependency.descriptor(IFortRushBattleController)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __STR_RES = R.strings.fort_rush.notifications.progression

    def __init__(self, awardCtrl):
        handlers = {SYS_MESSAGE_TYPE.tokenQuests.index(), SYS_MESSAGE_TYPE.fortRushBattleResults.index()}
        super(FortRushAwardsController, self).__init__(handlers, awardCtrl)
        self.__completedQuestIds = []

    def _needToShowAward(self, ctx):
        if not super(FortRushAwardsController, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        rawIds = message.data.get('completedQuestIDs', set())
        self.__completedQuestIds = sorted(((self.__getStageIdx(questId), questId) for questId in rawIds if isFREventProgressionQuest(questId)))
        return len(self.__completedQuestIds) > 0

    def _showAward(self, ctx):
        for stageIdx, questId in self.__completedQuestIds:
            rewards = self.__ctrl.getProgressionRewards(questId)
            rewardData = OrderedDict()
            self.__updateReward(rewardData, rewards)
            self.__showStageCompletedMessage(stageIdx, self.__getRewards(rewardData, rewards))
            if rewardData:
                showAwardWindow(list(rewardData.items()))

        self.__completedQuestIds = []

    def __updateReward(self, rewardData, bonuses):
        for bonus in bonuses:
            rewardValue = bonus.getValue()
            dataKey = self.__getRewardDataKey(bonus)
            if dataKey is not None:
                BONUS_MERGERS[dataKey](rewardData, dataKey, rewardValue, False, 1, None)
            if isinstance(rewardValue, dict) and self.__ctrl.getConfig().completedProgressionToken in rewardValue:
                continue
            _logger.warning('Unknown reward in award screen. key: %s, value: %s', bonus.getName(), rewardValue)

        return

    @staticmethod
    def __getRewardDataKey(bonus):
        rewardKey = bonus.getName()
        if rewardKey in BONUS_MERGERS.keys():
            return rewardKey
        else:
            return 'tokens' if rewardKey == 'tmanToken' and isinstance(bonus.getValue(), dict) else None

    def __showStageCompletedMessage(self, stageIdx, rewards):
        SystemMessages.pushMessage(text=backport.text(self.__STR_RES.stageAchieved(), stageIdx=str(stageIdx + 1), rewards=rewards), type=SystemMessages.SM_TYPE.FREventProgression, priority=NotificationPriorityLevel.MEDIUM)

    def __getRewards(self, rewardData, rewards):
        formattedList = []
        seenKeys = set()
        for bonus in rewards:
            rewardKey = bonus.getName()
            if rewardKey == 'battlePassPoints':
                if rewardKey in seenKeys:
                    continue
                seenKeys.add(rewardKey)
                formattedList.extend(bonus.formattedList())
                continue
            dataKey = self.__getRewardDataKey(bonus)
            if dataKey is None or dataKey in seenKeys or dataKey not in rewardData:
                continue
            seenKeys.add(dataKey)
            formattedList.extend(_FortRushQuestAchievesFormatter.getFormattedAchieves({dataKey: rewardData[dataKey]}, asBattleFormatter=False))

        return ', '.join(formattedList)

    def __getStageIdx(self, questID):
        stages = self.__ctrl.getConfig().progression.stage
        for idx, stage in enumerate(stages):
            if questID == stage.quest:
                return idx
