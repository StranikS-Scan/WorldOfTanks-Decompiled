# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_carousel_view.py
import BigWorld
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.daapi.view.meta.WTHangarBaseWidgetMeta import WTHangarBaseWidgetMeta
from gui.shop import showBuyLootboxOverlay
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWhiteTigerController
from items.vehicles import getItemByCompactDescr
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from wt_settings import g_wt_config
from white_tiger.gui.shared.event_dispatcher import showEventProgressionWindow
from white_tiger.gui.impl.lobby.tooltips.wt_event_stamp_tooltip_view import WtEventStampTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_carousel_vehicle_tooltip_view import WtCarouselVehicleTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_ammunition_tooltip_view import WtAmmunitionTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_carousel_tank_model import WtCarouselTankModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_equipment_slot_model import WtEquipmentSlotModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_carousel_view_model import WtCarouselViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_equipment_group_model import WtEquipmentGroupModel

class VignetteHolder(object):
    __slots__ = ('__defaultIntensity',)
    _VIGNETTE_INTENSITY = 0.85

    def __init__(self):
        vignetteSettings = BigWorld.PyRenderSettings().getVignetteSettings()
        self.__defaultIntensity = vignetteSettings.w
        vignetteSettings.w = self._VIGNETTE_INTENSITY
        BigWorld.PyRenderSettings().setVignetteSettings(vignetteSettings)

    def __del__(self):
        vignetteSettings = BigWorld.PyRenderSettings().getVignetteSettings()
        vignetteSettings.w = self.__defaultIntensity
        BigWorld.PyRenderSettings().setVignetteSettings(vignetteSettings)


class WTEventCarouselWidget(WTHangarBaseWidgetMeta):

    def _makeInjectView(self):
        return WTEventCarouselView()


