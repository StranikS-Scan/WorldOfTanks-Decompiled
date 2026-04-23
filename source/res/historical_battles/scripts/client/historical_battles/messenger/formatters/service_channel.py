# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/messenger/formatters/service_channel.py
import itertools
import BigWorld
from debug_utils import LOG_ERROR, LOG_WARNING
from dossiers2.ui.achievements import BADGES_BLOCK
from gui.shared.notifications import NotificationPriorityLevel
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
from gui.shared.formatters.currency import getBWFormatter, getStyle
from gui.shared.formatters import text_styles
from gui.server_events.recruit_helper import getRecruitInfo
from helpers import dependency, int2roman
from items import vehicles
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, InvoiceReceivedFormatter, BattleResultsFormatter, QuestAchievesFormatter, ClientSysMessageFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import SyncTokenQuestsSubFormatter
from skeletons.gui.shared import IItemsCache
from historical_battles_common.hb_constants import FrontType
from historical_battles_common.helpers_common import getVehicleBonus, getFrontCouponModifier
from historical_battles_common.hb_constants import FRONT_COUPON_TOKEN_PREFIX
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.hb_constants import FrontsOpenStates
from historical_battles.notification.decorators import HBProgressionLockButtonDecorator

def _processTankmanToken(tokenName):
    if tokenName.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
        tankmanInfo = getRecruitInfo(tokenName)
        if tankmanInfo is not None:
            hbProgression = R.strings.historical_battles_progression
            text = backport.text(hbProgression.serviceChannelMessages.tankmanAward(), name=tankmanInfo.getFullUserName())
            return text
    return


def _getOrderType(multiplier):
    return 'x{}'.format(getFrontCouponModifier(multiplier))


def _formatVehicles(data):
    vehiclesToFormat = data.get('vehicles')
    if vehiclesToFormat and isinstance(vehiclesToFormat, dict):
        data['vehicles'] = [vehiclesToFormat]


def _formatCurrencyValue(currency, value, useStyle=True):
    bwFormatter = getBWFormatter(currency)
    fValue = bwFormatter(value)
    if useStyle:
        style = getStyle(currency)
        fValue = style(fValue)
    return fValue


class HBProgressionAchievesFormatter(QuestAchievesFormatter):
    _BULLET = u'\u2022 '
    _SEPARATOR = '<br/>'
    __itemsCache = dependency.descriptor(IItemsCache)
    __gameEventController = dependency.descriptor(IGameEventController)

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(HBProgressionAchievesFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return result

    @classmethod
    def formatSpecialRewards(cls, data):
        additionalAchievements = []
        discount = cls.__formatHBDiscount(data)
        if discount:
            additionalAchievements.append(discount)
        result = cls._SEPARATOR.join(additionalAchievements)
        return cls._SEPARATOR + result if result else result

    @classmethod
    def __formatHBDiscount(cls, data):
        discounts = []
        if cls.__gameEventController.heroTank.hasHeroVehicle():
            return discounts
        hbProgression = R.strings.historical_battles_progression
        tokens = data.get('tokens', {})
        mainDiscountConf = cls.__gameEventController.getMainDiscount()
        rewardVehicleName = cls.__gameEventController.heroTank.getVehicle().userName
        for tokenID in tokens.keys():
            if tokenID == mainDiscountConf['tokenName']:
                discountAward = backport.text(hbProgression.serviceChannelMessages.discountAward(), vehicle=text_styles.gold(rewardVehicleName))
                tokens = cls.__itemsCache.items.tokens
                hbDiscountTokensCount = min(tokens.getTokenCount(mainDiscountConf['tokenName']), mainDiscountConf['maxTokenCount'])
                discountAwardPercentage = backport.text(hbProgression.serviceChannelMessages.discountAwardPercentage(), discount=hbDiscountTokensCount * mainDiscountConf['discountPerToken'])
                discounts.append(discountAward + text_styles.gold(discountAwardPercentage))
                break

        return cls._SEPARATOR.join(discounts)

    @classmethod
    def __getVehicleNameByCD(cls, vehicleCD):
        vehicleItem = cls.__itemsCache.items.getItemByCD(vehicleCD)
        return vehicleItem.shortUserName

    @classmethod
    def _processTokens(cls, data):
        tokenStrings = []
        for tokenName in data.get('tokens', {}).keys():
            tankmanTokenResult = _processTankmanToken(tokenName)
            if tankmanTokenResult:
                tokenStrings.append(tankmanTokenResult)

        return cls._SEPARATOR.join(tokenStrings)


class HBProgressionSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'HistoricalBattlesProgressionSystemMessage'

    def __init__(self):
        super(HBProgressionSystemMessageFormatter, self).__init__()
        self._achievesFormatter = HBProgressionAchievesFormatter()

    def format(self, message, *args):
        return self._format(message, args)

    def _format(self, message, *_):
        messageData = message.data or {}
        results = messageData.get('stages', set())
        messageDataList = []
        for result in sorted(results, key=lambda result: result.get('stage', {})):
            messageDataList.append(self._formatSingleStageCompletion(message, result))

        return messageDataList

    def _formatSingleStageCompletion(self, message, stageInfo):
        decorator = HBProgressionLockButtonDecorator
        messageHeader = backport.text(R.strings.historical_battles_progression.serviceChannelMessages.header())
        stage = stageInfo.get('stage')
        frontId = stageInfo.get('frontId')
        frontName = FrontType(frontId).name.lower()
        modeName = backport.text(R.strings.historical_battles_progression.serviceChannelMessages.modeName.dyn(frontName)())
        progressionName = backport.text(R.strings.historical_battles_progression.serviceChannelMessages.progressionName())
        messageBody = backport.text(R.strings.historical_battles_progression.serviceChannelMessages.body(), stage=str(stage), modeName=modeName, progressionName=progressionName)
        rewardsData = stageInfo.get('detailedRewards', {})
        if not rewardsData:
            return None
        else:
            _formatVehicles(rewardsData)
            formattedSpecialRewards = self._achievesFormatter.formatSpecialRewards(rewardsData)
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False)
            if formattedSpecialRewards:
                formattedRewards += formattedSpecialRewards
            data = {'savedData': {'frontId': frontId}}
            return MessageData(g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': messageHeader,
             'body': messageBody,
             'awards': formattedRewards}, data=data), self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=NotificationPriorityLevel.MEDIUM, decorator=decorator))


