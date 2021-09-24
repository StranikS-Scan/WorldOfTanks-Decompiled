# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_carousel_view.py
import BigWorld
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.impl.lobby.wt_event.tooltips.wt_event_carousel_vehicle_tooltip_view import WtEventCarouselVehicleTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_ammunition_tooltip_view import WtEventAmmunitionTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from gui.impl.gen.view_models.views.lobby.wt_event.carousel_tank_model import CarouselTankModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_equipment_slot_model import WtEquipmentSlotModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_carousel_view_model import WtEventCarouselViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_equipment_group_model import WtEquipmentGroupModel
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.meta.WTEventCarouselWidgetMeta import WTEventCarouselWidgetMeta
from gui.server_events.events_constants import EVENT_GROUP_PREFIX
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.shop import showBuyLootboxOverlay
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS as _TAGS, getIconResourceName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import first
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IGameEventController

class VignetteHolder(object):
    __slots__ = ('__defaultIntensity',)
    _VIGNETTE_INTENSITY = 0.85

    def __init__(self):
        vignetteSettings = BigWorld.WGRenderSettings().getVignetteSettings()
        self.__defaultIntensity = vignetteSettings.w
        vignetteSettings.w = self._VIGNETTE_INTENSITY
        BigWorld.WGRenderSettings().setVignetteSettings(vignetteSettings)

    def __del__(self):
        vignetteSettings = BigWorld.WGRenderSettings().getVignetteSettings()
        vignetteSettings.w = self.__defaultIntensity
        BigWorld.WGRenderSettings().setVignetteSettings(vignetteSettings)


class WTEventCarouselWidget(WTEventCarouselWidgetMeta, WTEventInjectWidget):

    def _makeInjectView(self):
        return WTEventCarouselView()


