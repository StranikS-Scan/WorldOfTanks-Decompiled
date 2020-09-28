# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_carousel_view.py
from collections import namedtuple
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.wt_event.tooltips.wt_event_vehicle_params_tooltip_view import WtEventVehicleParamsTooltipView
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from constants import PREBATTLE_TYPE
from gui.impl.gen import R
from gui.impl.lobby.wt_event.carousel_tank_status_component import CarouselTankStatusComponent
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform.daapi.view.meta.WTEventCarouselWidgetMeta import WTEventCarouselWidgetMeta
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_carousel_view_model import WtEventCarouselViewModel, CarouselTankModel, WtConsumableSlotModel
from gui.impl.backport.backport_tooltip import BackportTooltipWindow, createTooltipData
from gui.impl.lobby.wt_event.tooltips.wt_event_carousel_tooltip_view import WtEventCarouselTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_carousel_vehicle_tooltip_view import WtEventCarouselVehicleTooltipView
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from gui.prb_control.entities.listener import IGlobalListener
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.wt_event.wt_event_helpers import VignetteHolder
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IGameEventController
from items.vehicles import getItemByCompactDescr
from items.artefacts import AfterburningWT, ImpulseWT, InstantStunShootWT
EventVehicleCDs = namedtuple('EventVehicleCDs', 'hunterIntCD, bossIntCD, eliteBossIntCD')

class WTEventCarouselWidget(WTEventCarouselWidgetMeta, WTEventInjectWidget):
    __slots__ = ()

    def _makeInjectView(self):
        return WTEventCarouselView()


