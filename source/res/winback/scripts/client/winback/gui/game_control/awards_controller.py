# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/game_control/awards_controller.py
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from chat_shared import SYS_MESSAGE_TYPE
from collections import OrderedDict
from goodies.goodie_constants import GOODIE_VARIETY, GOODIE_TARGET_TYPE
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.game_control.AwardController import ServiceChannelHandler, MultiTypeServiceChannelHandler
from gui.server_events.events_helpers import isDailyQuest, getIdxFromQuestID
from gui.server_events.bonuses import getMergedBonusesFromDicts, GoodiesBonus, VehiclesBonus
from gui.shared.system_factory import registerAwardControllerHandlers
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.system_messages import ISystemMessages
from soft_exception import SoftException
from winback.gui.gui_constants import SM_TYPE_WINBACK_PROGRESSION, SCH_CLIENT_MSG_TYPE
from winback.gui.shared.event_dispatcher import showAwardsView
from winback.gui.impl.lobby.views.winback_reward_view import WinbackRewardWindow

def _getMessage(ctx):
    _, message = ctx
    return message


class WinbackProgressionStageHandler(ServiceChannelHandler):
    __systemMessages = dependency.descriptor(ISystemMessages)
    _CLIENT_MSG_TYPE = SCH_CLIENT_MSG_TYPE.WINBACK_PROGRESSION_NOTIFICATIONS

    def __init__(self, awardCtrl):
        super(WinbackProgressionStageHandler, self).__init__(SYS_MESSAGE_TYPE.__getattr__(SM_TYPE_WINBACK_PROGRESSION).index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        stages = message.data.get('stages', set())
        for stage in stages:
            if stage.get('showAwardWindow', False):
                showAwardsView({'bonuses': stage['detailedRewards'],
                 'isOnlyDaily': False,
                 'selectedRewards': False,
                 'isLastWindow': stage['finishStage'],
                 'stageNumber': stage['stage']})

        self._showMessages(ctx)

    def _showMessages(self, ctx):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(_getMessage(ctx), self._CLIENT_MSG_TYPE)


class WinbackQuestHandler(MultiTypeServiceChannelHandler):
    __notificationMgr = dependency.descriptor(INotificationWindowController)
    __winbackController = dependency.descriptor(IWinbackController)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __systemMessages = dependency.descriptor(ISystemMessages)
    _MAX_COUNT_BONUSES = 4

    def __init__(self, awardCtrl):
        super(WinbackQuestHandler, self).__init__((SYS_MESSAGE_TYPE.tokenQuests.index(), SYS_MESSAGE_TYPE.battleResults.index()), awardCtrl)
        self.__quests = {}

    def _showAward(self, ctx):
        self._filterDaily()
        if not self.__quests:
            return
        quests = self.__quests
        isOnlyDaily = len(quests) == 1 and isDailyQuest(first(quests))
        splittedBonuses = self._splitBonuses()
        splittedBonusesLength = len(splittedBonuses)
        for bonusesIndex, bonuses in enumerate(splittedBonuses):
            fromIdx, toIdx = bonusesIndex * self._MAX_COUNT_BONUSES, (bonusesIndex + 1) * self._MAX_COUNT_BONUSES
            window = WinbackRewardWindow(ctx={'quests': quests.keys()[fromIdx:toIdx],
             'bonuses': bonuses,
             'isOnlyDaily': isOnlyDaily,
             'isLastWindow': bonusesIndex == splittedBonusesLength - 1})
            self.__notificationMgr.append(WindowNotificationCommand(window))

    def _filterDaily(self):
        allQuests = self.eventsCache.getAllQuests()
        unneccessaryQIDs = [ qID for qID in self.__quests if isDailyQuest(qID) and not self.isShowCongrats(allQuests.get(qID)) ]
        for qID in unneccessaryQIDs:
            self.__quests.pop(qID)

    def _needToShowAward(self, ctx):
        _, message = ctx
        return False if not super(WinbackQuestHandler, self)._needToShowAward(ctx) else bool(self.__checkWinbackQuests(message.data))

    def _splitBonuses(self):
        splittedBonuses = []
        quests = self.__quests
        questIDs = quests.keys()
        allBonusesList = []
        dailyBonuses = {}
        for questID in questIDs:
            if isDailyQuest(questID):
                dailyBonuses = quests[questID]
            allBonusesList.extend(self._getMainBonusesList(quests[questID]))

        bonusIndex = 0
        currentBlock = {}
        countTilMax = self._MAX_COUNT_BONUSES
        while bonusIndex < len(allBonusesList):
            if countTilMax == 0:
                splittedBonuses.append(currentBlock)
                currentBlock = {}
                countTilMax = self._MAX_COUNT_BONUSES
            currentBlock = getMergedBonusesFromDicts([currentBlock] + allBonusesList[bonusIndex:bonusIndex + countTilMax])
            bonusIndex += countTilMax
            countTilMax = self._MAX_COUNT_BONUSES - self._calculateMainBonuses(currentBlock)

        if currentBlock:
            splittedBonuses.append(currentBlock)
        if dailyBonuses:
            if splittedBonuses:
                splittedBonuses[-1] = getMergedBonusesFromDicts([splittedBonuses[-1], dailyBonuses])
            else:
                splittedBonuses.append(dailyBonuses)
        return splittedBonuses

    def _getMainBonusesList(self, bonuses):
        result = []
        for bonusName, bonusData in bonuses.items():
            if bonusName == 'premium_plus':
                result.append({'premium_plus': bonuses.get('premium_plus')})
            if bonusName == 'tokens':
                result += [ {'tokens': {tokenName: bonusData.get(tokenName)}} for tokenName in bonusData.keys() if self.__winbackController.isWinbackOfferToken(tokenName) ]
            if bonusName == VehiclesBonus.VEHICLES_BONUS:
                result += [ {VehiclesBonus.VEHICLES_BONUS: {vehicleCD: vehicleData}} for vehicleBlock in bonusData for vehicleCD, vehicleData in vehicleBlock.iteritems() if vehicleData.get('compensatedNumber', 0) <= 0 ]
            if bonusName == BlueprintBonusTypes.BLUEPRINTS:
                result += self._getDiscounts(bonuses)
            if bonusName == 'slots':
                result.append({bonusName: bonusData})

        return result

    def _getDiscounts(self, bonuses):
        result = []
        vehicleToResultIndex = {}
        blueprints = bonuses.get(BlueprintBonusTypes.BLUEPRINTS, {})
        for blueprintId in blueprints.keys():
            result.append({BlueprintBonusTypes.BLUEPRINTS: {blueprintId: blueprints.get(blueprintId)}})
            if getFragmentType(blueprintId) == BlueprintTypes.VEHICLE:
                vehicleToResultIndex[blueprintId] = len(result) - 1

        goodies = bonuses.get(GoodiesBonus.GOODIES, {})
        addedVehicles = vehicleToResultIndex.keys()
        for goodyId in goodies.keys():
            goody = self.__goodiesCache.getGoodieByID(goodyId)
            if goody.variety == GOODIE_VARIETY.DISCOUNT and goody.target and goody.target.targetType == GOODIE_TARGET_TYPE.ON_BUY_VEHICLE:
                targetValue = goody.target.targetValue
                if targetValue in addedVehicles:
                    result[vehicleToResultIndex[targetValue]][GoodiesBonus.GOODIES] = {goodyId: goodies.get(goodyId)}

        return result

    def _calculateMainBonuses(self, bonuses):
        result = 0
        for bonusName, bonusData in bonuses.items():
            if bonusName == 'premium_plus':
                result += 1
            if bonusName == 'tokens':
                offerTokens = [ token for token in bonusData.keys() if self.__winbackController.isWinbackOfferToken(token) ]
                result += len(offerTokens)
            if bonusName == VehiclesBonus.VEHICLES_BONUS:
                for vehicleBlock in bonusData:
                    result += len(vehicleBlock)

            if bonusName == BlueprintBonusTypes.BLUEPRINTS:
                result += len(bonusData)

        return result

    def __checkWinbackQuests(self, data):
        completedQuestIDs = data.get('completedQuestIDs', ())
        qIDs = [ qID for qID in completedQuestIDs if self.__winbackController.isWinbackQuest(qID) ]
        if qIDs:
            self.__quests = OrderedDict(sorted([ (qID, data.get('detailedRewards', {}).get(qID)) for qID in qIDs ], key=lambda item: getIdxFromQuestID(item[0])))
        return qIDs


def registerWinbackProgressionAwardController():
    try:
        SYS_MESSAGE_TYPE.__getattr__(SM_TYPE_WINBACK_PROGRESSION).index()
    except AttributeError:
        raise SoftException('No index for {attr} found. Use registerSystemMessagesTypes before')

    registerAwardControllerHandlers((WinbackProgressionStageHandler, WinbackQuestHandler))