class WTEventCarouselView(ViewImpl, IGlobalListener):
    __gameEventCtrl = dependency.descriptor(IGameEventController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCarousel(), flags=ViewFlags.COMPONENT, model=WtEventCarouselViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__vignette = None
        self.__isInBattle = False
        super(WTEventCarouselView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__update()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = createTooltipData(isSpecial=True, specialAlias=event.getArgument('tooltipId'), specialArgs=(event.getArgument('id'), 1))
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        return super(WTEventCarouselView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventTicketTooltipView():
            return WtEventTicketTooltipView()
        if contentID == R.views.lobby.wt_event.tooltips.WtEventCarouselVehicleTooltipView():
            return WtEventCarouselVehicleTooltipView(vehInvID=event.getArgument('id'))
        return WtEventAmmunitionTooltipView(intCD=event.getArgument('id')) if contentID == R.views.lobby.wt_event.tooltips.WtEventAmmunitionTooltipView() else super(WTEventCarouselView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WTEventCarouselView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__update()
        self.__vignette = VignetteHolder()

    def _finalize(self):
        super(WTEventCarouselView, self)._finalize()
        self.__removeListeners()
        self.__vignette = None
        return

    def __addListeners(self):
        self.startGlobalListening()
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__prebattleVehicle.onChanged += self.__onVehicleChanged
        self.viewModel.onClick += self.__onCarouselClick
        self.viewModel.status.onBuyTicket += self.__onBuyTicketClick
        self.viewModel.status.onOpenTasks += self.__onOpenMissionsClick
        g_eventBus.addListener(events.HangarSimpleEvent.UPDATE_CAROUSEL_VEHICLE_STATES, self.__updateStates, EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        self.stopGlobalListening()
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__prebattleVehicle.onChanged -= self.__onVehicleChanged
        self.viewModel.onClick -= self.__onCarouselClick
        self.viewModel.status.onBuyTicket -= self.__onBuyTicketClick
        self.viewModel.status.onOpenTasks -= self.__onOpenMissionsClick
        g_eventBus.removeListener(events.HangarSimpleEvent.UPDATE_CAROUSEL_VEHICLE_STATES, self.__updateStates, EVENT_BUS_SCOPE.LOBBY)

    def __onCarouselClick(self, args):
        vehicle = self.__itemsCache.items.getVehicle(args.get('id'))
        self.__prebattleVehicle.select(vehicle)

    def __onBuyTicketClick(self):
        showBuyLootboxOverlay()

    def __onOpenMissionsClick(self):
        showMissionsCategories(groupID=EVENT_GROUP_PREFIX)

    def __onVehicleChanged(self):
        self.__update()

    def __onSyncCompleted(self, _, __):
        self.__update()

    def __updateStates(self, _):
        self.__update()

    def __update(self):
        vehicle = self.__prebattleVehicle.item
        if not vehicle:
            return
        if self.__isInBattle != vehicle.isInBattle:
            self.__isInBattle = vehicle.isInBattle
            g_eventBus.handleEvent(events.FightButtonEvent(events.FightButtonEvent.FIGHT_BUTTON_UPDATE), scope=EVENT_BUS_SCOPE.LOBBY)
        with self.viewModel.transaction() as trx:
            _updateDisableState(trx, vehicle)
            _fillStatus(trx.status, vehicle)
            _fillVehicles(trx.tanks, vehicle)
            _fillEquipment(trx.equipment, vehicle)


@dependency.replace_none_kwargs(gameEventCtrl=IGameEventController)
def _updateDisableState(model, vehicle, gameEventCtrl=None):
    pInfo = gameEventCtrl.prbDispatcher.getPlayerInfo()
    isReadyToPlatoonBattle = vehicle.isInUnit and pInfo.isReady
    model.setIsDisableAll(isReadyToPlatoonBattle)


@dependency.replace_none_kwargs(gameEventCtrl=IGameEventController)
def _fillStatus(model, item, gameEventCtrl=None):
    eventType = first(item.tags & _TAGS.EVENT_VEHS)
    model.setTitle(item.userName)
    model.setIcon(R.images.gui.maps.icons.wtevent.hangar.dyn(eventType)())
    model.setIsHunter(_TAGS.EVENT_HUNTER in item.tags)
    model.setIsSpecial(_TAGS.EVENT_SPECIAL_BOSS in item.tags)
    model.setQuantity(gameEventCtrl.getTicketCount())


@dependency.replace_none_kwargs(itemsCache=IItemsCache, gameEventCtrl=IGameEventController)
def _fillVehicles(array, item, itemsCache=None, gameEventCtrl=None):
    vehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_ANY_TAGS(_TAGS.EVENT_VEHS))
    array.clearItems()
    state = gameEventCtrl.prbDispatcher.getFunctionalState()
    pinfo = gameEventCtrl.prbDispatcher.getPlayerInfo()
    isReadyToPlatoonBattle = item.isInUnit and pinfo.isReady
    for vehicle in vehicles.itervalues():
        iconName = getIconResourceName(vehicle.name)
        if _TAGS.EVENT_BOSS in vehicle.tags and _TAGS.EVENT_SPECIAL_BOSS not in vehicle.tags:
            if gameEventCtrl.hasEnoughTickets():
                iconName += '_alt'
        model = CarouselTankModel()
        model.setId(vehicle.invID)
        model.setIcon(R.images.gui.maps.icons.vehicle.c_216x110.dyn(iconName)())
        model.setIconSmall(R.images.gui.maps.icons.vehicle.dyn(iconName)())
        model.setTitle(vehicle.userName)
        model.setIsHunter(_TAGS.EVENT_HUNTER in vehicle.tags)
        model.setInBattle(vehicle.isInBattle)
        model.setIsSpecial(_TAGS.EVENT_SPECIAL_BOSS in vehicle.tags)
        model.setSelected(vehicle == item)
        model.setInPlatoon(vehicle == item and isReadyToPlatoonBattle)
        if _TAGS.EVENT_BOSS in vehicle.tags:
            model.setQuantity(gameEventCtrl.getTicketCount())
            model.setUnsuitable(state.isInUnit())
        array.addViewModel(model)

    array.invalidate()


def _fillEquipment(array, item):
    array.clearItems()
    shells = []
    abilities = []
    regulars = []
    passives = []
    for eq in item.shells.layout:
        if not eq:
            continue
        shells.append(eq)

    for eq in item.consumables.layout:
        if not eq:
            continue
        if 'hidden' in eq.tags:
            continue
        if 'repairkit' in eq.tags or 'medkit' in eq.tags:
            regulars.append(eq)
        if 'eventItem' in eq.tags:
            abilities.append(eq)
        if 'eventPassiveItem' in eq.tags:
            passives.append(eq)

    for layout in (shells,
     abilities,
     regulars,
     passives):
        if not layout:
            continue
        groupmodel = WtEquipmentGroupModel()
        for eq in layout:
            if not eq:
                continue
            model = WtEquipmentSlotModel()
            model.setId(eq.intCD)
            model.setIcon(R.images.gui.maps.icons.artefact.dyn(eq.descriptor.iconName)())
            if eq.itemTypeID == GUI_ITEM_TYPE.SHELL:
                model.setIsInfinite(True)
            if eq.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT and eq in regulars:
                model.setTooltipId(TOOLTIPS_CONSTANTS.HANGAR_MODULE)
            groupmodel.group.addViewModel(model)

        array.addViewModel(groupmodel)

    array.invalidate()
