# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/techtree_events.py
import operator
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import TOP_OF_TREE_CONFIG
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from helpers.time_utils import ONE_DAY
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.techtree_events import ITechTreeEventsListener
from gui.server_events.events_constants import TECH_TREE_ACTION_POSTFIX
from gui.Scaleform.daapi.view.lobby.store.actions_helpers import getActionInfoData
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
_GROUP_NAME_SEPARATOR = '!'
_NOTIFY_THRESHOLD = ONE_DAY * 5

class _SettingsCache(object):
    _NATIONS = 'nations'
    _NOTIFIED = 'notified'

    def update(self, actionIDs):
        AccountSettings.setSettings(TOP_OF_TREE_CONFIG, dict(((actionID, _SettingsCache._getSettings(actionID)) for actionID in actionIDs)))

    def viewedNations(self):
        settings = _SettingsCache._getSettings()
        viewedNations = set()
        for eventSettings in settings.values():
            viewedNations.update([ nationID for nationID, viewed in enumerate(eventSettings[_SettingsCache._NATIONS]) if viewed ])

        return viewedNations

    def selectNation(self, actionID, nationID):
        eventSettings = _SettingsCache._getSettings(actionID)
        eventSettings[_SettingsCache._NATIONS][nationID] = True
        _SettingsCache._setSettings(actionID, eventSettings)

    def isNotified(self, actionID):
        return _SettingsCache._getSettings(actionID)[_SettingsCache._NOTIFIED]

    def setNotified(self, actionID):
        eventSettings = _SettingsCache._getSettings(actionID)
        eventSettings[_SettingsCache._NOTIFIED] = True
        return _SettingsCache._setSettings(actionID, eventSettings)

    @staticmethod
    def _defaultValue():
        return {_SettingsCache._NATIONS: [False] * len(nations.NAMES),
         _SettingsCache._NOTIFIED: False}

    @staticmethod
    def _setSettings(actionID, value):
        settings = AccountSettings.getSettings(TOP_OF_TREE_CONFIG)
        settings[actionID] = value
        AccountSettings.setSettings(TOP_OF_TREE_CONFIG, settings)

    @staticmethod
    def _getSettings(actionID=None):
        settings = AccountSettings.getSettings(TOP_OF_TREE_CONFIG)
        return settings if actionID is None else settings.get(actionID, _SettingsCache._defaultValue())


class TechTreeEventsListener(ITechTreeEventsListener):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __systemMessages = dependency.descriptor(ISystemMessages)
    actions = property(lambda self: self.__actions.keys())

    def __init__(self):
        self.__actions = {}
        self.__items = {}
        self.__settings = _SettingsCache()
        self.__em = EventManager()
        self.onEventsUpdated = Event(self.__em)
        self.onSettingsChanged = Event(self.__em)

    def init(self):
        self.__eventsCache.onSyncCompleted += self.__update
        self.__update()
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdated})

    def fini(self):
        self.__eventsCache.onSyncCompleted -= self.__update
        self.__em.clear()
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getUserName(self, actionID):
        action = self.__actions.get(actionID, None)
        return str() if action is None else action.getUserName()

    def getVehicles(self, nationID=None):
        vehicles = set()
        for actionID in self.__actions:
            vehicles.update([ v.intCD for v in self.__getVehicles(actionID, nationID) ])

        return vehicles

    def setNationViewed(self, nationID):
        for actionID in self.__getActions(nationID=nationID):
            self.__settings.selectNation(actionID, nationID)

        self.onSettingsChanged()

    def getNations(self, unviewed=False, actionID=None):
        if not self.actions:
            return set()
        else:
            if actionID is not None:
                nationIDs = self.__getNations(actionID)
            else:
                nationIDs = set.union(*[ self.__getNations(actionID) for actionID in self.__actions ])
            return nationIDs.difference(self.__settings.viewedNations()) if unviewed else nationIDs

    def getTimeTillEnd(self, actionID):
        action = self.__actions.get(actionID, None)
        return 0 if action is None else action.getFinishTimeLeft()

    def getFinishTime(self, actionID):
        action = self.__actions.get(actionID, None)
        return 0 if action is None else action.getFinishTime()

    def hasActiveAction(self, vehicleCD, nationID=None):
        return bool(self.__getActions(vehicleCD, nationID))

    def getActiveAction(self, vehicleCD=None, nationID=None):
        actionIDs = self.__getActions(vehicleCD, nationID)
        return self.__getActualEventID(actionIDs)

    def __update(self):
        actions = self.__eventsCache.getActions(self.__eventFilter())
        for aID, action in actions.items():
            for actionInfo in getActionInfoData(action):
                items = actionInfo.discount.parse()
                self.__items.update({aID: items})

        self.__actions = actions
        if self.actions:
            self.__settings.update(self.actions)
        self.__notifyAboutExpiration()

    def __getVehicles(self, actionID, nationID=None):
        items = self.__items.get(actionID, [])
        if nationID is not None:
            return [ v for v in items if v.nationID == nationID ]
        else:
            return items

    def __getNations(self, actionID):
        return {v.nationID for v in self.__getVehicles(actionID)}

    def __getUserName(self, actionID):
        action = self.__actions.get(actionID, None)
        return str() if action is None else action.getUserName()

    def __getActualEventID(self, actionIDs):
        actionItems = [ pair for pair in self.__actions.items() if pair[0] in actionIDs ]
        return None if not actionItems else min(((k, v.getFinishTime()) for k, v in actionItems), key=operator.itemgetter(1))[0]

    def __onAccountShowGUI(self, ctx):
        self.__notifyAboutExpiration()

    def __notifyAboutExpiration(self):
        if not self.actions:
            return
        expireTime = min([ action.getFinishTimeLeft() for action in self.__actions.values() ])
        if ONE_DAY <= expireTime <= _NOTIFY_THRESHOLD:
            actionIDs = [ aID for aID, action in self.__actions.items() if action.getFinishTimeLeft() == expireTime ]
            if actionIDs and any((self.__actionNotifierCondition(aID) for aID in actionIDs)):
                self.__systemMessages.proto.serviceChannel.pushClientMessage({'actionName': self.getUserName(actionIDs[0]),
                 'timeLeft': expireTime,
                 'single': len(self.actions) == 1}, SCH_CLIENT_MSG_TYPE.TECH_TREE_ACTION_DISCOUNT)
                map(self.__settings.setNotified, actionIDs)

    def __actionNotifierCondition(self, actionID):
        vehicleDossier = self.__getVehicleCDsWereInBattle()

        def invalidateVehicle(vehicle, dossier):
            return vehicle.level == 10 and not vehicle.isInInventory and vehicle.intCD not in dossier

        vehicles = self.__items[actionID].keys()
        isNotified = self.__settings.isNotified(actionID)
        return any((invalidateVehicle(vehicle, vehicleDossier) for vehicle in vehicles)) and not isNotified

    def __getVehicleCDsWereInBattle(self):
        accDossier = self.__itemsCache.items.getAccountDossier(None)
        return set(accDossier.getTotalStats().getVehicles().keys()) if accDossier else set()

    def __getActions(self, vehicleCD=None, nationID=None):

        def _filterFunc(actionID):
            vehicles = self.__getVehicles(actionID, nationID)
            if vehicleCD is not None:
                return any((vehicleCD == v.intCD for v in vehicles))
            else:
                return bool(vehicles) if nationID is not None else False

        return filter(_filterFunc, self.actions)

    def __onInventoryUpdated(self, _):
        self.__update()

    @staticmethod
    def __eventFilter():
        return lambda q: TECH_TREE_ACTION_POSTFIX in q.getID()