class WTEventCarouselView(ViewImpl, IGlobalListener):
    __slots__ = ('__vehCDs', '__eventInvVehiclesCDs', '__statusComponent', '__currentlySelectedIntCD', '__vignette')
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    eventController = dependency.descriptor(IGameEventController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCarousel(), flags=ViewFlags.COMPONENT, model=WtEventCarouselViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__vehCDs = EventVehicleCDs(hunterIntCD=self.eventController.getHunter().intCD, bossIntCD=self.eventController.getBoss().intCD, eliteBossIntCD=self.eventController.getSpecialBoss().intCD)
        self.__statusComponent = CarouselTankStatusComponent(self.__vehCDs, None)
        self.__eventInvVehiclesCDs = self.itemsCache.items.getVehicles(criteria=REQ_CRITERIA.VEHICLE.EVENT).keys()
        self.__currentlySelectedIntCD = None
        self.__vignette = None
        super(WTEventCarouselView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(WTEventCarouselView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventCarouselVehicleTooltipView():
            vehicleType = event.getArgument('vehicleType')
            return WtEventCarouselVehicleTooltipView(vehicleType)
        elif contentID == R.views.lobby.wt_event.tooltips.WtEventCarouselTooltipView():
            tokensCount = self.eventController.getWtEventTokensCount()
            return WtEventCarouselTooltipView(ticketsCount=tokensCount)
        elif contentID == R.views.lobby.wt_event.tooltips.WtEventVehicleParamsTooltipView():
            isShell = event.getArgument('isShell')
            intCD = int(event.getArgument('intCD'))
            return WtEventVehicleParamsTooltipView(intCD=intCD, isShell=isShell)
        else:
            return None

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
                return window
        return super(WTEventCarouselView, self).createToolTip(event)

    def _onLoaded(self):
        super(WTEventCarouselView, self)._onLoaded()
        Waiting.hide('loadPage')

    def _onLoading(self, *args, **kwargs):
        super(WTEventCarouselView, self)._onLoading()
        Waiting.show('loadPage')
        if (not g_currentVehicle.isPresent() or not g_currentVehicle.item.isEvent) and self.eventController.isEventPrbActive():
            g_currentVehicle.selectVehicle(None)
        self.__statusComponent.init(self.viewModel.status)
        self.__fillVehicles(selectedVehCD=g_currentVehicle.item.intCD if g_currentVehicle.item is not None else None)
        self.__addListeners()
        return

    def _initialize(self, *args, **kwargs):
        super(WTEventCarouselView, self)._initialize(*args, **kwargs)
        self.__vignette = VignetteHolder()

    def _finalize(self):
        super(WTEventCarouselView, self)._finalize()
        self.__removeListeners()
        self.__statusComponent.destroy()
        self.__vignette = None
        return

    def __addListeners(self):
        self.viewModel.onClick += self.__onClick
        self.startGlobalListening()
        self.itemsCache.onSyncCompleted += self.__onItemsCacheSyncCompleted
        self.eventsCache.onSyncCompleted += self.__onEventCacheSync
        g_currentVehicle.onChanged += self.__onVehicleChanged
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.__wtEventSelectedOff, EVENT_BUS_SCOPE.LOBBY)
        self.__statusComponent.addListeners()

    def __removeListeners(self):
        self.viewModel.onClick -= self.__onClick
        self.stopGlobalListening()
        self.itemsCache.onSyncCompleted -= self.__onItemsCacheSyncCompleted
        self.eventsCache.onSyncCompleted -= self.__onEventCacheSync
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self.__statusComponent.removeListeners()
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.__wtEventSelectedOff, EVENT_BUS_SCOPE.LOBBY)

    def __wtEventSelectedOff(self, _):
        self.__currentlySelectedIntCD = None
        return

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__fillVehicles()

    def onPrbEntitySwitched(self):
        self.__fillVehicles()

    def __onClick(self, args=None):
        if not self.__canChangeVehicle() or not self.eventController.eventHeroTankIsInFocus:
            return
        clickedIntCD = int(args.get('id', 0))
        if self.__currentlySelectedIntCD == clickedIntCD:
            return
        self.__currentlySelectedIntCD = clickedIntCD
        self.__selectVehicleFromEventCarousel(clickedIntCD)

    def __selectVehicleFromEventCarousel(self, vehCD):
        self.__currentlySelectedIntCD = vehCD
        veh = self.itemsCache.items.getItemByCD(vehCD)
        g_currentVehicle.selectVehicle(veh.invID)

    def __canChangeVehicle(self):
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                return permission.canChangeVehicle()
        return True

    def __onVehicleChanged(self):
        vehicleCD = g_currentVehicle.item.intCD if g_currentVehicle.item else None
        self.__fillVehicles(selectedVehCD=vehicleCD)
        return

    def __onItemsCacheSyncCompleted(self, _, diff):
        if GUI_ITEM_TYPE.VEHICLE in diff:
            self.__fillVehicles()

    def __onEventCacheSync(self):
        self.__fillVehicles()

    def __fillVehicles(self, selectedVehCD=None):
        if not self.eventController.isEventPrbActive():
            return
        else:
            self.__statusComponent.update(selectedVehCD)
            tanks = self.viewModel.tanks
            tanks.clearItems()
            tokensCount = self.eventController.getWtEventTokensCount()
            with self.viewModel.transaction() as vModelTrx:
                for vehIntCD in self.eventController.getEventVehiclesCarouselSorted():
                    if vehIntCD not in self.__eventInvVehiclesCDs:
                        continue
                    veh = self.itemsCache.items.getItemByCD(vehIntCD)
                    tank = CarouselTankModel()
                    tank.setId(veh.intCD)
                    tank.setTitle(veh.userName)
                    tank.setIsHunter(veh.intCD == self.__vehCDs.hunterIntCD)
                    tank.setInBattle(veh.isInBattle)
                    if veh.intCD == self.__vehCDs.bossIntCD:
                        tank.setQuantity(tokensCount)
                    tank.setIsSpecial(veh.intCD == self.__vehCDs.eliteBossIntCD)
                    isSelected = g_currentVehicle.item.intCD == veh.intCD
                    if selectedVehCD is not None:
                        isSelected = selectedVehCD == veh.intCD
                    tank.setSelected(isSelected)
                    tank.setInPlatoon(self.prbDispatcher.getFunctionalState().entityTypeID == PREBATTLE_TYPE.EVENT and self.prbDispatcher.getPlayerInfo().isReady and isSelected)
                    if veh.intCD in (self.__vehCDs.bossIntCD, self.__vehCDs.eliteBossIntCD):
                        if self.prbDispatcher.getFunctionalState().entityTypeID == PREBATTLE_TYPE.EVENT:
                            tank.setUnsuitable(True)
                    vModelTrx.tanks.addViewModel(tank)
                    if isSelected:
                        _WtShellSection(g_currentVehicle.item, vModelTrx.shells)
                        _WtConsumablesSection(g_currentVehicle.item, vModelTrx.consumables)

            tanks.invalidate()
            return

    def _updateShellsSection(self, vehicle, viewModel):
        _WtShellSection(vehicle, viewModel)

    def _updateAbilitiesSection(self, vehicle, viewModel):
        _WtConsumablesSection(vehicle, viewModel)

    def __getTooltipData(self, event):
        tooltipType = event.getArgument('tooltipId')
        intCD = int(event.getArgument('intCD'))
        return None if not tooltipType or not intCD else createTooltipData(isSpecial=True, specialAlias=tooltipType, specialArgs=(intCD, 1))


class WTEventCarouselWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WTEventCarouselWindow, self).__init__(WindowFlags.WINDOW, content=WTEventCarouselView(), parent=parent)


