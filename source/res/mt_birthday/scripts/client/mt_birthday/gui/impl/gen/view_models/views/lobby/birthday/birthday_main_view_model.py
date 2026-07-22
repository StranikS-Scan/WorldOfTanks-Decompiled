# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/birthday_main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.lootbox_entry_point import LootboxEntryPoint

class TabId(IntEnum):
    MAIL = 0
    QUESTS = 1
    REWARDS = 2
    GOLD_WAGON = 3
    TICKET_EXCHANGE = 4
    ABOUT = 5


class BirthdayMainViewModel(ViewModel):
    __slots__ = ('onTabChange', 'onClose', 'onOpenGoldenCarriage', 'onTipsCompleted')

    def __init__(self, properties=9, commands=4):
        super(BirthdayMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def lootboxEntryPoint(self):
        return self._getViewModel(0)

    @staticmethod
    def getLootboxEntryPointType():
        return LootboxEntryPoint

    def getIsTipEnabled(self):
        return self._getBool(1)

    def setIsTipEnabled(self, value):
        self._setBool(1, value)

    def getIsGeneralTipEnabled(self):
        return self._getBool(2)

    def setIsGeneralTipEnabled(self, value):
        self._setBool(2, value)

    def getHasNewRewards(self):
        return self._getBool(3)

    def setHasNewRewards(self, value):
        self._setBool(3, value)

    def getCurrentTabId(self):
        return self._getNumber(4)

    def setCurrentTabId(self, value):
        self._setNumber(4, value)

    def getIsIntroSeen(self):
        return self._getBool(5)

    def setIsIntroSeen(self, value):
        self._setBool(5, value)

    def getHasGoldenTickets(self):
        return self._getBool(6)

    def setHasGoldenTickets(self, value):
        self._setBool(6, value)

    def getIsEnabledGoldWagonEntry(self):
        return self._getBool(7)

    def setIsEnabledGoldWagonEntry(self, value):
        self._setBool(7, value)

    def getIsEnabledTicketExchangeEntry(self):
        return self._getBool(8)

    def setIsEnabledTicketExchangeEntry(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(BirthdayMainViewModel, self)._initialize()
        self._addViewModelProperty('lootboxEntryPoint', LootboxEntryPoint())
        self._addBoolProperty('isTipEnabled', False)
        self._addBoolProperty('isGeneralTipEnabled', False)
        self._addBoolProperty('hasNewRewards', False)
        self._addNumberProperty('currentTabId', 0)
        self._addBoolProperty('isIntroSeen', True)
        self._addBoolProperty('hasGoldenTickets', False)
        self._addBoolProperty('isEnabledGoldWagonEntry', False)
        self._addBoolProperty('isEnabledTicketExchangeEntry', False)
        self.onTabChange = self._addCommand('onTabChange')
        self.onClose = self._addCommand('onClose')
        self.onOpenGoldenCarriage = self._addCommand('onOpenGoldenCarriage')
        self.onTipsCompleted = self._addCommand('onTipsCompleted')
