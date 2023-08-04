# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/limited_ui/lui_tokens_storage.py
from collections import namedtuple
from itertools import chain
import typing
from future.utils import itervalues
import Event
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS, UI_STORAGE_KEYS
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL, BATTLE_MODE_VEHICLE_TAGS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.system_factory import collectLimitedUITokens, registerLimitedUITokens
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import getTypeOfCompactDescr
from personal_missions import PM_BRANCH
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from typing import Optional, Union, Tuple, Callable
LimitedUITokenInfo = namedtuple('LimitedUITokenInfo', ('tokenID', 'clazz', 'args'))
LimitedUITokenInfo.__new__.__defaults__ = ('', None, None)

class LimitedUICondition(object):
    __slots__ = ('__value', '__tokenID', '__isActive', 'onConditionValueUpdated')

    def __init__(self, tokenID):
        self.__tokenID = tokenID
        self.__value = None
        self.__isActive = False
        self.onConditionValueUpdated = Event.Event()
        return

    def initialize(self, *args):
        pass

    def tokenID(self):
        return self.__tokenID

    def value(self):
        return self.__value if self.__isActive else self._getValue()

    def activate(self):
        self.__subscribe()
        self.__value = self._getValue()
        self.__isActive = True

    def deactivate(self):
        self.__isActive = False
        self.__unsubscribe()
        self.__value = None
        return

    def finalize(self):
        self.__unsubscribe()
        self.onConditionValueUpdated.clear()

    def _getValue(self):
        raise NotImplementedError

    def _getEvents(self):
        return tuple()

    def _getCallbacks(self):
        return tuple()

    def __subscribe(self):
        for event, handler in self._getEvents():
            event += handler

        g_clientUpdateManager.addCallbacks(dict(self._getCallbacks()))

    def __unsubscribe(self):
        for event, handler in self._getEvents():
            event -= handler

        g_clientUpdateManager.removeObjectCallbacks(self)

    def _update(self, *_, **__):
        newValue = self._getValue()
        if self.__value != newValue:
            self.__value = newValue
            self.onConditionValueUpdated(self.__tokenID)


class _PermanentTrue(LimitedUICondition):
    __slots__ = ()

    def _getValue(self):
        return True


class _PermanentFalse(LimitedUICondition):
    __slots__ = ()

    def _getValue(self):
        return False


class _BattleCountCondition(LimitedUICondition):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)

    def _getValue(self):
        return 0 if not self.__itemsCache.items.stats.isSynced() else self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()

    def _getEvents(self):
        return ((g_playerEvents.onDossiersResync, self._update), (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted))

    def __onSyncCompleted(self, reason, diff):
        if reason in (CACHE_SYNC_REASON.SHOW_GUI, CACHE_SYNC_REASON.CLIENT_UPDATE, CACHE_SYNC_REASON.DOSSIER_RESYNC):
            self._update()


class _BattleMattersCompletedQuests(LimitedUICondition):
    __slots__ = ()
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def _getValue(self):
        return len(self.__battleMattersController.getCompletedBattleMattersQuests())

    def _getEvents(self):
        return ((self.__eventsCache.onSyncCompleted, self._update),)


class _VehicleCondition(LimitedUICondition):
    __slots__ = ('__criteria',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tokenID):
        super(_VehicleCondition, self).__init__(tokenID)
        self.__criteria = None
        return

    def initialize(self, level, *args):
        self.__criteria = self._getCriteria(level)

    def _getCriteria(self, level):
        criteria = REQ_CRITERIA.VEHICLE.LEVELS(range(level, MAX_VEHICLE_LEVEL + 1))
        criteria |= ~REQ_CRITERIA.VEHICLE.RENT
        criteria |= ~REQ_CRITERIA.SECRET
        criteria |= ~REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(BATTLE_MODE_VEHICLE_TAGS)
        return criteria

    def _getValue(self):
        return 0 if not self.__itemsCache.isSynced() else len(self.__itemsCache.items.getVehicles(self.__criteria))


class _MinVehicleLevel(_VehicleCondition):
    __slots__ = ()

    def _getCriteria(self, level):
        criteria = super(_MinVehicleLevel, self)._getCriteria(level)
        criteria |= REQ_CRITERIA.INVENTORY
        return criteria

    def _getCallbacks(self):
        return (('inventory.1', self._update),)


class _MinNonPremiumVehicleLevel(_MinVehicleLevel):
    __slots__ = ()

    def _getCriteria(self, level):
        criteria = super(_MinNonPremiumVehicleLevel, self)._getCriteria(level)
        criteria |= ~REQ_CRITERIA.VEHICLE.PREMIUM
        return criteria


class _MinUnlockedVehicleLevel(_VehicleCondition):
    __slots__ = ()

    def _getCriteria(self, level):
        criteria = super(_MinUnlockedVehicleLevel, self)._getCriteria(level)
        criteria |= ~REQ_CRITERIA.VEHICLE.PREMIUM
        criteria |= ~REQ_CRITERIA.CUSTOM(lambda item: item.isSpecial)
        criteria |= REQ_CRITERIA.UNLOCKED
        return criteria

    def _getCallbacks(self):
        return (('stats.unlocks', self.__onUnlocksUpdate),)

    def __onUnlocksUpdate(self, unlocks):
        if any((getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE for intCD in unlocks)):
            self._update()


