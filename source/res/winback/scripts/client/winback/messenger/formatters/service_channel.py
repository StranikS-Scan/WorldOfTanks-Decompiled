# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/messenger/formatters/service_channel.py
from copy import deepcopy
from itertools import chain
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.server_events.recruit_helper import _getRecruitInfoFromToken
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData
from helpers import dependency, int2roman
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.game_control import IWinbackController
from winback.gui.impl.lobby.winback_helpers import getLevelFromSelectableToken, getDiscountFromGoody, getDiscountFromBlueprint
from winback.gui.selectable_reward.selectable_reward_manager import WinbackSelectableRewardManager
from winback.notification.decorators import WinbackProgressionLockButtonDecorator

class WinbackQuestAchievesFormatter(QuestAchievesFormatter):

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        rewards = deepcopy(data)
        discounts = cls._formatDiscounts(rewards)
        result = super(WinbackQuestAchievesFormatter, cls).formatQuestAchieves(rewards, asBattleFormatter, processCustomizations, processTokens)
        if discounts is None:
            return result
        else:
            return discounts if result is None else cls._SEPARATOR.join((result, discounts))

    @classmethod
    def _formatDiscounts(cls, rewards):
        from winback.gui.impl.lobby.views.winback_bonus_packer import handleWinbackDiscounts, cutVehDiscountsFromBonuses
        discountsRes = R.strings.winback.serviceChannelMessages.awards
        results = []
        if 'blueprints' in rewards or 'goodies' in rewards:
            rewards, winbackRewards = cutVehDiscountsFromBonuses(rewards, received=True)
            winbackBonuses = handleWinbackDiscounts(winbackRewards)
            for bonus in winbackBonuses:
                for cd in bonus.getVehicleCDs():
                    vehicle = bonus.getVehicle(cd)
                    goodyID, blueprintCount = bonus.getResources(cd)
                    results.append(text_styles.rewards(backport.text(discountsRes.discountConcrete(), name=vehicle.userName, creditDiscount=getDiscountFromGoody(goodyID)[0], expDiscount=int(getDiscountFromBlueprint(cd, blueprintCount)))))

            if winbackBonuses:
                return backport.text(discountsRes.discountHeader()) + ', '.join(results)
        return None


class WinbackSelectedAward(ServiceChannelFormatter):
    __TEMPLATE = 'WinbackSelectedAward'

    def format(self, message, *args):
        achieves = WinbackQuestAchievesFormatter.formatQuestAchieves(message, asBattleFormatter=False)
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'achieves': achieves})
        settings = self._getGuiSettings(message, self.__TEMPLATE)
        return [MessageData(formatted, settings)]


