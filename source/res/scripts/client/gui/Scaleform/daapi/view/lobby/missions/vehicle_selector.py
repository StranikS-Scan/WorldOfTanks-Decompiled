# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/vehicle_selector.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import getVehicleDataVO, CarouselDataProvider, getStatusStrings
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import BasicCriteriesGroup
from gui.Scaleform.daapi.view.meta.MissionsVehicleSelectorMeta import MissionsVehicleSelectorMeta
from gui.Scaleform.daapi.view.meta.VehicleSelectorCarouselMeta import VehicleSelectorCarouselMeta
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.formatters import text_styles
from gui.shared.utils.requesters import REQ_CRITERIA

class MissionVehicleSelectorCarousel(VehicleSelectorCarouselMeta):

    def __init__(self):
        super(MissionVehicleSelectorCarousel, self).__init__()
        self._usedFilters = ('inventory',)
        self._carouselDPCls = _MissionsCarouselDataProvider

    def setFilter(self, idx, selected):
        self.filter.update({self._usedFilters[idx]: selected})
        self.applyFilter()

    def getSuitableVehicles(self):
        return self._carouselDP.getSuitableVehicles()

    def getSuitableVehiclesCount(self):
        return self._carouselDP.getSuitableVehiclesCount()

    def setCriteria(self, criteria, extraConditions, isForEventBattle=False):
        self._carouselDP.setCriteria(criteria, extraConditions, isForEventBattle)
        self.updateVehicles()
        self._carouselDP.applyFilter(forceApply=True)

    def _populate(self):
        super(MissionVehicleSelectorCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self._setCarouselFilters()

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(MissionVehicleSelectorCarousel, self)._dispose()

    def _setCarouselFilters(self):
        raise NotImplementedError

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == VIEW_ALIAS.VEHICLES_FILTER_POPOVER:
            view.setTankCarousel(self)


class MissionVehicleSelector(MissionsVehicleSelectorMeta):

    def __init__(self):
        super(MissionVehicleSelector, self).__init__()
        self._carousel = None
        self.__isQuestForBattleRoyale = False
        self.__isQuestForEventBattle = False
        return

    def setCriteria(self, criteria, extraConditions, isQuestForBattleRoyale=False, isForEventBattle=False):
        self.__isQuestForBattleRoyale = isQuestForBattleRoyale
        self.__isQuestForEventBattle = isForEventBattle
        self._carousel.setCriteria(criteria, extraConditions, isForEventBattle)
        self.__updateSelectedVehicle()

    def _populate(self):
        super(MissionVehicleSelector, self)._populate()
        g_currentVehicle.onChanged += self.__selectVehicle
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self._carousel = self.components.get(self._getCarouselAlias())
        self.__updateSelectedVehicle()

    def _dispose(self):
        g_currentVehicle.onChanged -= self.__selectVehicle
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self._carousel = None
        super(MissionVehicleSelector, self)._dispose()
        return

    @classmethod
    def _getCarouselAlias(cls):
        raise NotImplementedError

    def __selectVehicle(self):
        self.__updateSelectedVehicle()
        self.as_closeS()

    def __onVehicleClientStateChanged(self, vehicles):
        self.__selectVehicle()

    def __updateSelectedVehicle(self):
        vehicle = g_currentVehicle.item
        suitableVehicles = self._carousel.getSuitableVehicles()
        if self.__isQuestForBattleRoyale:
            selectedVeh = None
            status = ''
            title = ''
        else:
            if suitableVehicles and vehicle and vehicle.intCD in suitableVehicles:
                selectedVeh = getVehicleDataVO(vehicle, canShowDailyXPFactor=not self.__isQuestForEventBattle)
                status = text_styles.bonusAppliedText(QUESTS.MISSIONS_VEHICLESELECTOR_STATUS_SELECTED)
            elif suitableVehicles:
                label = QUESTS.MISSIONS_VEHICLESELECTOR_STATUS_SELECT
                style = text_styles.premiumVehicleName
                selectedVeh = {'buyTank': True,
                 'iconSmall': RES_ICONS.MAPS_ICONS_LIBRARY_EMPTY_SELECTION,
                 'smallInfoText': style(label),
                 'tooltip': TOOLTIPS.MISSIONS_VEHICLE_SELECTOR_SELECT}
                status = ''
            else:
                label = QUESTS.MISSIONS_VEHICLESELECTOR_STATUS_LIST
                style = text_styles.premiumVehicleName
                selectedVeh = {'buyTank': True,
                 'iconSmall': RES_ICONS.MAPS_ICONS_LIBRARY_EMPTY_SELECTION,
                 'smallInfoText': style(label),
                 'tooltip': TOOLTIPS.MISSIONS_VEHICLE_SELECTOR_LIST}
                status = self._getNotAvailableStatusText()
            selectedVeh.update(isUseRightBtn=False)
            selectedVeh.update(clickEnabled=True)
            title = self._getTitle()
        self.as_setInitDataS({'title': title,
         'statusText': status})
        self.as_showSelectedVehicleS(selectedVeh)
        return

    def _getTitle(self):
        pass

    def _getNotAvailableStatusText(self):
        pass


class _MissionsCarouselDataProvider(CarouselDataProvider):

    def __init__(self, carouselFilter, itemsCache):
        super(_MissionsCarouselDataProvider, self).__init__(carouselFilter, itemsCache)
        self.__suitableVehiclesIDs = []
        self.__extraConditions = []
        self.isForEventBattle = False

    def setCriteria(self, criteria, extraConditions, isForEventBattle=False):
        self._baseCriteria = criteria
        self.isForEventBattle = isForEventBattle
        self.__extraConditions = extraConditions
        self._filter.reset(exceptions=('inventory',))

    def getSuitableVehicles(self):
        return self.__suitableVehiclesIDs

    def getSuitableVehiclesCount(self):
        return len(self.__suitableVehiclesIDs)

    def _dispose(self):
        self.__extraConditions = []
        super(_MissionsCarouselDataProvider, self)._dispose()

    def _addCriteria(self):
        self._addVehicleItemsByCriteria(self._baseCriteria)

    def _buildVehicleItems(self):
        self.__suitableVehiclesIDs = []
        super(_MissionsCarouselDataProvider, self)._buildVehicleItems()

    def _buildVehicle(self, vehicle):
        vehicleVO = getVehicleDataVO(vehicle, canShowDailyXPFactor=not self.isForEventBattle)
        vehicleVO.update(isUseRightBtn=False)
        xpFactor = self._itemsCache.items.shop.dailyXPFactor if not self.isForEventBattle else 1
        if vehicle.isInInventory and vehicle.activeInNationGroup:
            for condition in self.__extraConditions:
                isOk, reason = condition.isAvailableReason(vehicle)
                if not isOk:
                    smallStatus, largeStatus = getStatusStrings(reason, ctx={'factor': xpFactor})
                    vehicleVO.update(smallInfoText=smallStatus, infoText=largeStatus, lockBackground=True, clickEnabled=False, infoImgSrc='', isCritInfo=False)
                    break
            else:
                self.__suitableVehiclesIDs.append(vehicle.intCD)

        return vehicleVO


class SelectorCriteriesGroup(BasicCriteriesGroup):

    def update(self, filters):
        super(SelectorCriteriesGroup, self).update(filters)
        if filters['inventory']:
            self._criteria |= REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP
