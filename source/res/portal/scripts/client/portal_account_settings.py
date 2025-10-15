# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_account_settings.py
import copy
from typing import TYPE_CHECKING
from account_helpers import AccountSettings
from portal_common.portal_constants import PORTAL_ACCOUNT_SETTINGS_KEY, ACCOUNT_DEFAULT_SETTINGS, SELECTED_COMPLEXITY_LEVEL, EVENT_ENTRY_POINT_IS_NEW, PORTAL_OUTRO_VIDEO_VIEWED, PORTAL_INTRO_VIDEO_VIEWED, PORTAL_FINISHED_NOTIFICATION_VIEWED, PORTAL_STARTED_NOTIFICATION_VIEWED, PORTAL_VEHICLE_UPGRADES_VIEWED, PORTAL_ABOUT_IMPROVEMENTS_VIEWED, MAX_UNLOCKED_UPGRADE_LEVEL_VIEWED
if TYPE_CHECKING:
    from typing import Any

def getSettings(name):
    settings = AccountSettings.getSettings(PORTAL_ACCOUNT_SETTINGS_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[PORTAL_ACCOUNT_SETTINGS_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(PORTAL_ACCOUNT_SETTINGS_KEY)
    settings[name] = value
    AccountSettings.setSettings(PORTAL_ACCOUNT_SETTINGS_KEY, settings)


def getSelectedComplexityLevel():
    return getSettings(SELECTED_COMPLEXITY_LEVEL)


def setSelectedComplexityLevel(level):
    return setSettings(SELECTED_COMPLEXITY_LEVEL, level)


def getEventEntrypointIsNew():
    return getSettings(EVENT_ENTRY_POINT_IS_NEW)


def setEventEntrypointIsNew(isNew):
    return setSettings(EVENT_ENTRY_POINT_IS_NEW, isNew)


def isOutroVideoViewed():
    return getSettings(PORTAL_OUTRO_VIDEO_VIEWED)


def setOutroVideoViewed(status):
    return setSettings(PORTAL_OUTRO_VIDEO_VIEWED, status)


def isIntroVideoViewed():
    return getSettings(PORTAL_INTRO_VIDEO_VIEWED)


def setIntroVideoViewed(status):
    return setSettings(PORTAL_INTRO_VIDEO_VIEWED, status)


def setPortalFinishedNotificationViewed(status):
    setSettings(PORTAL_FINISHED_NOTIFICATION_VIEWED, status)


def isPortalFinishedNotificationViewed():
    return getSettings(PORTAL_FINISHED_NOTIFICATION_VIEWED)


def setPortalStartedNotificationViewed(status):
    setSettings(PORTAL_STARTED_NOTIFICATION_VIEWED, status)


def isPortalStartedNotificationViewed():
    return getSettings(PORTAL_STARTED_NOTIFICATION_VIEWED)


def isVehicleUpgradesViewed(vehCD):
    vehicleUpgradesViewed = getSettings(PORTAL_VEHICLE_UPGRADES_VIEWED)
    return vehicleUpgradesViewed[vehCD]['isViewed']


def setVehicleUpgradesViewed(vehCD, isViewed):
    vehicleUpgradesViewed = copy.copy(getSettings(PORTAL_VEHICLE_UPGRADES_VIEWED))
    vehicleUpgradesViewed[vehCD]['isViewed'] = isViewed
    return setSettings(PORTAL_VEHICLE_UPGRADES_VIEWED, vehicleUpgradesViewed)


def getMaxViewedVehicleUpgradesStages(vehCD):
    vehicleUpgradesViewed = getSettings(PORTAL_VEHICLE_UPGRADES_VIEWED)
    return vehicleUpgradesViewed[vehCD]['maxViewedStage']


def setMaxViewedVehicleUpgradesStage(vehCD, stageID):
    vehicleUpgradesViewed = copy.copy(getSettings(PORTAL_VEHICLE_UPGRADES_VIEWED))
    vehicleUpgradesViewed[vehCD]['maxViewedStage'] = stageID
    return setSettings(PORTAL_VEHICLE_UPGRADES_VIEWED, vehicleUpgradesViewed)


def getMaxViewedUnlockedUpgradeLevel(vehCD):
    vehicleUpgradesViewed = getSettings(MAX_UNLOCKED_UPGRADE_LEVEL_VIEWED)
    return vehicleUpgradesViewed.get(vehCD, -1)


def setMaxViewedUnlockedUpgradeLevel(vehCD, level):
    vehicleUpgradesViewed = copy.copy(getSettings(MAX_UNLOCKED_UPGRADE_LEVEL_VIEWED))
    vehicleUpgradesViewed[vehCD] = level
    return setSettings(MAX_UNLOCKED_UPGRADE_LEVEL_VIEWED, vehicleUpgradesViewed)


def resetViewedVehicleUpgradesStages(vehCD):
    vehicleUpgradesViewed = copy.copy(getSettings(PORTAL_VEHICLE_UPGRADES_VIEWED))
    vehicleUpgradesViewed[vehCD]['maxViewedStage'] = -1
    return setSettings(PORTAL_VEHICLE_UPGRADES_VIEWED, vehicleUpgradesViewed)


def setAboutImprovementsViewed(status):
    setSettings(PORTAL_ABOUT_IMPROVEMENTS_VIEWED, status)


def isAboutImprovementsViewed():
    return getSettings(PORTAL_ABOUT_IMPROVEMENTS_VIEWED)
