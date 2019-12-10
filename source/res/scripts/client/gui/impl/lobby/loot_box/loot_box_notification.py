# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_notification.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from gui.shared.gui_items.loot_box import NewYearCategories
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
_SETTINGS_MAP = {NewYearCategories.NEWYEAR: SETTINGS_SECTIONS.LOOT_BOX_NEW_YEAR,
 NewYearCategories.ORIENTAL: SETTINGS_SECTIONS.LOOT_BOX_ORIENTAL,
 NewYearCategories.FAIRYTALE: SETTINGS_SECTIONS.LOOT_BOX_FAIRYTALE,
 NewYearCategories.CHRISTMAS: SETTINGS_SECTIONS.LOOT_BOX_CHRISTMAS}

class LootBoxNotification(object):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _itemsCache = dependency.descriptor(IItemsCache)
    _temp_storage = {}

    @classmethod
    def hasNewBox(cls, category):
        count = cls.__getInventoryCount(category)
        settingsCount = cls.__getCategoryCount(category)
        return count > settingsCount

    @classmethod
    def saveCategory(cls, category):
        count = cls.__getInventoryCount(category)
        cls.__setCategoryCount(category, count)

    @classmethod
    def setTotalLootCount(cls, count):
        cls._temp_storage[SETTINGS_SECTIONS.LOOT_BOX_VIEWED] = count

    @classmethod
    def resetTempStorage(cls):
        cls._temp_storage.clear()

    @classmethod
    def applyTempStorage(cls):
        cls._settingsCore.serverSettings.setSettings(cls._temp_storage)
        cls.resetTempStorage()

    @classmethod
    def __getInventoryCount(cls, category):
        count = 0
        for lootBox in cls._itemsCache.items.tokens.getLootBoxes().itervalues():
            if lootBox.getCategory() == category:
                count += lootBox.getInventoryCount()

        return count

    @classmethod
    def __getCategoryCount(cls, category):
        settingName = _SETTINGS_MAP.get(category)
        if settingName:
            if settingName not in cls._temp_storage:
                count = cls._settingsCore.serverSettings.getSectionSettings(settingName, 'count', 0)
                cls._temp_storage[settingName] = count
            return cls._temp_storage[settingName]

    @classmethod
    def __setCategoryCount(cls, category, count):
        settingName = _SETTINGS_MAP.get(category)
        if settingName:
            cls._temp_storage[settingName] = count
