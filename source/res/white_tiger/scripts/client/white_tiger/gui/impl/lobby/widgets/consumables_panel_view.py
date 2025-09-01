# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/consumables_panel_view.py
from shared_utils import first
from helpers import dependency
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.hangar_consumables_panel_view_model import HangarConsumablesPanelViewModel, TankTypeEnum
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.equipment_group_model import EquipmentGroupModel
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.equipment_slot_model import EquipmentSlotModel
from white_tiger.gui.impl.lobby.tooltips.ammunition_tooltip_view import AmmunitionTooltipView
from white_tiger.gui.impl.lobby.tooltips.ticket_tooltip_view import TicketTooltipView
from white_tiger.gui.shared.event_dispatcher import showProgressionScreen, showBuyLootboxOverlay
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController

class ConsumablesPanelView(ViewComponent[HangarConsumablesPanelViewModel]):
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.ConsumablesPanel(), **kwargs):
        super(ConsumablesPanelView, self).__init__(layoutID=layoutID, model=HangarConsumablesPanelViewModel)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = createTooltipData(isSpecial=True, specialAlias=event.getArgument('tooltipId'), specialArgs=(event.getArgument('id'), 1))
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        return super(ConsumablesPanelView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.white_tiger.mono.lobby.tooltips.ammunition_panel_tooltip():
            return AmmunitionTooltipView(intCD=event.getArgument('id'))
        return TicketTooltipView() if contentID == R.views.white_tiger.mono.lobby.tooltips.ticket_tooltip() else super(ConsumablesPanelView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(ConsumablesPanelView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ConsumablesPanelView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__update), (self.viewModel.onBuyTicket, self.__onBuyTicketClick), (self.viewModel.onOpenTasks, self.__onOpenTasksClick))

    def _getCallbacks(self):
        return (('tokens', self.__onTokensUpdate),)

    def __onBuyTicketClick(self):
        showBuyLootboxOverlay()

    def __onOpenTasksClick(self):
        showProgressionScreen()

    def __update(self):
        if not self.__wtCtrl.isEventPrbActive() or not self.__wtCtrl.isSelectedVehicleWTVehicle():
            return
        vehicle = g_currentVehicle.item
        with self.viewModel.transaction() as vm:
            self.__fillEquipment(vm.equipments, vehicle)
            self.__fillStatus(vm, vehicle, self.__economicsCtrl)

    def __onTokensUpdate(self, diff):
        if self.__wtCtrl.isEventPrbActive() and ('wtevent:' in key for key in diff.keys()):
            self.__update()

    def __fillStatus(self, model, item, gameEventCtrl=None):
        if not item:
            return
        eventType = first(item.tags & WT_VEHICLE_TAGS.EVENT_VEHS)
        model.setTankType(TankTypeEnum(eventType) if WT_VEHICLE_TAGS.PRIORITY_BOSS not in item.tags else TankTypeEnum.SPECIALBOSS)
        model.setTitle(item.userName)
        model.setIcon(R.images.white_tiger.gui.maps.icons.hangar.dyn(eventType)())
        model.setQuantity(self.__economicsCtrl.getTicketCount() or 0)

    def __fillEquipment(self, array, item):
        array.clearItems()
        shells = [ eq for eq in item.shells.layout if eq ]
        abilities = []
        regulars = []
        ultimates = []
        for eq in item.consumables.layout:
            if not eq or 'hidden' in eq.tags:
                continue
            if 'repairkit' in eq.tags or 'medkit' in eq.tags:
                regulars.append(eq)
            if 'Hyperion' in eq.name:
                ultimates.append(eq)
            if 'builtin' or 'trigger' in eq.tags:
                abilities.append(eq)

        for layout in (shells,
         abilities,
         regulars,
         ultimates):
            if not layout:
                continue
            groupmodel = EquipmentGroupModel()
            for eq in layout:
                if not eq:
                    continue
                model = EquipmentSlotModel()
                model.setId(eq.intCD)
                model.setIcon(R.images.gui.maps.icons.artefact.dyn(eq.descriptor.iconName)())
                if eq.itemTypeID == GUI_ITEM_TYPE.SHELL:
                    model.setIsInfinite(True)
                if eq.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT and eq in regulars:
                    model.setTooltipId(TOOLTIPS_CONSTANTS.HANGAR_MODULE)
                groupmodel.group.addViewModel(model)

            array.addViewModel(groupmodel)

        array.invalidate()