class HBBattleQuestsAchievesFormatter(QuestAchievesFormatter):
    _SEPARATOR = '<br/>'
    _ALLOWED_DOSSIER_BLOCKS = ('singleAchievements',)

    @classmethod
    def formatHBBattleQuestAchieves(cls, rewards):
        additionalAchievements = []
        dossier = cls.__formatDossier(rewards)
        if dossier:
            additionalAchievements.append(dossier)
        result = cls._SEPARATOR.join(additionalAchievements)
        return cls._SEPARATOR + result if result else result

    @classmethod
    def __formatDossier(cls, rewards):
        dossierData = rewards.get('dossier')
        if not dossierData:
            return ''
        dossierID = cls.__getDossierID(dossierData)
        return '' if not dossierID else g_settings.htmlTemplates.format('hbBattleQuestDossier', {'medal': backport.text(R.strings.achievements.dyn(dossierID)())})

    @classmethod
    def __getDossierID(cls, data):
        for rec in data.itervalues():
            for (block, name), _ in rec.iteritems():
                if block in cls._ALLOWED_DOSSIER_BLOCKS and name:
                    return name

        return None


class HBBattleQuestsSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'tokenQuests'
    __QUEST_PREFIX = 'hb26'

    def __init__(self):
        super(HBBattleQuestsSystemMessageFormatter, self).__init__()
        self._achievesFormatter = HBBattleQuestsAchievesFormatter()

    def format(self, message, auxData=None):
        data = message.data or {}
        completedQuestIDs = data.get('completedQuestIDs', set())
        detailedRewards = data.get('detailedRewards', {})
        targetQuests = [ qID for qID in completedQuestIDs if qID.startswith(self.__QUEST_PREFIX) ]
        if not targetQuests:
            return []
        formattedMessages = []
        for qID in targetQuests:
            rewards = detailedRewards.get(qID)
            if not rewards:
                continue
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
            formattedHBBattleQuestAchieves = self._achievesFormatter.formatHBBattleQuestAchieves(rewards)
            if formattedHBBattleQuestAchieves:
                formattedRewards += formattedHBBattleQuestAchieves
            if formattedRewards:
                formattedText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'achieves': formattedRewards})
                settings = self._getGuiSettings(message, self.__TEMPLATE)
                formattedMessages.append(MessageData(formattedText, settings))

        return formattedMessages


