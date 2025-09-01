# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/server_events/bonuses.py
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import LootBoxTokensBonus, TokensBonus, tokensFactory, CustomizationsBonus
from white_tiger.skeletons.economics_controller import IEconomicsController
from helpers import dependency
from gui import makeHtmlString
from white_tiger_common.wt_constants import WT_LOOTBOX_TOKEN_KEYS

def whiteTigerTokensFactory(name, value, isCompensation=False, ctx=None):
    result = []
    nonWhiteTigerTokens = {}
    economyController = dependency.instance(IEconomicsController)
    for tID, tValue in value.iteritems():
        if tID == economyController.getTicketTokenName():
            result.append(TicketTokensBonus(name, {tID: tValue}, isCompensation, ctx))
        if tID == economyController.getStampTokenName():
            result.append(StampTokensBonus(name, {tID: tValue}, isCompensation, ctx))
        if tID in WT_LOOTBOX_TOKEN_KEYS:
            result.append(WTLootBoxBonus({tID: tValue}, isCompensation, ctx))
        nonWhiteTigerTokens[tID] = tValue

    result.extend(tokensFactory(name, nonWhiteTigerTokens, isCompensation, ctx))
    return result


class TicketTokensBonus(TokensBonus):
    __gameEventCtrl = dependency.descriptor(IEconomicsController)

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TicketTokensBonus, self).__init__(name, value, isCompensation, ctx)
        self._name = 'ticket'

    def isShowInGUI(self):
        return True

    def formatValue(self):
        ticketName = self.__gameEventCtrl.getConfig()['ticketToken']
        amount = sum([ data.get('count', 0) for tokenID, data in self._value.iteritems() if tokenID == ticketName ])
        return amount if bool(amount) else None

    def getWrappedEpicBonusList(self):
        return []

    def getUserName(self):
        return backport.text(R.strings.white_tiger_lobby.ticketTooltip.title())


class StampTokensBonus(TokensBonus):
    __gameEventCtrl = dependency.descriptor(IEconomicsController)

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(StampTokensBonus, self).__init__(name, value, isCompensation, ctx)
        self._name = 'stamp'

    def isShowInGUI(self):
        return True

    def formatValue(self):
        stampName = self.__gameEventCtrl.getConfig()['stamp']
        amount = sum([ data.get('count', 0) for tokenID, data in self._value.iteritems() if tokenID == stampName ])
        return amount if bool(amount) else None

    def getWrappedEpicBonusList(self):
        return []


class WtCustomizationsBonus(CustomizationsBonus):

    def formattedList(self):
        formattedList = []
        for item in self._value:
            if self._name is not None and item is not None:
                custItem = self.getC11nItem(item)
                itemType = custItem.itemTypeName
                value = item.get('value')
                text = makeHtmlString('html_templates:lobby/quests/bonuses/{}'.format(self._name), itemType, {'value': value})
                if text != self._name:
                    formattedList.append(text)

        return formattedList


class WTLootBoxBonus(LootBoxTokensBonus):

    def isShowInGUI(self):
        return True

    def formatValue(self):
        amount = sum([ data.get('count', 0) for _, data in self._value.iteritems() ])
        return amount or 0

    def formattedList(self):
        text = makeHtmlString('html_templates:lobby/quests/bonuses/', self.getBox().getCategory(), {'value': self.formatValue()})
        return [text]
