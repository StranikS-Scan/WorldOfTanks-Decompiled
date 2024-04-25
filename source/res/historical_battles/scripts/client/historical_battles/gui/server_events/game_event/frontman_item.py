# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/frontman_item.py
import typing
import BigWorld
import HBAccountSettings
from AccountCommands import LOCK_REASON
from helpers import dependency
from historical_battles.gui.server_events.game_event.game_event_progress import ProgressItemsController, GameEventCollection, GameEventProgressQuest, GameEventProgressItemEmpty
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import AccountSettingsKeys, FRONTMAN_PROGRESS_POINTS_TOKEN_TPL, FRONTMAN_PROGRESS_QUEST_GROUP_TPL
from shared_utils import first, findFirst
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Dict, Optional
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.event_items import Quest

@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getFrontmanProgressItem(frontmanID, eventsCache=None):
    quest = first((q for q in eventsCache.getHiddenQuests().itervalues() if q.getGroupID() == FRONTMAN_PROGRESS_QUEST_GROUP_TPL.format(frontmanID)))
    return GameEventProgressQuest(quest, FRONTMAN_PROGRESS_POINTS_TOKEN_TPL.format(frontmanID)) if quest else GameEventProgressItemEmpty(None)


class FrontmenController(ProgressItemsController):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, frontID):
        super(FrontmenController, self).__init__()
        self.frontID = frontID
        self.selectedFrontmanID = None
        return

    def start(self):
        super(FrontmenController, self).start()
        settings = HBAccountSettings.getSettings(AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONTMEN)
        self.selectedFrontmanID = settings.get(self.frontID)
        if self.selectedFrontmanID is None and self.getItems() or self.selectedFrontmanID not in self.getActiveItemIDs():
            self.setSelectedFrontmanID(sorted(self.getItems().keys())[0])
        return

    def getSelectedFrontmanID(self):
        return self.selectedFrontmanID

    def setSelectedFrontmanID(self, value):
        isChanged = value in self.getActiveItemIDs() and self.selectedFrontmanID != value
        if isChanged:
            self.selectedFrontmanID = value
        return isChanged

    def getSelectedFrontman(self):
        return self.getItems().get(self.getSelectedFrontmanID(), None)

    def getInstanceClass(self):
        return FrontmanItem

    def getActiveItemIDs(self):
        return [ key for key, value in self.gameEventController.getGameEventData().get('frontmen', {}).items() if value.get('frontID', None) == self.frontID ]


class FrontmanItem(GameEventCollection):
    itemsCache = dependency.descriptor(IItemsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, frontmanID):
        super(FrontmanItem, self).__init__()
        self._id = frontmanID
        self.roleQuest = None
        return

    @property
    def frontmenLockCache(self):
        return BigWorld.player().HBAccountComponent.frontmenLock or {}

    def init(self):
        super(FrontmanItem, self).init()
        self.roleQuest = getFrontmanProgressItem(self._id)

    def getID(self):
        return self._id

    def getFrontID(self):
        return self._getFrontmenData().get('frontID', None)

    def getSelectedVehicle(self):
        vehTypeCD = self._getSelectedVehicleConfig()['vehTypeCD']
        return self.itemsCache.items.getStockVehicle(vehTypeCD)

    def getIsProfiledVehicle(self):
        return self._getSelectedVehicleConfig()['isProfiled']

    def setNextSelectedVehicle(self):
        frontmenSettings = HBAccountSettings.getSettings(AccountSettingsKeys.FRONTMEN_SELECTED_VEHICLE)
        frontmenSettings[self._id] = self._getNextVehicleId()
        HBAccountSettings.setSettings(AccountSettingsKeys.FRONTMEN_SELECTED_VEHICLE, frontmenSettings)

    def getVehicles(self):
        return self._getFrontmenData().get('vehicles', [])

    def getRoleID(self):
        return self._getFrontmenData().get('roleID', 0)

    def hasRole(self):
        return True

    def getVehicleAbilities(self, vehicleIndex):
        return self.getVehicles()[vehicleIndex].get('abilities', [])

    def getVehicleLevel(self):
        return self._getSelectedVehicleConfig()['level']

    def getNextVehicleCD(self):
        vehicles = self.getVehicles()
        return vehicles[self._getNextVehicleId()]['vehTypeCD'] if vehicles else None

    def getSelectedVehicleAbilities(self):
        return self.getVehicleAbilities(self._getSelectedVehicleIndex())

    def getRoleAbility(self):
        roleAbilities = self._getFrontmenData().get('roleAbilities', [])
        return roleAbilities.get('eqId')

    def isLocked(self):
        return self.getID() in self.frontmenLockCache

    def isInBattle(self):
        return self._getLockReason() == LOCK_REASON.ON_ARENA

    def isInUnit(self):
        return self._getLockReason() == LOCK_REASON.UNIT

    def isHeroVehicle(self):
        return self._getSelectedVehicleConfig().get('isHero', False)

    def getHeroVehicle(self):
        heroVehicle = self._getHeroVehicleConfig()
        return self.itemsCache.items.getItemByCD(heroVehicle['vehTypeCD']) if heroVehicle else None

    def _onSyncCompleted(self):
        self.roleQuest = getFrontmanProgressItem(self._id)
        self.onItemsUpdated()

    def _getFrontmenData(self):
        return self.gameEventController.getGameEventData().get('frontmen', {}).get(self.getID(), None)

    def _getSelectedVehicleIndex(self):
        frontmenSettings = HBAccountSettings.getSettings(AccountSettingsKeys.FRONTMEN_SELECTED_VEHICLE)
        return frontmenSettings.get(self._id, 0)

    def _getSelectedVehicleConfig(self):
        return self.getVehicles()[self._getSelectedVehicleIndex()]

    def _getLockReason(self):
        if not self.isLocked():
            return LOCK_REASON.NONE
        _, lockReason = self.frontmenLockCache.get(self.getID(), (0, LOCK_REASON.NONE))
        return lockReason

    def _getNextVehicleId(self):
        nextVehicleIdx = self._getSelectedVehicleIndex() + 1
        if nextVehicleIdx >= len(self.getVehicles()):
            nextVehicleIdx = 0
        return nextVehicleIdx

    def _getHeroVehicleConfig(self):
        return findFirst(lambda vehicle: vehicle.get('isHero', False), self.getVehicles())