class HBBattleResultsFormatter(BattleResultsFormatter):
    _battleResultKeys = {-1: 'HBBattleDefeatResult',
     0: 'HBBattleDrawResult',
     1: 'HBBattleVictoryResult'}

    def _prepareFormatData(self, message):
        templateName, ctx = super(HBBattleResultsFormatter, self)._prepareFormatData(message)
        battleResults = message.data
        divisionID = battleResults['divisionID']
        hbCoins = battleResults['hbCoins']
        ctx['hbEventName'] = backport.text(R.strings.hb_lobby.system_messages.battleResults.event())
        frontId = battleResults.get('frontID', 0)
        frontName = FrontType(frontId).name.lower()
        ctx['modeName'] = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.modeName.dyn(frontName)())
        ctx['hbDivision'] = backport.text(R.strings.hb_lobby.system_messages.battleResults.division(), name=backport.text(R.strings.hb_lobby.dyn('division_{}'.format(divisionID)).name()))
        extraData = []
        if hbCoins:
            extraData.append(backport.text(R.strings.hb_lobby.system_messages.battleResults.coins.dyn(hbCoins['type'])(), amount=backport.getIntegralFormat(hbCoins['amount'])))
        ctx['hbExtraData'] = '<br/>'.join(extraData)
        return (templateName, ctx)

    @staticmethod
    def __getBadgeIdFromResult(battleResults, questID):
        dossiers = battleResults['detailedRewards'][questID]['dossier']
        for rec in dossiers.itervalues():
            for (block, name), _ in rec.iteritems():
                if block == BADGES_BLOCK and name != '':
                    return name

        return None


class HBShopBundlePurchasedSysMessageFormatter(InvoiceReceivedFormatter):
    _MESSAGE_TEMPLATE = 'HBShopBundlePurchasedSysMessage'
    _MULTI_PRICE_ICON = 'multiPrice'
    _CURRENCY_TO_ICON = {Currency.GOLD: 'GoldIcon',
     Currency.CREDITS: 'CreditsIcon',
     'hb_coin_defence': 'historical_battles:defence',
     'hb_coin_counterattack': 'historical_battles:counterattack',
     'hb_coin_offence': 'historical_battles:offence',
     _MULTI_PRICE_ICON: 'historical_battles:multiPriceCoins'}

    def isAsync(self):
        return False

    @property
    def shop(self):
        return getattr(BigWorld.player(), 'HBShopAccountComponent', None)

    def format(self, message, *args):
        bundleID = message.data['bundleID']
        count = message.data['count']
        bundle = self.shop.getBundle(bundleID)
        operations = self._formatBundleName(bundle)
        operations += self._composeOperations(message.data)
        operations += self._formatBundleTokens(bundle, count)
        operations += self._formatWithdrawnMoney(bundle.prices, count)
        settings = self._getGuiSettings(message, self._MESSAGE_TEMPLATE)
        formatted = g_settings.msgTemplates.format(self._MESSAGE_TEMPLATE, {'op': '<br/>'.join(operations)}, data={'icon': self._getMessageIcon(bundle)})
        return [MessageData(formatted, settings)]

    def _getMessageIcon(self, bundle):
        key = self._MULTI_PRICE_ICON if len(bundle.prices) > 1 else bundle.prices[0].currency
        return self._CURRENCY_TO_ICON.get(key, '')

    def _formatBundleName(self, bundle):
        resource = R.strings.hb_shop.bundles.dyn(bundle.id).dyn('systemMessage').dyn('purchased')
        return [g_settings.htmlTemplates.format('hbShopBundleSimpleText', {'text': backport.text(resource())})] if resource.exists() else []

    def _formatBundleTokens(self, bundle, purchasesCount):
        result = []
        for name, record in self._getTokensIter(bundle.bonuses):
            tokenFormatter = self._getTokenFormatter(name)
            if tokenFormatter is not None:
                result.append(tokenFormatter(record, bundle, purchasesCount))

        return result

    def _getTokensIter(self, bonuses):
        return itertools.chain.from_iterable((b.getTokens().iteritems() for b in bonuses if b.getName() == 'HBCoupon'))

    def _getTokenFormatter(self, tokenID):
        return None

    def _formatWithdrawnMoney(self, prices, count):
        return [ g_settings.htmlTemplates.format('hbShopBundleSimpleText', {'text': backport.text(R.strings.hb_shop.systemMessage.moneySpent(), text=backport.text(R.strings.hb_shop.systemMessage.moneySpent.dyn(subPrice.currency)(), amount=getBWFormatter(subPrice.currency)(subPrice.amount * count)))}) for subPrice in prices ]


