# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_characteristics_panel_view.py
import typing
from gui.doc_loaders.event_settings_loader import getVehicleCharacteristics
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_characteristics_panel_view_model import WtCharacteristicsPanelViewModel, WtCharacteristicModel
from white_tiger.gui.impl.lobby.tooltips.wt_vehicle_params_tooltip_view import WtVehicleParamsTooltipView
from white_tiger.gui.impl.lobby.wt_event_inject_widget_view import WTEventInjectWidget
from white_tiger.gui.impl.lobby.wt_event_constants import VehicleCharacteristics
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.meta.WTEventParamsWidgetMeta import WTEventParamsWidgetMeta
from frameworks.wulf import ViewFlags, ViewSettings
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IWhiteTigerController
if typing.TYPE_CHECKING:
    from gui.impl.wrappers.user_list_model import UserListModel
_STR_PATH = R.strings.event.characteristicsPanel
_IMG_PATH = R.images.white_tiger.gui.maps.icons.characteristicPanel

class WTEventCharacteristicsPanelWidget(WTEventParamsWidgetMeta, WTEventInjectWidget):

    def _makeInjectView(self):
        return WTEventCharacteristicsPanelView()


class WTEventCharacteristicsPanelView(ViewImpl):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __wtController = dependency.descriptor(IWhiteTigerController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.CharacteristicsPanel(), flags=ViewFlags.VIEW, model=WtCharacteristicsPanelViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventCharacteristicsPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        parameter = event.getArgument('parameter')
        return WtVehicleParamsTooltipView(parameter=parameter) if parameter is not None else super(WTEventCharacteristicsPanelView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WTEventCharacteristicsPanelView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        super(WTEventCharacteristicsPanelView, self)._finalize()

    def __addListeners(self):
        self.__prebattleVehicle.onChanged += self.__updateViewModel
        self.viewModel.onLeaveClicked += self.__onLeaveClicked

    def __removeListeners(self):
        self.__prebattleVehicle.onChanged -= self.__updateViewModel
        self.viewModel.onLeaveClicked -= self.__onLeaveClicked

    def __updateViewModel(self):
        vehicle = self.__prebattleVehicle.item
        if vehicle is None:
            return
        else:
            info = getVehicleCharacteristics().get(vehicle.name)
            if info is None:
                return
            with self.viewModel.transaction() as model:
                model.setSpecialInfo(_STR_PATH.specialInfo.dyn(info.role)())
                self.__fillList(model.pros, VehicleCharacteristics.PROS.value, info.pros)
                self.__fillList(model.cons, VehicleCharacteristics.CONS.value, info.cons)
            return

    @staticmethod
    def __fillList(model, aspect, properties):
        model.clearItems()
        for prop in properties:
            item = WtCharacteristicModel()
            item.setParameter(prop)
            item.setIcon(_IMG_PATH.dyn(aspect).dyn(prop)())
            model.addViewModel(item)

        model.invalidate()

    def __onLeaveClicked(self):
        if self.__wtController.isAvailable() and self.__wtController.isEventPrbActive():
            self.__wtController.doLeaveEventPrb()