class WinbackProgressionAchievesFormatter(QuestAchievesFormatter):
    __winbackController = dependency.descriptor(IWinbackController)
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    @classmethod
    def getFormattedAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        rewards = deepcopy(data)
        tokenResult = cls._preprocessTokens(rewards.get('tokens', {})) if processTokens else None
        boostersResult = cls._preprocessBoosters(rewards.get('goodies', {}))
        results = super(WinbackProgressionAchievesFormatter, cls).getFormattedAchieves(rewards, asBattleFormatter, processCustomizations, processTokens)
        if boostersResult:
            results.append(boostersResult)
        if tokenResult:
            results.append(tokenResult)
        return results

    @classmethod
    def _preprocessBoosters(cls, goodies):
        boostersStrings = []
        for goodieID, gInfo in goodies.items():
            booster = cls.__goodiesCache.getBooster(goodieID)
            if booster is not None and booster.enabled:
                del goodies[goodieID]
                if gInfo.get('count'):
                    boostersStrings.append(backport.text(R.strings.system_messages.bonuses.booster.value(), name=booster.userName, count=gInfo.get('count')))
                else:
                    boostersStrings.append(booster.userName)

        return g_settings.htmlTemplates.format('winbackBoostersInvoiceReceived', ctx={'boosters': ', '.join(boostersStrings)}) if boostersStrings else None

    @classmethod
    def _preprocessTokens(cls, tokens):
        tankmenResult = []
        selectableBonuses = []
        for tokenID in tokens.keys():
            tankmanTokenResult = cls._processTankmanToken(tokenID, tokens[tokenID].get('count', 1))
            if tankmanTokenResult:
                tankmenResult.append(tankmanTokenResult)
                del tokens[tokenID]
            if cls.__winbackController.isWinbackOfferToken(tokenID):
                selectableBonusTokenResult = cls._processSelectableBonusToken(tokenID)
                if selectableBonusTokenResult[1]:
                    selectableBonuses.append(selectableBonusTokenResult)
                del tokens[tokenID]

        selectableBonuses.sort()
        return cls._SEPARATOR.join(chain(tankmenResult, (result for level, result in selectableBonuses)))

    @staticmethod
    def _processTankmanToken(tokenID, count):
        tankmanInfo = _getRecruitInfoFromToken(tokenID)
        return g_settings.htmlTemplates.format('winbackTankman', {'name': tankmanInfo.getFullUserName() if tankmanInfo.getLastName() else tankmanInfo.getFirstName(),
         'count': count}) if tankmanInfo is not None else None

    @staticmethod
    def _processSelectableBonusToken(tokenID):
        compensationTemplateSuffix = ''
        compensationValue = 0
        if WinbackSelectableRewardManager.isOfferCompensated(tokenID):
            compensationTemplateSuffix = 'Compensation'
            compensationValue = WinbackSelectableRewardManager.createCompensationBonusFromOffer(tokenID).getCount()
        level = int(getLevelFromSelectableToken(tokenID))
        selectableType = WinbackSelectableRewardManager.getSelectableBonusName(tokenID)
        formattedResult = g_settings.htmlTemplates.format(''.join(['winback', selectableType, compensationTemplateSuffix]), ctx={'level': int2roman(level),
         'value': compensationValue})
        return (level, formattedResult)


class WinbackProgressionSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE_BASE = 'ProgressionSystemMessage'
    __TEMPLATE_SIMPLE = 'winbackProgressionSystemMessage'
    __winbackController = dependency.descriptor(IWinbackController)

    def format(self, message, *args):
        return self._format(message, args)

    def _format(self, message, *args):
        messageData = message.data or {}
        results = messageData.get('stages', set())
        messageDataList = []
        for result in sorted(results, key=lambda result: result.get('stage', {})):
            messageDataList.append(self._formatSingleStageCompletion(message, result))

        return messageDataList

    def _selectButtonTemplate(self, data):
        tokens = data.get('tokens', {})
        for tokenID in tokens.keys():
            if self.__winbackController.isWinbackOfferToken(tokenID):
                giftSuffix = '_gift'
                if tokenID.endswith(giftSuffix):
                    tokenID = tokenID[:-len(giftSuffix)]
                if WinbackSelectableRewardManager.isOfferCompensated(tokenID):
                    tokens[tokenID] = tokens.pop(tokenID + giftSuffix)
                    continue
                return 'SelectRewardButton'

    def _getTemplate(self, data):
        return ''.join(['VersusAI',
         self.__winbackController.progressionName,
         self.__TEMPLATE_BASE,
         self._selectButtonTemplate(data)])

    def _formatSingleStageCompletion(self, message, stageInfo):
        decorator = WinbackProgressionLockButtonDecorator
        messageHeader = backport.text(R.strings.winback.serviceChannelMessages.header())
        stage = stageInfo.get('stage')
        progressionName = backport.text(R.strings.winback.serviceChannelMessages.progressionName.dyn(self.__winbackController.progressionName)())
        messageBody = backport.text(R.strings.winback.serviceChannelMessages.progressionStage(), stage=str(stage), progressionName=progressionName)
        rewardsData = stageInfo.get('detailedRewards', {})
        if not rewardsData:
            return None
        else:
            template = self._getTemplate(rewardsData)
            formattedRewards = WinbackProgressionAchievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False)
            formattedMessage = g_settings.htmlTemplates.format(self.__TEMPLATE_SIMPLE, ctx={'header': messageHeader,
             'body': messageBody,
             'awards': formattedRewards})
            return MessageData(g_settings.msgTemplates.format(template, ctx={'message': formattedMessage}, data={}), self._getGuiSettings(message, template, decorator=decorator))