class HBCouponsBundlePurchasedSysMessageFormatter(HBShopBundlePurchasedSysMessageFormatter):
    _MESSAGE_TEMPLATE = 'HBCouponsBundlePurchasedSysMessage'
    _R = R.strings.hb_shop.systemMessage.bundleOrders

    def _getTokenFormatter(self, _):
        return self._formatFrontCouponsToken

    @classmethod
    def _formatFrontCouponsToken(cls, tokenRecord, bundle, purchasesCount):
        isGift = bundle.prices[0].currency == Currency.GOLD
        orderType = ''
        if tokenRecord.id.startswith(FRONT_COUPON_TOKEN_PREFIX):
            orderType = _getOrderType(tokenRecord.id)
        else:
            LOG_ERROR('Failed conversion {0} to orderType'.format(tokenRecord.id))
        return g_settings.htmlTemplates.format('hbShopBundleSimpleText', {'text': backport.text(cls._R.gift() if isGift else cls._R.purchase(), orderType=orderType, count=tokenRecord.count * purchasesCount)})


class HBTankModuleBundlePurchasedSysMessageFormatter(HBShopBundlePurchasedSysMessageFormatter):
    MAIN_PRIZE_VEHICLE_BUNDLE_ID = 'hb22BundleMainPrizeVehicle'

    def _formatBundleName(self, bundle):
        mainPrizeBundle = self.shop.getBundle(self.MAIN_PRIZE_VEHICLE_BUNDLE_ID)
        bundleBonuses = self.shop.getBundleBonusesWithQuests(mainPrizeBundle)
        vehicleBonus = getVehicleBonus(bundleBonuses)
        if vehicleBonus is None:
            return []
        else:
            self.__mainPrizeVehicleName = vehicleBonus.userName
            resource = R.strings.hb_shop.bundles.dyn(bundle.id).dyn('systemMessage').dyn('purchased')
            return [g_settings.htmlTemplates.format('hbShopBundleSimpleText', {'text': backport.text(resource(), vehName=self.__mainPrizeVehicleName)})] if resource.exists() else []


class MainPrizeVehicleBundlePurchased(ServiceChannelFormatter):
    _MESSAGE_TEMPLATE = 'HBMainPrizeVehicleBundlePurchased'
    _R_MAIN_PRIZE = R.strings.hb_shop.systemMessage.mainPrize
    _CURRENCIES_ORDER = [Currency.CREDITS, Currency.GOLD]

    def format(self, message, *args):
        if not message.data:
            return []
        moneySpent = message.data.get('moneySpent')
        vehTypeIntCD = message.data.get('vehTypeIntCD')
        isGift = not moneySpent or not moneySpent.get(Currency.GOLD, 0)
        vehDescr = vehicles.VehicleDescr(typeID=vehicles.parseIntCompactDescr(vehTypeIntCD)[1:])
        messageLines = []
        vehResourse = self._R_MAIN_PRIZE.giftVehicle if isGift else self._R_MAIN_PRIZE.vehicle
        messageLines.append(g_settings.htmlTemplates.format('hbShopBundleSimpleText', {'text': backport.text(vehResourse(), vehName=vehDescr.type.userString)}))
        if isGift:
            messageLines.append(g_settings.htmlTemplates.format('hbShopBundleSimpleText', {'text': backport.text(self._R_MAIN_PRIZE.slot())}))
        if moneySpent:
            money = [ backport.text(R.strings.hb_shop.systemMessage.moneySpent.dyn(currency)(), amount=getBWFormatter(currency)(moneySpent[currency])) for currency in self._CURRENCIES_ORDER if currency in moneySpent and moneySpent[currency] != 0 ]
            if money:
                messageLines.append(g_settings.htmlTemplates.format('hbShopBundleSimpleText', {'text': backport.text(R.strings.hb_shop.systemMessage.moneySpent(), text=', '.join(money))}))
        settings = self._getGuiSettings(message, self._MESSAGE_TEMPLATE)
        formatted = g_settings.msgTemplates.format(self._MESSAGE_TEMPLATE, {'op': '<br/>'.join(messageLines)})
        return [MessageData(formatted, settings)]


