# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/messenger/formatters/service_channel.py
import types
from collections import defaultdict
import constants
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.notifications import NotificationGuiSettings
from messenger import g_settings
from messenger.formatters.service_channel import ClientSysMessageFormatter, IInvoiceDataSubFormatter, EOL, IQuestAchievesSubformatter
from messenger.formatters.service_channel_helpers import getCustomizationItemData
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year_common.items import collectibles
from new_year.ny_constants import TOY_COLLECTIONS
from new_year.gui.shared.ny_machine_helper import getMachineLootboxToken
from new_year.gui.shared.variadic_discount import VariadicDiscount
from new_year.notification.decorators import NyMessageButtonDecorator
from new_year_common.items.components.ny_constants import CurrentNYConstants, TOKEN_VARIADIC_DISCOUNT_PREFIX
from helpers import dependency
from new_year.skeletons.new_year import ITamagotchiDataProvider

class NewNYEventFormatter(ClientSysMessageFormatter):

    def _getGuiSettings(self, data, key=None, priorityLevel=None, groupID=None):
        if isinstance(data, types.TupleType) and data:
            auxData = data[0][:]
            if len(data[0]) > 1 and priorityLevel is None:
                priorityLevel = data[0][1]
        else:
            auxData = []
        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        if groupID is None:
            groupID = g_settings.msgTemplates.groupID(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel=priorityLevel, auxData=auxData, groupID=groupID, messageSubtype=SCH_CLIENT_MSG_TYPE.NY_EVENT_BUTTON_MESSAGE, decorator=NyMessageButtonDecorator)


class NewYearInvoiceDataSubformatter(IInvoiceDataSubFormatter):
    __dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def format(self, data, operations):
        newYearToys = NewYearInvoiceDataSubformatter.getNewYearToys(data)
        toysStr = self.getNYToysString(newYearToys)
        if toysStr:
            operations.append(toysStr)
        fillers = data.get(CurrentNYConstants.FILLERS, {})
        if fillers:
            strFillers = self.getNyFillersString(fillers)
            if strFillers:
                operations.append(strFillers)

    def customFormatPurchase(self, data):
        if 'ny26_tamagotchi' not in data.get('tags', ()):
            return
        self.__dataProvider.onMailRewards(data.get('data', {}))

    @staticmethod
    def getNewYearToys(data):
        return {k:data.get(k, {}) for k in TOY_COLLECTIONS}

    @classmethod
    def getNYToysString(cls, data):
        accrued = {}
        debited = {}
        result = []
        for year, toys in data.iteritems():
            toyCollection = collectibles.g_cache[year[:4]].toys
            for toyID, toyCount in toys.iteritems():
                toyDescr = toyCollection.get(toyID)
                if toyDescr:
                    toyType = toyDescr.type
                    operation = accrued if toyCount > 0 else debited
                    toyTypeCount = operation.setdefault(toyType, 0)
                    operation[toyType] = toyTypeCount + toyCount

        if accrued:
            result.append(cls.__packNYToys(accrued, 'nyToysAccruedInvoiceReceived'))
        if debited:
            result.append(cls.__packNYToys(debited, 'nyToysDebitedInvoiceReceived'))
        return EOL.join(result)

    @classmethod
    def getNyFillersString(cls, fillers):
        if fillers > 0:
            template = 'nyFillersAccruedInvoiceReceived'
        else:
            template = 'nyFillersDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {'amount': backport.getIntegralFormat(abs(fillers))})

    @staticmethod
    def __packNYToys(data, template):
        typesStrings = []
        for toyType, toyCount in data.iteritems():
            typeName = backport.text(R.strings.ny.decorationTypes.dyn(toyType)())
            if abs(toyCount) == 1:
                typesStrings.append(backport.text(R.strings.menu.quote(), string=typeName))
            typesStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.toyTypeWrapper(), name=typeName, count=abs(toyCount)))

        return g_settings.htmlTemplates.format(template, {'toysList': ', '.join(typesStrings)})


class NewYearQuestAchievesSubFormatter(IQuestAchievesSubformatter):

    @classmethod
    def format(cls, data, asBattleFormatter, result, processCustomizations=True, processTokens=True):
        nyBoxes = cls.__processNyBoxes(data)
        if nyBoxes:
            result.extend(nyBoxes)
        newYearTokenResult = cls._processNewYearTokens(data.get('tokens', {}))
        if newYearTokenResult:
            result.extend(newYearTokenResult)
        newYearToys = NewYearInvoiceDataSubformatter.getNewYearToys(data)
        toysStr = NewYearInvoiceDataSubformatter.getNYToysString(newYearToys)
        if toysStr:
            result.append(toysStr)
        fillers = data.get(CurrentNYConstants.FILLERS, {})
        if fillers:
            strFillers = NewYearInvoiceDataSubformatter.getNyFillersString(fillers)
            if strFillers:
                result.append(strFillers)

    @classmethod
    def _processNewYearTokens(cls, tokens):
        result = []
        for tokenID in sorted((tokenID for tokenID in tokens.iterkeys())):
            value = tokens[tokenID]
            if tokenID.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX):
                discount = VariadicDiscount(tokenID)
                result.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.variadicDiscount(), discount=discount.getDiscountValue(), level=discount.getTankLevel()))
            recruitInfo = getRecruitInfo(tokenID)
            if recruitInfo is not None:
                if recruitInfo.getSourceID().startswith('ny21woman'):
                    count = value['count']
                    result.append(g_settings.htmlTemplates.format('tankwoman', {'count': count}))
                elif recruitInfo.getSourceID().startswith('ny22men'):
                    name = recruitInfo.getFullUserName()
                    result.append(backport.text(R.strings.lootboxes.notification.ny22man(), name=name))

        return result

    @classmethod
    def __processNyBoxes(cls, data):
        lootBoxesCount = 0
        machineCoin = 0
        result = []
        for tokenName, tokenData in data.get('tokens', {}).iteritems():
            if tokenName == getMachineLootboxToken() and tokenData.get('count', 0) > 0:
                machineCoin += tokenData['count']
                continue
            if tokenName.startswith(constants.LOOTBOX_TOKEN_PREFIX) and tokenData.get('count', 0) > 0:
                lootBoxesCount += tokenData['count']

        if lootBoxesCount > 0:
            count = backport.getIntegralFormat(lootBoxesCount)
            text = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.nyBoxes(), count=count)
            result.append(g_settings.htmlTemplates.format('battleQuestsNYBoxes', {'text': text}))
        if machineCoin > 0:
            count = backport.getIntegralFormat(machineCoin)
            text = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.nyCoins(), count=count)
            result.append(g_settings.htmlTemplates.format('battleQuestsNYBoxes', {'text': text}))
        return result


class NewYearCollectionFormatter(object):

    @classmethod
    def formatAchieves(cls, data):
        customizations = data.get('customizations', [])
        rewards = defaultdict(lambda : defaultdict(int))
        for customizationItem in customizations:
            custType = customizationItem['custType']
            guiItemType, itemName = getCustomizationItemData(customizationItem['id'], custType)
            itemCount = customizationItem['value']
            rewards[guiItemType][itemName] += itemCount

        result = []
        for guiItemType, items in rewards.iteritems():
            for itemName, itemCount in items.iteritems():
                msg = backport.text(R.strings.system_messages.customization.added.dyn(guiItemType)(), itemName)
                if itemCount > 1:
                    count = backport.text(R.strings.ny.notification.collectionComplete.bonusCount(), count=itemCount)
                    msg = ' '.join((msg, count))
                result.append(msg)

        return EOL.join(result)
