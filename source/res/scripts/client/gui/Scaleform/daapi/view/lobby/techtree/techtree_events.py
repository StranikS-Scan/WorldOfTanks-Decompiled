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

    def getUserName(self):
        return self.__getUserName(self.__getActualEventID())

    def getVehicles(self, nationID=None):
        vehicles = set()
        for actionID in self.__actions:
            vehicles.update([ v.intCD for v in self.__getVehicles(actionID, nationID) ])

        return vehicles

    def setNationViewed(self, nationID):
        for actionID in self.__getEvents(nationID):
            self.__settings.selectNation(actionID, nationID)

        self.onSettingsChanged()

    def getNations(self, unviewed=False):
        if not self.actions:
            return set()
        nationIDs = set.union(*[ self.__getNations(actionID) for actionID in self.__actions ])
        return nationIDs.difference(self.__settings.viewedNations()) if unviewed else nationIDs

    def getTimeTillEnd(self):
        actionID = self.__getActualEventID()
        return 0 if actionID is None else self.__actions[actionID].getFinishTimeLeft()

    def getFinishTime(self):
        actionID = self.__getActualEventID()
        return 0 if actionID is None else self.__actions[actionID].getFinishTime()

    def hasActiveAction(self, vehicleCD, nationID=None):
        return vehicleCD in self.getVehicles(nationID) if nationID not in self.__settings.viewedNations() else False

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

    def __getEvents(self, nationID):
        return (actionID for actionID in self.__actions if nationID in self.__getNations(actionID))

    def __getActualEventID(self):
        return None if not self.__actions else max(((k, v.getFinishTime()) for k, v in self.__actions.items()), key=operator.itemgetter(1))[0]

    def __onAccountShowGUI(self, ctx):
        self.__notifyAboutExpiration()

    def __notifyAboutExpiration(self):
        for aID, action in self.__actions.items():
            timeLeft = action.getFinishTimeLeft()
            if ONE_DAY <= timeLeft <= _NOTIFY_THRESHOLD and not self.__settings.isNotified(aID):
                if not self.__actionNotifierCondition(aID):
                    continue
                self.__systemMessages.proto.serviceChannel.pushClientMessage({'actionName': self.__getUserName(aID),
                 'timeLeft': timeLeft}, SCH_CLIENT_MSG_TYPE.TECH_TREE_ACTION_DISCOUNT)
                self.__settings.setNotified(aID)

    def __actionNotifierCondition(self, actionID):
        vehicleDossier = self.__getVehicleCDsWereInBattle()

        def invalidateVehicle(vehicle, dossier):
            return vehicle.level == 10 and not vehicle.isInInventory and vehicle.intCD not in dossier

        vehicles = self.__items[actionID].keys()
        return any((invalidateVehicle(vehicle, vehicleDossier) for vehicle in vehicles))

    def __getVehicleCDsWereInBattle(self):
        accDossier = self.__itemsCache.items.getAccountDossier(None)
        return set(accDossier.getTotalStats().getVehicles().keys()) if accDossier else set()

    def __onInventoryUpdated(self, _):
        self.__update()

    @staticmethod
    def __eventFilter():
        return lambda q: TECH_TREE_ACTION_POSTFIX in q.getID()
