# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/messenger/formatters/service_channel.py
from helpers import dependency
from messenger import g_settings
from skeletons.gui.shared import IItemsCache
from skeletons.gui.goodies import IGoodiesCache
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData, getCustomizationItem
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.formatters import getStyle, text_styles
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, CREW_BONUS_X3_TOKEN
from items import vehicles, ITEM_TYPES
from one_time_gift.gui.gui_constants import OTG_MISSION_TOKEN_PREFIX
from dossiers2.ui.achievements import BADGES_BLOCK
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, List

class OneTimeGiftVehiclesReceiveFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __TEMPLATE = 'OTGVehiclesReceiveMessage'
    __BULLET = u' \u2022 '
    __BREAK_LINE = '<br/>'
    __INDENT = '<font size="6"> </font>' + __BREAK_LINE
    __SEPARATOR = __BREAK_LINE + __INDENT + __BULLET

    def format(self, message, *args):
        if not args:
            return [MessageData(None, None)]
        else:
            data = args[0]
            if not data['vehicles']:
                return [MessageData(None, None)]
            if data['isPremium']:
                vehiclesReceivedHeader = R.strings.one_time_gift.added.premiumVehicles()
            else:
                vehiclesReceivedHeader = R.strings.one_time_gift.added.vehicles()
            ctx = {'vehicles': ''.join([self.__BULLET, self.__formatVehicles(data['vehicles'])]),
             'slots': data['slots'],
             'vehiclesReceivedHeader': backport.text(vehiclesReceivedHeader)}
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx=ctx)
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    def __formatVehicles(self, vehiclesData):
        sortedVehicles = sorted(vehiclesData, key=lambda vehIntCD: self.__itemsCache.items.getItemByCD(vehIntCD).level, reverse=True)
        vehiclesStrings = [ self.__itemsCache.items.getItemByCD(vehIntCD).userName for vehIntCD in sortedVehicles ]
        return self.__SEPARATOR.join(vehiclesStrings)


