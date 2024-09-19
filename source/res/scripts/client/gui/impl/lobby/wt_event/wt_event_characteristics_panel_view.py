# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_characteristics_panel_view.py
import typing
from Event import Event
from gui.doc_loaders.event_settings_loader import getVehicleCharacteristics
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_characteristics_panel_view_model import WtEventCharacteristicsPanelViewModel, PropertyModel
from gui.impl.lobby.wt_event.tooltips.wt_event_vehicle_params_tooltip_view import WtEventVehicleParamsTooltipView
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.impl.lobby.wt_event.wt_event_constants import VehicleCharacteristics
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.meta.WTEventParamsWidgetMeta import WTEventParamsWidgetMeta
from frameworks.wulf import ViewFlags, ViewSettings
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
if typing.TYPE_CHECKING:
    from gui.impl.wrappers.user_list_model import UserListModel
_STR_PATH = R.strings.event.characteristicsPanel
_IMG_PATH = R.images.gui.maps.icons.wtevent.characteristicPanel

class WTEventCharacteristicsPanelWidget(WTEventParamsWidgetMeta, WTEventInjectWidget):

    def _makeInjectView(self):
        return WTEventCharacteristicsPanelView()

    def getOnEscKeyDown(self):
        return self.getInjectView().onEscKeyDown


class WTEventCharacteristicsPanelView(ViewImpl):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __slots__ = ('onEscKeyDown',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCharacteristicsPanel(), flags=ViewFlags.VIEW, model=WtEventCharacteristicsPanelViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self.onEscKeyDown = Event()
        super(WTEventCharacteristicsPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        parameter = event.getArgument('parameter')
        return WtEventVehicleParamsTooltipView(parameter=parameter) if parameter is not None else super(WTEventCharacteristicsPanelView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WTEventCharacteristicsPanelView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        super(WTEventCharacteristicsPanelView, self)._finalize()

    def __addListeners(self):
        self.__prebattleVehicle.onChanged += self.__updateViewModel
        self.viewModel.onEscKeyDown += self.__onEscKeyDown

    def __removeListeners(self):
        self.__prebattleVehicle.onChanged -= self.__updateViewModel
        self.viewModel.onEscKeyDown -= self.__onEscKeyDown

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
            item = PropertyModel()
            item.setParameter(prop)
            item.setIcon(_IMG_PATH.dyn(aspect).dyn(prop)())
            model.addViewModel(item)

        model.invalidate()

    def __onEscKeyDown(self):
        self.onEscKeyDown()
