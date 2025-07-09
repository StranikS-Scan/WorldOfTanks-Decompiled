# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/birthday_main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.lootbox_entry_point import LootboxEntryPoint

class TabId(IntEnum):
    MAIL = 0
    REWARDS = 1
    ABOUT = 2


class BirthdayMainViewModel(ViewModel):
    __slots__ = ('onTabChange', 'onClose', 'onOpenGoldenCarriage')

    def __init__(self, properties=6, commands=3):
        super(BirthdayMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def lootboxEntryPoint(self):
        return self._getViewModel(0)

    @staticmethod
    def getLootboxEntryPointType():
        return LootboxEntryPoint

    def getHasNewRewards(self):
        return self._getBool(1)

    def setHasNewRewards(self, value):
        self._setBool(1, value)

    def getCurrentTabId(self):
        return self._getNumber(2)

    def setCurrentTabId(self, value):
        self._setNumber(2, value)

    def getIsIntroSeen(self):
        return self._getBool(3)

    def setIsIntroSeen(self, value):
        self._setBool(3, value)

    def getHasGoldenTickets(self):
        return self._getBool(4)

    def setHasGoldenTickets(self, value):
        self._setBool(4, value)

    def getIsEnabledGoldWagonEntry(self):
        return self._getBool(5)

    def setIsEnabledGoldWagonEntry(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BirthdayMainViewModel, self)._initialize()
        self._addViewModelProperty('lootboxEntryPoint', LootboxEntryPoint())
        self._addBoolProperty('hasNewRewards', False)
        self._addNumberProperty('currentTabId', 0)
        self._addBoolProperty('isIntroSeen', True)
        self._addBoolProperty('hasGoldenTickets', False)
        self._addBoolProperty('isEnabledGoldWagonEntry', False)
        self.onTabChange = self._addCommand('onTabChange')
        self.onClose = self._addCommand('onClose')
        self.onOpenGoldenCarriage = self._addCommand('onOpenGoldenCarriage')
