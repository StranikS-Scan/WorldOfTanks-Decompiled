# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/new_items_notification.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_CUSTOMIZATION_ITEMS
from gui.customization.shared import CUSTOMIZATION_TYPE

class _AbstractItemNotification(object):

    @classmethod
    def getNewItems(cls):
        items = cls.__getItemsFromStorage()
        return [ k for k, v in items.iteritems() if v ]

    @classmethod
    def setNewItemVisited(cls, itemName):
        items = cls.__getItemsFromStorage()
        if itemName in items.keys():
            items[itemName] = False
            cls.__setItemsToStorage(items)

    @classmethod
    def _getAccountSettingsKey(cls):
        raise NotImplementedError

    @classmethod
    def _getFormattedValue(cls, value):
        if value > 0:
            return str(value)
        else:
            return ''

    @classmethod
    def __getItemsFromStorage(cls):
        return AccountSettings.getSettings(cls._getAccountSettingsKey())

    @classmethod
    def __setItemsToStorage(cls, value):
        AccountSettings.setSettings(cls._getAccountSettingsKey(), value)


class CustomizationItemNotification(_AbstractItemNotification):
    """
    It is better to add method for initializing 'count', instead of hardcoded values
    If the functionality is added to trunk, it should be refactored.
    For the event battle leave as is.
    """
    _COUNTER_MAP = {CUSTOMIZATION_TYPE.INSCRIPTION: (4, 'inscriptions'),
     CUSTOMIZATION_TYPE.EMBLEM: (3, 'emblems')}

    @classmethod
    def getFormattedItemCountByType(cls, customizationType):
        count = cls.__getItemCountByType(customizationType)
        return cls._getFormattedValue(count)

    @classmethod
    def getFormattedOverallCount(cls):
        return cls._getFormattedValue(cls.__getOverallCount())

    @classmethod
    def setItemVisitedByType(cls, customizationType):
        if customizationType in cls._COUNTER_MAP:
            _, accountSettingName = cls._COUNTER_MAP[customizationType]
            cls.setNewItemVisited(accountSettingName)

    @classmethod
    def _getAccountSettingsKey(cls):
        return NEW_CUSTOMIZATION_ITEMS

    @classmethod
    def __getItemCountByType(cls, customizationType):
        if customizationType in cls._COUNTER_MAP:
            counter, accountSettingsName = cls._COUNTER_MAP[customizationType]
            if accountSettingsName in cls.getNewItems():
                return counter
            else:
                return 0
        else:
            return 0

    @classmethod
    def __getOverallCount(cls):
        result = 0
        for cType in CUSTOMIZATION_TYPE.ALL:
            result += cls.__getItemCountByType(cType)

        return result