class HBMainVehiclePrizeMessageFormatter(SyncTokenQuestsSubFormatter):
    __TEMPLATE = 'HBMainVehiclePrizeQuest'
    __QUEST_ID = 'hbMainVehiclePrize'

    def __init__(self):
        super(HBMainVehiclePrizeMessageFormatter, self).__init__()
        self._achievesFormatter = HBProgressionAchievesFormatter()

    def format(self, message, *args):
        messageHeader = backport.text(R.strings.historical_battles_progression.serviceChannelMessages.header())
        rewards = getRewardsForQuests(message, (self.__QUEST_ID,))
        _formatVehicles(rewards)
        formatted = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if not formatted:
            return []
        formattedText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': messageHeader,
         'rewards': formatted})
        return [MessageData(formattedText, self._getGuiSettings(message.data, self.__TEMPLATE))]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID == cls.__QUEST_ID


class HBMainVehiclePrizeCompensationMessageFormatter(SyncTokenQuestsSubFormatter):
    __TEMPLATE = 'HBMainVehiclePrizeCompensation'
    __QUEST_ID = 'hbMainVehiclePrizeCompensation'
    __gameEventController = dependency.descriptor(IGameEventController)

    def format(self, message, *args):
        messageHeader = backport.text(R.strings.historical_battles_progression.serviceChannelMessages.compensation.title())
        rewards = getRewardsForQuests(message, (self.__QUEST_ID,))
        formatted = self._formatDiscountCompensation(rewards)
        if not formatted:
            return []
        formattedText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': messageHeader,
         'rewards': formatted})
        return [MessageData(formattedText, self._getGuiSettings(message.data, self.__TEMPLATE))]

    def _formatDiscountCompensation(self, rewards):
        currency = next(itertools.ifilter(lambda c: c in rewards, ['gold', 'credits']), None)
        amount = rewards.get(currency)
        if not amount:
            return ''
        else:
            rewardVehicle = self.__gameEventController.heroTank.getVehicle()
            resource = R.strings.historical_battles_progression.serviceChannelMessages.compensation
            bodyText = backport.text(resource.body(), vehicleLvl=int2roman(rewardVehicle.level), vehicleName=rewardVehicle.userName, compensationAmount=_formatCurrencyValue(currency, amount))
            return bodyText

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID == cls.__QUEST_ID


class HBArenaBanSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'HistoricalBattlesArenaBanSystemMessage'

    def canBeEmpty(self):
        return True

    def format(self, data, *args):
        messageDataList = []
        messageDataList.append(self._formatSingleStageCompletion(data))
        return messageDataList

    def _formatSingleStageCompletion(self, data):
        isStarted = data.get('isStarted', False)
        if isStarted:
            header = backport.text(R.strings.hb_lobby.sysMessageFairPlayMsg.arenaBanStart.header())
            body = backport.text(R.strings.hb_lobby.sysMessageFairPlayMsg.arenaBanStart.body())
            icon = 'hbBanIcon'
        else:
            header = backport.text(R.strings.hb_lobby.sysMessageFairPlayMsg.arenaBanStop.header())
            body = backport.text(R.strings.hb_lobby.sysMessageFairPlayMsg.arenaBanStop.body())
            icon = 'InformationIcon'
        data = {'savedData': {'isStarted': isStarted,
                       'reason': data.get('reason', ''),
                       'duration': data.get('duration', 0),
                       'banExpiryTime': data.get('banExpiryTime', 0)},
         'icon': icon}
        return MessageData(g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': header,
         'body': body}, data=data), self._getGuiSettings(data, self.__TEMPLATE))


class HBArenaWarningSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'HistoricalBattlesArenaWarningSystemMessage'

    def canBeEmpty(self):
        return True

    def format(self, data, *args):
        messageDataList = []
        messageDataList.append(self._formatSingleStageCompletion(data))
        return messageDataList

    def _formatSingleStageCompletion(self, data):
        header = backport.text(R.strings.hb_lobby.sysMessageFairPlayMsg.arenaWarning.header())
        body = backport.text(R.strings.hb_lobby.sysMessageFairPlayMsg.arenaWarning.body())
        data = {'savedData': {'reason': data.get('reason', ''),
                       'duration': data.get('duration', 0),
                       'banExpiryTime': data.get('banExpiryTime', 0)}}
        return MessageData(g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': header,
         'body': body}, data=data), self._getGuiSettings(data, self.__TEMPLATE))


