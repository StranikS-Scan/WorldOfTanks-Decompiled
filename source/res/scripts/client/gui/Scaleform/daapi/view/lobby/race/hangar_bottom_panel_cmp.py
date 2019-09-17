# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/hangar_bottom_panel_cmp.py
import logging
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.race.equipment_panel_cmp_tooltips import EquipmentPanelCmpTooltips
from gui.impl.gen.view_models.views.race.hangar_bottom_panel_view_model import HangarBottomPanelViewModel
from gui.impl.gen.view_models.views.race.race_equipment_model import RaceEquipmentModel
from gui.impl.gen.view_models.views.race.race_equipment_tooltip_model import RaceEquipmentTooltipModel
from gui.impl.pub import ViewImpl
_logger = logging.getLogger(__name__)

class RaceEquipmentCD(object):
    ENGINE = 0
    REAR = 1
    NITRO = 2
    AMMO = 2570
    INTEL = 3


_RACE_EQUIPMENT = {RaceEquipmentCD.ENGINE: 'engine',
 RaceEquipmentCD.REAR: 'rear',
 RaceEquipmentCD.NITRO: 'nitro',
 RaceEquipmentCD.INTEL: 'intel'}
_RACE_EQUIPMENT_COMMON = (_RACE_EQUIPMENT[RaceEquipmentCD.INTEL],)

class RaceVehicleName(object):
    T_50 = 'ussr:R00_T-50_race'
    CHAFFEE = 'usa:A00_M24_Chaffee_race'
    LEOPARD = 'germany:G00_VK1602_race'


_RACE_VEHICLE_SHORT_NAMES = {RaceVehicleName.T_50: 't_50',
 RaceVehicleName.CHAFFEE: 'chaffee',
 RaceVehicleName.LEOPARD: 'leopard'}

class HangarBottomPanelComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return HangarBottomPanelView()


class HangarBottomPanelView(ViewImpl):

    def __init__(self, *args, **kwargs):
        super(HangarBottomPanelView, self).__init__(R.views.lobby.race.hangar_bottom_panel_cmp.HangarBottomPanelCmp(), ViewFlags.COMPONENT, HangarBottomPanelViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(HangarBottomPanelView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return RaceEquipmentItemTooltip(event.getArgument('intCD')) if event.contentID == R.views.lobby.race.hangar_bottom_panel_cmp.RaceEquipmentItemTooltip() else super(HangarBottomPanelView, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(HangarBottomPanelView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(HangarBottomPanelView, self)._initialize(*args, **kwargs)
        self.__addListeners()
        self.__updateModel()

    def _finalize(self):
        self.__removeListeners()
        super(HangarBottomPanelView, self)._finalize()

    def __addListeners(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged

    def __removeListeners(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return
        else:
            items = self.viewModel.equipment.getItems()
            if items is None:
                return
            items.clear()
            self.__addEquipmentItem(items, RaceEquipmentCD.ENGINE)
            self.__addEquipmentItem(items, RaceEquipmentCD.REAR)
            self.__addEquipmentItem(items, RaceEquipmentCD.NITRO)
            itemModel = RaceEquipmentModel()
            itemModel.setIconSource(R.images.gui.maps.icons.ammopanel.ammo.HIGH_EXPLOSIVE_PREMIUM())
            if vehicle.shells:
                itemModel.setIntCD(vehicle.shells[0].intCD)
            else:
                itemModel.setIntCD(0)
            itemModel.setTooltipType(EquipmentPanelCmpTooltips.TOOLTIP_SHELL)
            itemModel.setTooltipResId(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())
            items.addViewModel(itemModel)
            self.__addEquipmentItem(items, RaceEquipmentCD.INTEL)
            self.viewModel.setHasShortPanel(True)
            items.invalidate()
            return

    def __addEquipmentItem(self, items, itemId):
        itemName = _RACE_EQUIPMENT[itemId]
        if itemName is None:
            _logger.warning('There is no equipment item with id %d', itemId)
            return
        else:
            vehicleName = _RACE_VEHICLE_SHORT_NAMES.get(g_currentVehicle.item.name)
            itemModel = RaceEquipmentModel()
            if vehicleName:
                itemOnTankName = '{}_{}'.format(vehicleName, itemName)
                itemModel.setIconSource(R.images.gui.maps.icons.race.hangar.bottom_panel.dyn(itemOnTankName)())
            itemModel.setTooltipResId(R.views.lobby.race.hangar_bottom_panel_cmp.RaceEquipmentItemTooltip())
            itemModel.setIntCD(itemId)
            items.addViewModel(itemModel)
            return

    def __getTooltipData(self, event):
        tooltipType = event.getArgument('tooltipType')
        intCD = event.getArgument('intCD')
        return None if not tooltipType or not intCD else createTooltipData(isSpecial=True, specialAlias=tooltipType, specialArgs=(intCD, 1))


class RaceEquipmentItemTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, itemId):
        super(RaceEquipmentItemTooltip, self).__init__(R.views.lobby.race.hangar_bottom_panel_cmp.RaceEquipmentItemTooltip(), ViewFlags.COMPONENT, RaceEquipmentTooltipModel, itemId)

    def _initialize(self, itemId):
        super(RaceEquipmentItemTooltip, self)._initialize()
        itemName = _RACE_EQUIPMENT.get(itemId)
        vehicleName = _RACE_VEHICLE_SHORT_NAMES.get(g_currentVehicle.item.name)
        itemOnTankName = '{}_{}'.format(vehicleName, itemName)
        if itemName is None:
            _logger.warning('There is no equipment item with id %d', itemId)
            return
        else:
            if g_currentVehicle.isPresent:
                vehicleCD = g_currentVehicle.item.intCD
            else:
                _logger.warning('Current vehicle is not present')
                return
            if vehicleName is None:
                _logger.warning('There is no race vehicle with id %d', vehicleCD)
                return
            if itemName in _RACE_EQUIPMENT_COMMON:
                tooltip = R.strings.festival.race.hangar.equipment.tooltip.dyn(itemName)
            else:
                tooltip = R.strings.festival.race.hangar.equipment.dyn(vehicleName).tooltip.dyn(itemName)
            with self.getViewModel().transaction() as model:
                model.setTitle(tooltip.title())
                model.setDescription(tooltip.description())
                model.setIconSource(R.images.gui.maps.icons.race.hangar.bottom_panel.c_100_100.dyn(itemOnTankName)())
            return

    @property
    def viewModel(self):
        return super(RaceEquipmentItemTooltip, self).getViewModel()
