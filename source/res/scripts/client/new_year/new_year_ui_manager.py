# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/new_year_ui_manager.py
import Event
from skeletons.new_year import INewYearUIManager
from gui.shared.utils.HangarSpace import g_hangarSpace
from account_helpers.AccountSettings import AccountSettings, NY_DECORATIONS_POPOVER_FILTER_1

class NewYearUIManager(INewYearUIManager):

    def __init__(self):
        self.__em = Event.EventManager()
        self.__craftPopoverFilter = None
        self.__selectedCraftToy = None
        self.__selectedCollectionLevels = None
        self.onCraftPopoverFilterChanged = Event.Event(self.__em)
        self.onChestGiftsLoaded = Event.Event(self.__em)
        self.onChestGiftsDone = Event.Event(self.__em)
        self.onChestDone = Event.Event(self.__em)
        self.buttonClickOpenChest = Event.Event(self.__em)
        self.buttonClickOpenNextChest = Event.Event(self.__em)
        self.buttonClickCloseChest = Event.Event(self.__em)
        self.chestViewDone = Event.Event(self.__em)
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreated
        return

    def fini(self):
        self.__em.clear()
        self.__craftPopoverFilter = None
        self.__selectedCollectionLevels = None
        self.__selectedCraftToy = None
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        return

    def getCraftPopoverFilter(self):
        return self.__craftPopoverFilter

    def setCraftPopoverFilter(self, craftFilter):
        self.__craftPopoverFilter = craftFilter
        self.onCraftPopoverFilterChanged()

    def getSelectedCollectionLevels(self):
        return self.__selectedCollectionLevels

    def setSelectedCollectionLevels(self, selectedCollectionLevels):
        self.__selectedCollectionLevels = selectedCollectionLevels

    def getSelectedCraftToy(self):
        return self.__selectedCraftToy

    def setSelectedCraftToy(self, selectedToy):
        self.__selectedCraftToy = selectedToy

    def __onSpaceCreated(self):
        self.__craftPopoverFilter = None
        self.__selectedCraftToy = None
        self.__selectedCollectionLevels = None
        AccountSettings.setFilter(NY_DECORATIONS_POPOVER_FILTER_1, (0, 0))
        return