class HBStateMessageFormatter(ServiceChannelFormatter):
    __TEMPLATES_MAP = {FrontsOpenStates.EVENT_STARTED: 'HBStartedMessage',
     FrontsOpenStates.EVENT_ENDED: 'HBEndedMessage'}

    def format(self, message, *args):
        template = self.__TEMPLATES_MAP.get(args[0])
        formatted = g_settings.msgTemplates.format(template)
        return [MessageData(formatted, self._getGuiSettings(message, template))]


class HBDivisionLevelUpSysMessageFormatter(ClientSysMessageFormatter):
    _R_ABILITIES = R.strings.messenger.serviceChannelMessages.division.abilitiesUnlocked

    def format(self, data, *args):
        divisionName = data['divisionName']
        divisionLevel = data['divisionLevel']
        divisionVehicles = data['divisionVehicles']
        unlockedAbilities = data['unlockedAbilities']
        messageLines = [self.__formatDivisionNameAndLevel(divisionName, divisionLevel), self.__formatUnlockedVehicles(divisionVehicles), self.__formatUnlockedAbilities(unlockedAbilities)]
        settings = self._getGuiSettings(data, 'HBDivisionLevelUpSystemMessage')
        formatted = g_settings.msgTemplates.format('HBDivisionLevelUpSystemMessage', {'op': '<br/>'.join(messageLines)})
        return [MessageData(formatted, settings)]

    @staticmethod
    def __formatDivisionNameAndLevel(divisionName, divisionLevel):
        return g_settings.htmlTemplates.format('hbDivisionNameAndLevel', {'text': backport.text(R.strings.messenger.serviceChannelMessages.division.levelUp(), division_name=divisionName, division_level=int2roman(divisionLevel))})

    @staticmethod
    def __formatUnlockedVehicles(divisionVehicles):
        divisionVehicles = ', '.join((str(vehicle) for vehicle in divisionVehicles))
        return g_settings.htmlTemplates.format('hbDivisionLevelUpUnlockedVehicles', {'vehicles': divisionVehicles})

    def __formatUnlockedAbilities(self, unlockedAbilities):
        abilitiesMessage = self._R_ABILITIES.plural() if len(unlockedAbilities) > 1 else self._R_ABILITIES()
        unlockedAbilities = ', '.join((str(ability) for ability in unlockedAbilities))
        return g_settings.htmlTemplates.format('hbDivisionLevelUpUnlockedAbilities', {'abilitiesMessage': backport.text(abilitiesMessage),
         'abilities': unlockedAbilities})


class HBDivisionUpgradePurchasedSysMessageFormatter(ClientSysMessageFormatter):

    def format(self, message, *args):
        price = message.data['price']
        currency = message.data['currency']
        textRes = R.strings.messenger.serviceChannelMessages.division.upgrade.financial_success.dyn(currency)()
        text = backport.text(textRes)
        messageLine = g_settings.htmlTemplates.format('hbDivisionUpgradeFinancialSuccess', {'text': text,
         'price': _formatCurrencyValue(currency, price)})
        settings = self._getGuiSettings(message.data, 'HBDivisionUpgradeFinancialSuccessSystemMessage')
        formatted = g_settings.msgTemplates.format('HBDivisionUpgradeFinancialSuccessSystemMessage', {'op': messageLine})
        return [MessageData(formatted, settings)]


class HBOrderInvoiceSysMessageFormatter(ClientSysMessageFormatter):

    def format(self, message, *args):
        tokens = message.data
        orders = {}
        for tokenName, tokenValue in tokens.iteritems():
            if tokenName.startswith(FRONT_COUPON_TOKEN_PREFIX):
                orders[tokenName] = tokenValue['count']

        if not orders:
            LOG_WARNING('Formatting order invoice message, but there is no orders')
            return []
        messageLines = []
        for orderId, count in orders.iteritems():
            messageLines.append(g_settings.htmlTemplates.format('hbOrderSimpleText', {'text': backport.text(R.strings.messenger.serviceChannelMessages.orders.invoice(), orderType=_getOrderType(orderId), count=count)}))

        settings = self._getGuiSettings(message.data, 'HBOrderInvoiceSystemMessage')
        formatted = g_settings.msgTemplates.format('HBOrderInvoiceSystemMessage', {'op': '<br/>'.join(messageLines)})
        return [MessageData(formatted, settings)]
