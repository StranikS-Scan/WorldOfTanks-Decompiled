# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/counter_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_SETTINGS_COUNTER
from account_helpers.settings_core import settings_constants
from helpers import dependency
from skeletons.gui.game_control import IAnonymizerController
_NEW_SETTING_COUNTER_VISIBILITY_VALIDATORS = {settings_constants.GAME.ANONYMIZER: lambda : dependency.instance(IAnonymizerController).isEnabled}

def isNewSettingCounterVisible(settingKey):
    return _NEW_SETTING_COUNTER_VISIBILITY_VALIDATORS.get(settingKey, lambda : True)()


def getCountNewSettings():
    settings = _getSettingsFromStorage()
    count = _countNewSettingsItems(settings, 0)
    return count


def getNewSettings():
    settings = _getSettingsFromStorage()
    result = []
    for tabID, tabsSettings in settings.iteritems():
        tabData = _getTabData(result, tabID)
        for subTabID, controlSettings in tabsSettings.iteritems():
            if isinstance(controlSettings, bool):
                controlID = subTabID
                subTabID = None
                _packCounter(tabData, controlSettings, subTabID, controlID)
            for controlID, state in controlSettings.iteritems():
                _packCounter(tabData, state, subTabID, controlID)

    return result


def invalidateSettings(tabName, subTabName, controlIDs):
    settings = _getSettingsFromStorage()
    isChanged = False
    if tabName in settings.keys():
        tabSettings = settings[tabName]
        if subTabName in tabSettings:
            subContainer = tabSettings[subTabName]
        else:
            subContainer = tabSettings
        for controlID in controlIDs:
            if controlID in subContainer and subContainer[controlID]:
                subContainer[controlID] = False
                isChanged = True

    if isChanged:
        _setSettingsToStorage(settings)
        return True
    return False


def dropCounters():
    newsettings = getNewSettings()
    for setting in newsettings:
        for subtab in setting['subTabsData']:
            for counter in subtab['counters']:
                invalidateSettings(setting['tabId'], subtab['subTabId'], [counter['componentId']])


def _countNewSettingsItems(dictItem, count):
    for _, v in dictItem.iteritems():
        if isinstance(v, dict):
            count = _countNewSettingsItems(v, count)
        if isinstance(v, bool) and v:
            count = count + 1

    return count


def _getTabData(formatedData, searchTabID):
    for tabData in formatedData:
        if tabData['tabId'] == searchTabID:
            if 'subTabsData' not in tabData:
                tabData['subTabsData'] = []
            return tabData

    tabData = {'tabId': searchTabID,
     'subTabsData': []}
    formatedData.append(tabData)
    return tabData


def _packCounter(tabData, state, subTabID, controlID):
    count = '1' if state else '0'
    counters = None
    for subTabData in tabData['subTabsData']:
        if subTabData['subTabId'] == subTabID:
            if 'counters' not in subTabData:
                subTabData['counters'] = []
            counters = subTabData['counters']
            break

    if counters is None:
        emptySubTabData = {'subTabId': subTabID,
         'counters': []}
        tabData['subTabsData'].append(emptySubTabData)
        counters = emptySubTabData['counters']
    counters.append({'componentId': controlID,
     'count': count})
    return


def _getSettingsFromStorage():
    return _filterSettings(AccountSettings.getSettings(NEW_SETTINGS_COUNTER))


def _setSettingsToStorage(value):
    AccountSettings.setSettings(NEW_SETTINGS_COUNTER, _filterSettings(value))


def _filterSettings(value):
    return {category:{settingKey:settingValue for settingKey, settingValue in settings.iteritems() if isNewSettingCounterVisible(settingKey)} for category, settings in value.iteritems()}