class _DailyMissionsCompletedCount(LimitedUICondition):
    __slots__ = ()
    __eventsCache = dependency.descriptor(IEventsCache)

    def _getValue(self):
        quests = self.__eventsCache.getDailyQuests(filterFunc=lambda q: q.isCompleted())
        return len(quests.keys())

    def _getEvents(self):
        return ((self.__eventsCache.onSyncCompleted, self._update),)


class _BattlePassPoints(LimitedUICondition):
    __slots__ = ()
    __battlePass = dependency.descriptor(IBattlePassController)

    def _getValue(self):
        chaptersIDs = self.__battlePass.getChapterIDs()
        points = sum([ self.__battlePass.getPointsInChapter(chapterID) for chapterID in chaptersIDs ])
        freePoints = self.__battlePass.getFreePoints()
        return points + freePoints

    def _getEvents(self):
        return ((self.__battlePass.onPointsUpdated, self._update),)


class _PersonalMissionsActive(LimitedUICondition):
    __slots__ = ()
    __eventsCache = dependency.descriptor(IEventsCache)

    def _getValue(self):
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            operations = self.__eventsCache.getPersonalMissions().getOperationsForBranch(branch)
            if any((operation.isInProgress() for operation in itervalues(operations))):
                return True

        return False

    def _getEvents(self):
        return ((self.__eventsCache.onSyncCompleted, self._update), (self.__eventsCache.onProgressUpdated, self._update))


class _BluePrintsAvailability(LimitedUICondition):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)

    def _getValue(self):
        return False if not self.__itemsCache.isSynced() else self.__itemsCache.items.blueprints.hasBlueprintsOrFragments()

    def _getCallbacks(self):
        return ('blueprints', self._update)


class _PersonalReservesAvailability(LimitedUICondition):
    __slots__ = ()
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def _getValue(self):
        return False if not self.__itemsCache.isSynced() else bool(self.__goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_ACCOUNT))

    def _getEvents(self):
        return ((self.__itemsCache.onSyncCompleted, self._update),)


class _WereRealMoneyExpenses(LimitedUICondition):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __REAL_MONEY_EXPENSES_ENTITLEMENT = 'real_money_expenses'

    def _getValue(self):
        return False if not self.__itemsCache.isSynced() else self.__itemsCache.items.stats.entitlements.get(self.__REAL_MONEY_EXPENSES_ENTITLEMENT, 0) > 0

    def _getCallbacks(self):
        return (('cache.entitlements', self.__updateEntitlements),)

    def __updateEntitlements(self, entitlements):
        if entitlements.get(self.__REAL_MONEY_EXPENSES_ENTITLEMENT, 0):
            self._update()


class _LootboxesAvailability(LimitedUICondition):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)

    def _getValue(self):
        uiStorage = self.__settingsCore.serverSettings.getUIStorage2()
        isEntryPointEnabled = uiStorage.get(UI_STORAGE_KEYS.GUI_LOOTBOXES_ENTRY_POINT)
        return isEntryPointEnabled

    def _getEvents(self):
        return ((self.__settingsCore.onSettingsChanged, self._updateLootBoxes),)

    def _updateLootBoxes(self, diff):
        if SETTINGS_SECTIONS.UI_STORAGE_2 in diff:
            self._update()


_VEHICLE_LEVEL_TOKENS = tuple((tokenInfo for tokenInfo in chain.from_iterable(((LimitedUITokenInfo('minVehicleLevel_{}'.format(vehLevel), _MinVehicleLevel, (vehLevel,)), LimitedUITokenInfo('minNonPremiumVehicleLevel_{}'.format(vehLevel), _MinNonPremiumVehicleLevel, (vehLevel,)), LimitedUITokenInfo('minUnlockedVehicleLevel_{}'.format(vehLevel), _MinUnlockedVehicleLevel, (vehLevel,))) for vehLevel in range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)))))
_REGISTER_TOKENS = (LimitedUITokenInfo('permanentTrue', _PermanentTrue, None),
 LimitedUITokenInfo('permanentFalse', _PermanentFalse, None),
 LimitedUITokenInfo('battlesCount', _BattleCountCondition, None),
 LimitedUITokenInfo('bmCompletedQuests', _BattleMattersCompletedQuests, None),
 LimitedUITokenInfo('dailyMissionsCompleted', _DailyMissionsCompletedCount, None),
 LimitedUITokenInfo('battlePassPoints', _BattlePassPoints, None),
 LimitedUITokenInfo('pmHasActiveMission', _PersonalMissionsActive, None),
 LimitedUITokenInfo('hasBlueprint', _BluePrintsAvailability, None),
 LimitedUITokenInfo('hasPersonalReserve', _PersonalReservesAvailability, None),
 LimitedUITokenInfo('wereRealMoneyExpenses', _WereRealMoneyExpenses, None),
 LimitedUITokenInfo('hadLootboxes', _LootboxesAvailability, None)) + _VEHICLE_LEVEL_TOKENS
registerLimitedUITokens(_REGISTER_TOKENS)

def getTokensInfo():
    return collectLimitedUITokens()