class _WtItemSection(object):
    _ArtefactData = namedtuple('_ArtefactData', ('intCD', 'quantity', 'icon', 'tooltip'))
    _INVALID_CD = 0

    def __init__(self, vehicle, viewModel):
        self._vehicle = vehicle
        self._viewModel = viewModel
        self._fillSection()

    def _fillSection(self):
        self._viewModel.clearItems()
        for itemCD in self._getItemCDs():
            if itemCD == self._INVALID_CD:
                continue
            item = self._getItemData(itemCD)
            itemModel = WtConsumableSlotModel()
            itemModel.setIntCD(item.intCD)
            itemModel.setIconSource(item.icon)
            itemModel.setQuantity(item.quantity)
            itemModel.setTooltipType(item.tooltip)
            self._viewModel.addViewModel(itemModel)

        self._viewModel.invalidate()

    def _getItemData(self, intCD):
        raise NotImplementedError

    def _getItemCDs(self):
        raise NotImplementedError

    def _getIcon(self, item):
        raise NotImplementedError


class _WtShellSection(_WtItemSection):

    def _getItemData(self, intCD):
        item = getItemByCompactDescr(intCD)
        return self._ArtefactData(intCD=intCD, quantity=-1, icon=self._getIcon(item.iconName), tooltip='')

    def _getItemCDs(self):
        return self._vehicle.shells.installed.getIntCDs()

    def _getIcon(self, iconName):
        return R.images.gui.maps.icons.wtevent.hangar.dyn(iconName)()

    def __isItemAbility(self, item):
        return isinstance(item, (AfterburningWT, ImpulseWT, InstantStunShootWT))


class _WtConsumablesSection(_WtItemSection):
    _gameEventController = dependency.descriptor(IGameEventController)

    def _getItemData(self, intCD):
        item = getItemByCompactDescr(intCD)
        tooltipID = '' if self.__isItemAbility(item) else TOOLTIPS_CONSTANTS.HANGAR_SLOT_MODULE
        return self._ArtefactData(intCD=intCD, quantity=1, icon=self._getIcon(item.iconName), tooltip=tooltipID)

    def _getItemCDs(self):
        return self._gameEventController.getVehicleEquipmentIDs(self._vehicle.descriptor)

    def _getIcon(self, iconName):
        return R.images.gui.maps.icons.artefact.dyn(iconName)()

    def __isItemAbility(self, item):
        return isinstance(item, (AfterburningWT, ImpulseWT, InstantStunShootWT))