class OneTimeGiftAdditionalRewardsReceiveFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __TEMPLATE = 'OTGAdditionalRewardsReceiveMessage'
    __BULLET = u' \u2022 '
    __BREAK_LINE = '<br/>'
    __INDENT = __BREAK_LINE + '<font size="6"> </font>' + __BREAK_LINE
    __OTG_MESSAGES = R.strings.one_time_gift.added
    __CURRENCY_ORDER = (Currency.CREDITS, Currency.CRYSTAL, Currency.GOLD)

    def format(self, message, *args):
        if not args:
            return [MessageData(None, None)]
        else:
            data = args[0]
            processors = (self.__formatCurrencies,
             self.__formatPremium,
             self.__formatItems,
             self.__formatVehicles,
             self.__formatGoodies,
             self.__formatCrewBook,
             self.__formatTokens,
             self.__formatCustomization,
             self.__formatAchievements)
            message = []
            for processor in processors:
                res = processor(data)
                if res:
                    message.append(res)

            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'message': self.__formatLines(message)})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    def __formatLines(self, lines):
        return self.__INDENT.join(lines)

    def __formatBulletList(self, lines, style=None):
        string = self.__BULLET + (self.__INDENT + self.__BULLET).join(lines)
        if style is not None:
            string = style(string)
        return string

    def __formatCurrencies(self, data):
        currencies = []
        for currency in self.__CURRENCY_ORDER:
            if currency not in data or not data[currency]:
                continue
            currencies.append(self.__BULLET + backport.text(self.__OTG_MESSAGES.dyn(currency)(), amount=self.__formatCurrencyCount(currency, data[currency])))

        return None if not currencies else self.__formatLines([backport.text(self.__OTG_MESSAGES.currencies())] + currencies)

    @staticmethod
    def __formatCurrencyCount(currencyName, count):
        style = getStyle(currencyName)
        return style(backport.getIntegralFormat(abs(count)))

    def __formatPremium(self, data):
        premium = data.get('premium_plus', 0)
        if not premium:
            return None
        else:
            style = text_styles.credits
            return backport.text(self.__OTG_MESSAGES.premium(), amount=style(premium))

    def __formatItems(self, data):
        items = data.get('items', {})
        itemsNames = []
        for intCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles.parseIntCompactDescr(intCD)
            if itemTypeID == ITEM_TYPES.crewBook:
                continue
            itemDescr = vehicles.getItemByCompactDescr(intCD)
            string = '{}{}'.format(self.__BULLET, itemDescr.i18n.userString)
            if count > 1:
                string += ': {}'.format(count)
            itemsNames.append(string)

        return None if not itemsNames else self.__formatLines([backport.text(self.__OTG_MESSAGES.equipment())] + sorted(itemsNames))

    def __formatCrewBook(self, data):
        items = data.get('items', {})
        for intCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles.parseIntCompactDescr(intCD)
            if itemTypeID != ITEM_TYPES.crewBook:
                continue
            return backport.text(self.__OTG_MESSAGES.universalManual(), amount=count)

        return None

    def __formatCustomization(self, data):
        customizations = data.get('customizations', {})
        names = []
        attachmentNames = []
        for customization in customizations:
            custType = customization.get('custType', None)
            isAttachment = custType == 'attachment'
            item = getCustomizationItem(customization['id'], custType)
            count = customization['value']
            string = item.userName
            if not isAttachment:
                string = backport.text(self.__OTG_MESSAGES.dyn(item.itemTypeName)(), element_name=string)
            if count > 1:
                string += ': {}'.format(count)
            if isAttachment:
                attachmentNames.append(string)
            names.append(string)

        result = []
        if attachmentNames:
            result.append(backport.text(self.__OTG_MESSAGES.attachment()))
            result.append(self.__formatBulletList(attachmentNames))
        if names:
            result.append(self.__formatLines(names))
        return None if not result else self.__formatLines(result)

    def __formatAchievements(self, data):
        dossier = data.get('dossier', {})
        achievements = []
        for d in dossier.itervalues():
            it = d if not isinstance(d, dict) else d.iteritems()
            for block, _ in it:
                achieve = getAchievementFactory(block).create()
                if achieve is None:
                    continue
                string = backport.text(self.__OTG_MESSAGES.medal(), element_name=achieve.getUserName())
                achievements.append(string)

        return self.__formatLines(achievements)

    def __formatTokens(self, data):
        tokens = data.get('tokens', {})
        itemsNames = []
        for tokenID, tokenData in tokens.iteritems():
            string = ''
            count = tokenData.get('count', 1)
            if tokenID.startswith(OTG_MISSION_TOKEN_PREFIX):
                string = backport.text(self.__OTG_MESSAGES.pm_token())
                if count > 1:
                    string += ': {}'.format(count)
            elif tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
                string = backport.text(self.__OTG_MESSAGES.battle_bonus_x5(), amount=count)
            elif tokenID.startswith(CREW_BONUS_X3_TOKEN):
                string = backport.text(self.__OTG_MESSAGES.crew_bonus_x3(), amount=count)
            itemsNames.append(string)

        return self.__formatLines(sorted(itemsNames))

    def __formatVehicles(self, data):
        vehiclesData = data.get('vehicles', {})
        addVehName, rentedVehName = [], []

        def sortVehicles():
            sortedVehicles = sorted(vehiclesData.keys(), key=lambda vehIntCD: self.__itemsCache.items.getItemByCD(vehIntCD).level, reverse=True)
            for vehIntCD in sortedVehicles:
                days = vehiclesData[vehIntCD].get('rent', {}).get('time', 0)
                compensatedNumber = vehiclesData[vehIntCD].get('compensatedNumber', 0)
                vehName = self.__itemsCache.items.getItemByCD(vehIntCD).userName
                if days:
                    rentedVehName.append(backport.text(self.__OTG_MESSAGES.rentedDays(), vehName=vehName, days=backport.getIntegralFormat(days)))
                if compensatedNumber == 0:
                    addVehName.append(vehName)

        sortVehicles()
        result = []
        style = None
        if addVehName:
            result.append(backport.text(self.__OTG_MESSAGES.premiumVehicles()))
            style = text_styles.credits
            result.append(self.__formatBulletList(addVehName, style))
        if rentedVehName:
            style = None
            result.append(backport.text(self.__OTG_MESSAGES.vehiclesRented()))
            result.append(self.__formatBulletList(rentedVehName))
        slots = self.__formatSlots(data, style)
        if slots:
            result.append(slots)
        return self.__formatLines(result)

    def __formatSlots(self, data, style=None):
        slots = data.get('slots', {})
        if not slots:
            return None
        else:
            slotsString = backport.getIntegralFormat(slots)
            if style:
                slotsString = style(slotsString)
            return '{} {}'.format(backport.text(self.__OTG_MESSAGES.slots()), slotsString)

    def __formatGoodies(self, data):
        goodiesData = data.get('goodies', {})
        if not goodiesData:
            return None
        else:
            result = []
            for goodieID, info in goodiesData.iteritems():
                if goodieID in self.__itemsCache.items.shop.recertificationForms:
                    count = info.get('count', 0)
                    string = backport.text(self.__OTG_MESSAGES.crewRetraining(), amount=count)
                    result.append(string)

            return self.__formatLines(result)


class OneTimeGiftCollectorRewardsReceiveFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __TEMPLATE = 'OTGCollectorRewardsReceiveMessage'
    __BREAK_LINE = '<br/>'
    __INDENT = __BREAK_LINE + '<font size="6"> </font>' + __BREAK_LINE
    __OTG_MESSAGES = R.strings.one_time_gift.addedCollector

    def format(self, message, *args):
        if not args:
            return [MessageData(None, None)]
        else:
            data = args[0]
            res = self.__formatAchievements(data)
            if not res:
                return [MessageData(None, None)]
            message = [res]
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'message': self.__formatLines(message)})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    def __formatAchievements(self, data):
        dossier = data.get('dossier', {})
        achievements = []
        badges = []
        badgesCache = self.__itemsCache.items.getBadges()
        for d in dossier.itervalues():
            for block, name in d:
                if block == BADGES_BLOCK:
                    badge = badgesCache[name]
                    badgeName = badge.getUserName()
                    isStripe = badge.isSuffixLayout()
                    badgeType = self.__OTG_MESSAGES.stripe() if isStripe else self.__OTG_MESSAGES.badge()
                    badges.append(backport.text(badgeType, element_name=badgeName))
                achieve = getAchievementFactory((block, name)).create()
                if achieve is not None:
                    achievements.append(backport.text(self.__OTG_MESSAGES.medal(), element_name=achieve.getUserName()))

        return self.__formatLines(badges + achievements)

    def __formatLines(self, lines):
        return self.__INDENT.join(lines)
