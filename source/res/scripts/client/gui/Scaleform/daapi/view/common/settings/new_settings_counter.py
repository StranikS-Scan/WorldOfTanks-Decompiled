# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/new_settings_counter.py
""" NEW_SETTINGS_COUNTER Structure
NEW_SETTINGS_COUNTER can contain structure was described below:
{
    'tabID_1' : {
        'subTabID_1' : {
            'controlID_1' : True/False,
            'controlID_2' : True/False,
            ...
        },
        'subTabID_2' {
            ...
        },
        ...
    },
    'tabID_2' : {
        'controlID_3' : True/False,
        'controlID_4' : True/False,
        ...
    },
    ...
}

Where:
    tabID - 'GameSettings' | 'GraphicSettings' | 'SoundSettings' | 'ControlsSettings' |
            'AimSettings' | 'MarkerSettings' | 'FeedbackSettings'
    subTabID - 'feedbackDamageLog' | 'arcade' | 'sniper' | 'ally' | 'enemy' ...
    controlID - str

Example:
    {
        'GameSettings': {
            'enableSpamFilter': True
        },
        'GraphicSettings': {
            'vertSync': True,
            'VEHICLE_DUST_ENABLED': True
        },
        'FeedbackSettings': {
            'feedbackDamageLog': {
                'damageLogAssistStun': True
            },
            'feedbackBattleEvents': {
                'battleEventsEnemyAssistStun': True,
            },
        },
        'MarkerSettings': {
            'enemy': {
                'markerBaseLevel': True,
                'markerBaseHpIndicator': True,
            }
        }
    }
"""
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_SETTINGS_COUNTER

def getCountNewSettings():
    """Get count of new settings items
    :return: int
    """
    settings = _getSettingsFromStorage()
    count = _countNewSettingsItems(settings, 0)
    return count


def getNewSettings():
    """Get list of new settings to view
    :return: dict {'tabId', 'subTabsData':['subTabId','counters'[{'count', 'componentId'},],]},
    """
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


def invalidateSettings(tabName, subTabName, controlID):
    """Update viewed settings
    :param tabName: viewed tabName
    :param subTabName: viewed subTab if it exist for current view
    :param controlID: controlID
    """
    settings = _getSettingsFromStorage()
    isChanged = False
    if tabName in settings.keys():
        tabSettings = settings[tabName]
        if subTabName:
            if subTabName in tabSettings:
                subTabSettings = tabSettings[subTabName]
                if controlID in subTabSettings and subTabSettings[controlID]:
                    subTabSettings[controlID] = False
                    isChanged = True
        elif controlID in tabSettings and tabSettings[controlID]:
            tabSettings[controlID] = False
            isChanged = True
    if isChanged:
        _setSettingsToStorage(settings)
        return True
    return False


def _countNewSettingsItems(dictItem, count):
    for k, v in dictItem.iteritems():
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
    """Get settings from accountSettings
    """
    return AccountSettings.getSettings(NEW_SETTINGS_COUNTER)


def _setSettingsToStorage(value):
    """Set settings to accountSettings
    """
    AccountSettings.setSettings(NEW_SETTINGS_COUNTER, value)
