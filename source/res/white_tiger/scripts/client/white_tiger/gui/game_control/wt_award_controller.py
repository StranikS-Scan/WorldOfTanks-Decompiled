# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/wt_award_controller.py
from gui.game_control.AwardController import ServiceChannelHandler
from gui.server_events.bonuses import VehiclesBonus, CrystalBonus, WtCustomizationsBonus, PlusPremiumDaysBonus, WtTmanTemplateTokensBonus
from helpers import dependency
import types
import ArenaType
from constants import ARENA_BONUS_TYPE
from gui.DialogsInterface import showPunishmentDialog
from skeletons.gui.game_control import IWhiteTigerController
from gui.impl.gen import R
from gui.impl import backport
from chat_shared import SYS_MESSAGE_TYPE
from gui.wt_event.wt_event_helpers import hasWTEventQuest, isWtEventSpecialQuest
from gui.wt_event.wt_event_helpers import isWTEventProgressionQuest
from gui.shared.event_dispatcher import showWtEventAwardWindow, showWtEventSpecialAwardWindow
from gui import SystemMessages
from gui.shared.notifications import NotificationPriorityLevel
from gui import makeHtmlString

class WtEventQuestAwardHandler(ServiceChannelHandler):
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)
    __STR_RES = R.strings.white_tiger.notifications.progression

    def __init__(self, awardCtrl):
        super(WtEventQuestAwardHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        if not self.__gameEventCtrl.isModeActive():
            return False
        else:
            _, message = ctx
            if message is not None and message.data and isinstance(message.data, types.DictType):
                if hasWTEventQuest(message.data.get('completedQuestIDs', set())):
                    return True
            return False

    def _showAward(self, ctx):
        _, message = ctx
        for questId in message.data.get('completedQuestIDs', set()):
            if isWTEventProgressionQuest(questId):
                self.__showProgressionCompletedMessage(questId)
                showWtEventAwardWindow(questId)
            if isWtEventSpecialQuest(questId):
                detailedReward = message.data.get('detailedRewards', {})
                questData = detailedReward.get(questId, None)
                showWtEventSpecialAwardWindow(questId=questId, questData=questData)

        return

    def __showProgressionCompletedMessage(self, questId):
        stageIdx = self.__getStageIdx(questId)
        if stageIdx == -1:
            return None
        else:
            rewards = self.__getRewards(questId)
            if stageIdx == len(self.__gameEventCtrl.getConfig().progression) - 1:
                SystemMessages.pushMessage(text=backport.text(self.__STR_RES.completed(), rewards=rewards), type=SystemMessages.SM_TYPE.WTEventProgression, priority=NotificationPriorityLevel.HIGH)
            else:
                SystemMessages.pushMessage(text=backport.text(self.__STR_RES.stageAchieved(), stageIdx=str(stageIdx + 1), rewards=rewards), type=SystemMessages.SM_TYPE.WTEventProgression, priority=NotificationPriorityLevel.MEDIUM)
            return None

    def __getStageIdx(self, questID):
        progression = self.__gameEventCtrl.getConfig().progression
        for idx, stage in enumerate(progression):
            if questID == stage['quest']:
                return idx

    def __getRewards(self, questID):
        rewards = self.__gameEventCtrl.getQuestRewards(questID)
        formattedList = []
        predicate = backport.text(self.__STR_RES.rewardAdded())
        for reward in rewards:
            if isinstance(reward, VehiclesBonus):
                formattedList.extend(self.__formatVehicleBonus(reward))
            if isinstance(reward, CrystalBonus):
                formattedList.extend(self.__formatCrystalbonus(reward, predicate))
            if isinstance(reward, WtCustomizationsBonus):
                formattedList.extend(self.__formatCustomizationBonus(reward))
            if isinstance(reward, PlusPremiumDaysBonus):
                formattedList.extend(self.__formatPremiumPlusBonus(reward))
            if isinstance(reward, WtTmanTemplateTokensBonus):
                formattedList.extend(self.__formatTmanTokenBonus(reward))
            for item in reward.formattedList():
                formattedList.append(predicate + ' ' + item)

        return '{0}'.format('\n'.join(formattedList))

    def __formatVehicleBonus(self, reward):
        formattedList = []
        for item, vehInfo in reward.getVehicles():
            if reward.isRentVehicle(vehInfo):
                vehName = makeHtmlString('html_templates:lobby/quests/bonuses', 'rentVehicle', {'name': item.userName})
                formatted = backport.text(self.__STR_RES.rentVehicleReceived(), vehName=vehName, count=reward.getRentBattles(vehInfo), crew=reward.getTmanRoleLevel(vehInfo))
                formattedList.append(formatted)

        return formattedList

    def __formatCrystalbonus(self, reward, predicate=''):
        formattedValue = reward.formatValue()
        if reward.getName() is not None and formattedValue is not None:
            text = makeHtmlString('html_templates:lobby/quests/bonuses', 'wtCrystal', {'value': formattedValue})
            if text != reward.getName():
                return [predicate + text]
        return [formattedValue]

    def __formatCustomizationBonus(self, reward):
        return reward.formattedList()

    def __formatTmanTokenBonus(self, reward):
        return reward.formattedList()

    def __formatPremiumPlusBonus(self, reward):
        formattedValue = reward.formatValue()
        if reward.getName() is not None and formattedValue is not None:
            text = makeHtmlString('html_templates:lobby/quests/bonuses', 'wtPremiumPlus', {'value': formattedValue})
            if text != reward.getName():
                return [text]
        return [formattedValue]


class WtPunishWindowHandler(ServiceChannelHandler):
    EXCLUDED_ARENA_BONUS_TYPES = [ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD]

    def __init__(self, awardCtrl):
        super(WtPunishWindowHandler, self).__init__(SYS_MESSAGE_TYPE.whiteTigerBattleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        arenaTypeID = message.data.get('arenaTypeID', 0)
        if arenaTypeID > 0 and arenaTypeID in ArenaType.g_cache:
            arenaType = ArenaType.g_cache[arenaTypeID]
        else:
            arenaType = None
        arenaCreateTime = message.data.get('arenaCreateTime', None)
        fairplayViolations = message.data.get('fairplayViolations', None)
        bonusType = message.data.get('bonusType')
        if arenaCreateTime and arenaType and bonusType not in self.EXCLUDED_ARENA_BONUS_TYPES and fairplayViolations is not None and fairplayViolations[:2] != (0, 0):
            banDuration = message.data['restriction'][1] if 'restriction' in message.data else None
            showPunishmentDialog(arenaType, arenaCreateTime, fairplayViolations, banDuration)
        return