class WTEventCarouselView(ViewImpl, IGlobalListener):
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.CarouselView(), flags=ViewFlags.VIEW, model=WtCarouselViewModel())
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
        if contentID == R.views.white_tiger.lobby.tooltips.TicketTooltipView():
            return WtEventTicketTooltipView()
        if contentID == R.views.white_tiger.lobby.tooltips.StampTooltipView():
            return WtEventStampTooltipView()
        if contentID == R.views.white_tiger.lobby.tooltips.CarouselVehicleTooltipView():
            return WtCarouselVehicleTooltipView(vehInvID=event.getArgument('id'))
        return WtAmmunitionTooltipView(intCD=event.getArgument('id')) if contentID == R.views.white_tiger.lobby.tooltips.AmmunitionTooltipView() else super(WTEventCarouselView, self).createToolTipContent(event, contentID)

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
        self.viewModel.status.onOpenTasks += self.__onOpenTasksClick
        g_eventBus.addListener(events.HangarSimpleEvent.UPDATE_CAROUSEL_VEHICLE_STATES, self.__updateStates, EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        self.stopGlobalListening()
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__prebattleVehicle.onChanged -= self.__onVehicleChanged
        self.viewModel.onClick -= self.__onCarouselClick
        self.viewModel.status.onBuyTicket -= self.__onBuyTicketClick
        self.viewModel.status.onOpenTasks -= self.__onOpenTasksClick
        g_eventBus.removeListener(events.HangarSimpleEvent.UPDATE_CAROUSEL_VEHICLE_STATES, self.__updateStates, EVENT_BUS_SCOPE.LOBBY)

    def __onCarouselClick(self, args):
        vehicle = self.__itemsCache.items.getItemByCD(int(args.get('id')))
        self.__prebattleVehicle.select(vehicle)

    def __onBuyTicketClick(self):
        showBuyLootboxOverlay()

    def __onOpenTasksClick(self):
        showEventProgressionWindow()

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
            _fillVehicles(trx.getTanks(), vehicle)
            _fillEquipment(trx.getEquipmentGroups(), vehicle)


@dependency.replace_none_kwargs(gameEventCtrl=IWhiteTigerController)
def _updateDisableState(model, vehicle, gameEventCtrl=None):
    pInfo = gameEventCtrl.prbDispatcher.getPlayerInfo()
    isReadyToPlatoonBattle = vehicle.isInUnit and pInfo.isReady
    model.setIsDisableAll(isReadyToPlatoonBattle)


def _fillStatus(model, item):
    vehicleData = g_wt_config.getVehicleData(item.intCD)
    ticketCount = g_wt_config.getTokensForBattle(item.intCD)
    model.setTitle(item.userName)
    model.setIcon(R.images.white_tiger.gui.maps.icons.hangar.dyn(vehicleData.type)())
    model.setQuantity(ticketCount)
    model.setWtVehicleType(vehicleData.type)


@dependency.replace_none_kwargs(gameEventCtrl=IWhiteTigerController)
def _fillVehicles(array, item, gameEventCtrl=None):
    array.clear()
    state = gameEventCtrl.prbDispatcher.getFunctionalState()
    pinfo = gameEventCtrl.prbDispatcher.getPlayerInfo()
    isReadyToPlatoonBattle = item.isInUnit and pinfo.isReady
    for vehicleData in g_wt_config.getAllVehiclesData().itervalues():
        if not vehicleData.canShowInHangar:
            continue
        vehicle = vehicleData.vehicle
        iconName = getIconResourceName(vehicle.name)
        if vehicleData.isBoss and g_wt_config.hasTokensForBattle(vehicle.intCD):
            iconName += '_alt'
        model = WtCarouselTankModel()
        model.setId(vehicle.intCD)
        model.setIcon(iconName)
        model.setTitle(vehicle.userName)
        model.setInBattle(vehicle.isInBattle)
        model.setSelected(vehicle == item)
        model.setInPlatoon(vehicle == item and isReadyToPlatoonBattle)
        if vehicleData.isBoss or vehicleData.isSpecialBoss:
            model.setQuantity(g_wt_config.getTokensForBattle(vehicle.intCD))
            model.setUnsuitable(state.isInUnit())
        model.setWtVehicleType(vehicleData.type)
        array.addViewModel(model)

    array.invalidate()


def _fillEquipment(array, item):
    array.clear()
    vehData = g_wt_config.getVehicleData(item.intCD)
    shells = []
    for eq in item.shells.layout:
        if not eq:
            continue
        shells.append(eq)

    shellGroupModel = WtEquipmentGroupModel()
    for shell in shells:
        model = WtEquipmentSlotModel()
        model.setId(shell.intCD)
        model.setIcon(R.images.gui.maps.icons.artefact.dyn(shell.descriptor.iconName)())
        model.setInfiniteIcon(R.images.white_tiger.gui.maps.icons.hangar.infinity.dyn(vehData.type)())
        shellGroupModel.getSlots().addViewModel(model)

    abilities = [ getItemByCompactDescr(eqCD) for eqCD in vehData.equipments ]
    abilityGroupModel = WtEquipmentGroupModel()
    equipmentyGroupModel = None
    for ability in abilities:
        model = WtEquipmentSlotModel()
        model.setId(ability.compactDescr)
        model.setIcon(R.images.gui.maps.icons.artefact.dyn(ability.iconName)())
        if 'eventItem' not in ability.tags:
            model.setTooltipId(TOOLTIPS_CONSTANTS.HANGAR_MODULE)
            if equipmentyGroupModel is None:
                equipmentyGroupModel = WtEquipmentGroupModel()
            equipmentyGroupModel.getSlots().addViewModel(model)
        abilityGroupModel.getSlots().addViewModel(model)

    array.addViewModel(abilityGroupModel)
    if equipmentyGroupModel is not None:
        array.addViewModel(equipmentyGroupModel)
    array.addViewModel(shellGroupModel)
    array.invalidate()
    return
