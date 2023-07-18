# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/epicBattle/carousel_data_provider.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import UNLOCK_VEHICLES_IN_BATTLE_HINTS
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import isVehLevelUnlockableInBattle
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider, _SUPPLY_ITEMS, _FRONT_SUPPLY_ITEMS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicBattleCarouselDataProvider(HangarCarouselDataProvider):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, carouselFilter, itemsCache):
        super(EpicBattleCarouselDataProvider, self).__init__(carouselFilter, itemsCache)
        self.__separatorItems = []
        self.__filteredSeparators = []
        self.__indexToScroll = -1

    def _getFrontIndices(self):
        previousItemsCount = len(self._vehicles) + len(_SUPPLY_ITEMS.ALL) + len(self.__separatorItems)
        return [ previousItemsCount + idx for idx in _FRONT_SUPPLY_ITEMS.ALL ]

    @property
    def collection(self):
        return self._vehicleItems + self.__separatorItems + self._supplyItems + self._frontSupplyItems

    def getCurrentVehiclesCount(self):
        result = super(EpicBattleCarouselDataProvider, self).getCurrentVehiclesCount()
        return result - len(self.__filteredSeparators)

    def clear(self):
        super(EpicBattleCarouselDataProvider, self).clear()
        self.__separatorItems = []
        self.__filteredSeparators = []
        self.__indexToScroll = -1

    def getIndexToScroll(self):
        return -1 if self.__isHintsShown() else self.__indexToScroll

    def updateVehicles(self, vehiclesCDs=None, filterCriteria=None, forceUpdate=False):
        if self.__epicController.isUnlockVehiclesInBattleEnabled() and not self.__separatorItems:
            self.buildList()
        else:
            super(EpicBattleCarouselDataProvider, self).updateVehicles(vehiclesCDs, filterCriteria, forceUpdate)

    def applyFilter(self, forceApply=False):
        prevFilteredIndices = self._filteredIndices[:]
        prevSelectedIdx = self._selectedIdx
        self._filteredIndices = []
        self._selectedIdx = -1
        self.__indexToScroll = -1
        isSeparatorsNeeded = self.__epicController.isUnlockVehiclesInBattleEnabled()
        vehLevelsToScroll = self.__epicController.getModeSettings().unlockableInBattleVehLevels
        visibleVehiclesIntCDs = [ vehicle.intCD for vehicle in self._getCurrentVehicles() ]
        sortedVehicleIndices = self._getSortedIndices()
        self.__filteredSeparators = []
        frontAdded = False
        for idx in sortedVehicleIndices:
            vehicle = self._vehicles[idx]
            if vehicle.intCD in visibleVehiclesIntCDs:
                if isSeparatorsNeeded and vehicle.level not in self.__filteredSeparators:
                    separatorIdx = len(self._vehicles) + (vehicle.level - 1)
                    if vehicle.level in vehLevelsToScroll:
                        self.__indexToScroll = len(self._filteredIndices)
                    self._filteredIndices.append(separatorIdx)
                    self.__filteredSeparators.append(vehicle.level)
                    if not frontAdded:
                        self._filteredIndices += self._getFrontAdditionalItemsIndexes()
                        frontAdded = True
                self._filteredIndices.append(idx)
                if self._currentVehicleInvID == vehicle.invID:
                    self._selectedIdx = len(self._filteredIndices) - 1

        self._filteredIndices += self._getAdditionalItemsIndexes()
        needUpdate = forceApply or prevFilteredIndices != self._filteredIndices or prevSelectedIdx != self._selectedIdx
        if needUpdate:
            self._filterByIndices()

    def _buildVehicleItems(self):
        self.__buildSeparatorItems()
        super(EpicBattleCarouselDataProvider, self)._buildVehicleItems()

    def __buildSeparatorItems(self):
        self.__separatorItems = []
        if not self.__epicController.isUnlockVehiclesInBattleEnabled():
            return
        for level in range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1):
            self.__separatorItems.append({'levelInfo': self.__getLevelInfo(level),
             'clickEnabled': isVehLevelUnlockableInBattle(level)})

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        isForbidden = vehicle.intCD in cls.__epicController.getForbiddenVehicles()
        return (not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isOnlyForBattleRoyaleBattles,
         not isForbidden and not cls._isSuitableForQueue(vehicle),
         vehicle.level,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    @classmethod
    def _isSuitableForQueue(cls, vehicle):
        controller = cls.__epicController
        return vehicle.level in controller.getValidVehicleLevels() and vehicle.intCD not in controller.getForbiddenVehicles()

    def _buildVehicle(self, vehicle):
        result = super(EpicBattleCarouselDataProvider, self)._buildVehicle(vehicle)
        state, _ = vehicle.getState()
        resShortCut = R.strings.epic_battle.epicBattlesCarousel
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            header = resShortCut.lockedTooltip.header()
            if vehicle.level in self.__epicController.getValidVehicleLevels():
                body = resShortCut.wrongMode.body()
            else:
                body = resShortCut.lockedTooltip.body()
            result['lockedTooltip'] = makeTooltip(backport.text(header), backport.text(body))
        if state == Vehicle.VEHICLE_STATE.WILL_BE_UNLOCKED_IN_BATTLE:
            result['unlockedInBattle'] = True
        result['xpImgSource'] = ''
        result['debutBoxesImgSource'] = ''
        return result

    def _getSupplyIndices(self):
        return [ len(self._vehicles + self.__separatorItems) + idx for idx in _SUPPLY_ITEMS.ALL ]

    def __getLevelInfo(self, level):
        if isVehLevelUnlockableInBattle(level):
            levelTxt = text_styles.neutral(backport.text(R.strings.epic_battle.epicBattlesCarousel.lobby.levelInfo.level(), lvl=int2roman(level)))
            levelInfoText = backport.text(R.strings.epic_battle.epicBattlesCarousel.lobby.levelInfo(), level=levelTxt)
            return {'level': level,
             'isCollapsed': self.__isHintsShown(),
             'isCollapsible': True,
             'infoText': levelInfoText}
        return {'level': level,
         'isCollapsed': True,
         'isCollapsible': False,
         'infoText': ''}

    def __isHintsShown(self):
        hintCount = AccountSettings.getSettingsDefault(UNLOCK_VEHICLES_IN_BATTLE_HINTS)
        battleCount = self.__epicController.getStats().battleCount
        return battleCount > hintCount
