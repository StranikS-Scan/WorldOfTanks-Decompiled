# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_notification.py
import logging
from collections import defaultdict
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import NYLootBoxesStorageKeys
from gui.shared.gui_items.loot_box import NewYearCategories, NewYearLootBoxes
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_SETTINGS_MAP = {NewYearCategories.NEWYEAR: SETTINGS_SECTIONS.LOOT_BOX_NEW_YEAR,
 NewYearCategories.ORIENTAL: SETTINGS_SECTIONS.LOOT_BOX_ORIENTAL,
 NewYearCategories.FAIRYTALE: SETTINGS_SECTIONS.LOOT_BOX_FAIRYTALE,
 NewYearCategories.CHRISTMAS: SETTINGS_SECTIONS.LOOT_BOX_CHRISTMAS,
 NewYearLootBoxes.COMMON: SETTINGS_SECTIONS.LOOT_BOX_COMMON}

class LootBoxNotification(object):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _itemsCache = dependency.descriptor(IItemsCache)
    _temp_storage = defaultdict(dict)

    @classmethod
    def hasNewBox(cls, boxType, category=''):
        count = cls.__getInventoryCount(boxType, category)
        settingsCount = cls.__getNewCount(boxType, category)
        return count > settingsCount

    @classmethod
    def hasDeliveredBox(cls, category):
        count = cls.__getInventoryCount(NewYearLootBoxes.PREMIUM, category)
        settingsCount = cls.__getCategoryDeliveredCount(category)
        return count > settingsCount

    @classmethod
    def setCategoryNewCount(cls, boxType, category=''):
        count = cls.__getInventoryCount(boxType, category)
        cls.__setCategoryNewCount(boxType, category, count)

    @classmethod
    def setCategoryDeliveredCount(cls, category):
        count = cls.__getInventoryCount(NewYearLootBoxes.PREMIUM, category)
        cls.__setCategoryDeliveredCount(category, count)

    @classmethod
    def setTotalLootBoxesCount(cls, count):
        cls._temp_storage[SETTINGS_SECTIONS.LOOT_BOX_VIEWED]['count'] = count

    @classmethod
    def saveSettings(cls):
        for section, settings in cls._temp_storage.iteritems():
            cls._settingsCore.serverSettings.setSectionSettings(section, settings)

        cls.__resetTempStorage()

    @classmethod
    def __resetTempStorage(cls):
        cls._temp_storage.clear()

    @classmethod
    def __getInventoryCount(cls, boxType, category=''):
        count = 0
        for lootBox in cls._itemsCache.items.tokens.getLootBoxes().itervalues():
            if lootBox.getCategory() == category and lootBox.getType() == boxType:
                count += lootBox.getInventoryCount()

        return count

    @classmethod
    def __getNewCount(cls, boxType, category=''):
        if boxType == NewYearLootBoxes.PREMIUM:
            return cls.__getCategorySettingCount(category, NYLootBoxesStorageKeys.NEW_COUNT)
        return cls.__getCategorySettingCount(NewYearLootBoxes.COMMON, NYLootBoxesStorageKeys.NEW_COUNT) if boxType == NewYearLootBoxes.COMMON else None

    @classmethod
    def __getCategoryDeliveredCount(cls, category):
        return cls.__getCategorySettingCount(category, NYLootBoxesStorageKeys.DELIVERED_COUNT)

    @classmethod
    def __getCategorySettingCount(cls, category, settingKey):
        settingName = _SETTINGS_MAP.get(category)
        if settingName is None:
            _logger.error('Failed to get serverSettings: [%s] for lootboxes category: [%s]', settingKey, category)
            return 0
        else:
            categorySettings = cls._temp_storage[settingName]
            if settingKey not in categorySettings:
                count = cls._settingsCore.serverSettings.getSectionSettings(settingName, settingKey, 0)
                categorySettings[settingKey] = count
            return cls._temp_storage[settingName][settingKey]

    @classmethod
    def __setCategoryNewCount(cls, boxType, category, count):
        if boxType == NewYearLootBoxes.PREMIUM:
            cls.__setCategorySettingCount(category, NYLootBoxesStorageKeys.NEW_COUNT, count)
        elif boxType == NewYearLootBoxes.COMMON:
            cls.__setCategorySettingCount(NewYearLootBoxes.COMMON, NYLootBoxesStorageKeys.NEW_COUNT, count)

    @classmethod
    def __setCategoryDeliveredCount(cls, category, count):
        cls.__setCategorySettingCount(category, NYLootBoxesStorageKeys.DELIVERED_COUNT, count)

    @classmethod
    def __setCategorySettingCount(cls, category, settingKey, count):
        settingName = _SETTINGS_MAP.get(category)
        if settingName is not None:
            cls._temp_storage[settingName][settingKey] = count
        else:
            _logger.error('Failed to set serverSettings: [%s] for lootboxes category: [%s]', settingKey, category)
        return
