# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/messenger/formatters/service_channel.py
from collections import defaultdict
import nations
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from gui import GUI_NATIONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import getStyle, text_styles
from gui.shared.money import Currency
from gui.shared.utils.requesters.blueprints_requester import getFragmentNationID
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.shared import IItemsCache

class TechTreeTradeInCompletedFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'TechTreeTradeInCompleted'
    __TECH_TREE_TRADE_IN_MESSAGES = R.strings.tech_tree_trade_in_messenger.serviceChannelMessages.techTreeTradeInComplete
    __BULLET = u'\u2022'
    __BREAK_LINE = '<br/>'
    __SPACE = ' '
    __INDENT = '<font size="6"> </font>'
    __SEPARATOR = __BREAK_LINE + __INDENT + __BREAK_LINE + __BULLET + __SPACE
    __NONE_NATION_NAME = 'intelligence'
    __NO_NATION_INDEX = -1
    __NATIONS_ORDER = {name:idx for idx, name in enumerate(GUI_NATIONS, 0)}
    __NATIONS_ORDER[__NONE_NATION_NAME] = __NO_NATION_INDEX
    __CURRENCY_ORDER = {name:idx for idx, name in enumerate((Currency.GOLD, Currency.CRYSTAL, Currency.FREE_XP))}
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        if not args:
            return [MessageData(None, None)]
        else:
            data = args[0]
            unlockedVehciles = self.__formatVehicles(data.get('unlockedVehicles', {}))
            lockedVehciles = self.__formatVehicles(data.get('lockedVehicles', {}))
            if not unlockedVehciles or not lockedVehciles:
                return [MessageData(None, None)]
            resources = self.__formatResources(data.get('resources', {}))
            if not resources:
                return [MessageData(None, None)]
            ctx = {'resources': self.__SPACE.join([self.__BULLET, resources]),
             'unlockedVehicles': self.__SPACE.join([self.__BULLET, unlockedVehciles]),
             'lockedVehicles': self.__SPACE.join([self.__BULLET, lockedVehciles])}
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx=ctx)
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    def __formatVehicles(self, vehicles):
        vehiclesStrings = []
        for vehCD in vehicles:
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            vehiclesStrings.append(vehicle.userName)

        return self.__SEPARATOR.join(vehiclesStrings)

    def __formatResources(self, resources):
        resourceStrings = []
        if 'currency' in resources:
            resourceStrings.extend(self.__formatCurrencies(resources['currency']))
        if 'blueprints' in resources:
            resourceStrings.append(self.__formatBlueprints(resources['blueprints']))
        return self.__SEPARATOR.join(resourceStrings)

    def __formatBlueprints(self, blueprintResources):
        blueprints = defaultdict(int)
        for fragmentCD, amount in blueprintResources.iteritems():
            fragmentType = getFragmentType(fragmentCD)
            if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
                blueprints[self.__NONE_NATION_NAME] += amount
            if fragmentType == BlueprintTypes.NATIONAL:
                blueprints[nations.MAP.get(getFragmentNationID(fragmentCD), nations.NONE_INDEX)] += amount

        blueprintStrings = []
        for nation, amount in sorted(blueprints.items(), cmp=lambda a, b: cmp(self.__NATIONS_ORDER.get(a), self.__NATIONS_ORDER.get(b)), key=lambda x: x[0]):
            if nation == self.__NONE_NATION_NAME:
                blueprintStrings.append(backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.blueprints.universal(), amount=self.__formatBlueprintsAmount(amount)))
            blueprintStrings.append(backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.blueprints.national(), nationName=backport.text(R.strings.blueprints.nations.dyn(nation)()), amount=self.__formatBlueprintsAmount(amount)))

        return self.__SPACE.join([backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.blueprints.title()), ', '.join(blueprintStrings)])

    def __formatCurrencies(self, currencyResources):
        currencies = sorted(currencyResources.items(), key=lambda x: x[0], cmp=lambda a, b: cmp(self.__CURRENCY_ORDER.get(a), self.__CURRENCY_ORDER.get(b)))
        return [ backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.dyn(name)(), amount=self.__formatCurrencyCount(name, amount)) for name, amount in currencies ]

    @staticmethod
    def __formatCurrencyCount(currencyName, count):
        style = getStyle(currencyName) if currencyName in Currency.ALL else text_styles.crystal
        return style(backport.getIntegralFormat(abs(count)))

    def __formatBlueprintsAmount(self, amount):
        return text_styles.crystal(backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.blueprints.amount(), amount=backport.getIntegralFormat(abs(amount))))


class TechTreeTradeInDetailsFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'TechTreeTradeInDetails'
    __TECH_TREE_TRADE_IN_MESSAGES = R.strings.tech_tree_trade_in_messenger.serviceChannelMessages.techTreeTradeInDetails
    __BULLET = u'\u2022'
    __BREAK_LINE = '<br/>'
    __SPACE = ' '
    __INDENT = '<font size="6"> </font>'
    __SEPARATOR = __BREAK_LINE + __INDENT + __BREAK_LINE + __BULLET + __SPACE
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        if not args:
            return [MessageData(None, None)]
        else:
            ctx = {'details': self.__SPACE.join([self.__BULLET, self.__formatDetails(args[0])])}
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx=ctx)
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    def __formatDetails(self, details):
        detailsStrings = [backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.details.crew(), sentToBarracksAmount=self.__formatAmount(details['crew']['sentToBarracks']), nationalRescruitsAmount=self.__formatAmount(details['crew']['recruits'])), backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.details.postProgressionCompensation(), amount=self.__formatAmount(details['postProgressionCompensation']['currency'][Currency.CREDITS])), backport.text(self.__TECH_TREE_TRADE_IN_MESSAGES.details.xpTransfer(), vehicleName=text_styles.credits(self.__getVehName(details['xpTransferredVehCD'])))]
        return self.__SEPARATOR.join(detailsStrings)

    @staticmethod
    def __formatAmount(amount):
        return text_styles.credits(backport.getIntegralFormat(abs(amount)))

    def __getVehName(self, vehCD):
        return self.__itemsCache.items.getItemByCD(vehCD).userName
