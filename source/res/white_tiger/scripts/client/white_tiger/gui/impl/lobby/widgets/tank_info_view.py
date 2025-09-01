# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/tank_info_view.py
import logging
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.tank_info_view_model import TankInfoViewModel, PropertyModel
from white_tiger.gui.impl.lobby.tooltips.tank_info_tooltip_view import TankInfoTooltipView
from white_tiger.gui.doc_loaders.gui_settings_loader import getVehicleCharacteristics
from white_tiger.gui.white_tiger_gui_constants import VehicleCharacteristics
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from CurrentVehicle import g_currentVehicle
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.white_tiger_lobby.characteristicsPanel.specialInfo
_IMG_PATH = R.images.white_tiger.gui.maps.icons.characteristicPanel

class TankInfoView(ViewComponent[TankInfoViewModel]):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.VehicleStats(), **kwargs):
        super(TankInfoView, self).__init__(layoutID=layoutID, model=TankInfoViewModel)

    def createToolTipContent(self, event, contentID):
        parameter = event.getArgument('parameter')
        return TankInfoTooltipView(parameter=parameter) if parameter is not None else super(TankInfoView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(TankInfoView, self).getViewModel()

    @sf_lobby
    def __app(self):
        return None

    def _onLoading(self, *args, **kwargs):
        super(TankInfoView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__fillModel),)

    def __fillModel(self):
        if not self.__wtCtrl.isSelectedVehicleWTVehicle():
            return
        else:
            vehicle = g_currentVehicle.item
            info = getVehicleCharacteristics().get(vehicle.name)
            if info is None:
                _logger.error('There is no special characteristics of the event vehicle  %s to get commander role', vehicle.name)
                return
            with self.viewModel.transaction() as model:
                model.setSpecialInfo(_STR_PATH.dyn(info.role)())
                self.__fillList(model.getPros(), VehicleCharacteristics.PROS.value, info.pros)
                self.__fillList(model.getCons(), VehicleCharacteristics.CONS.value, info.cons)
            return

    @staticmethod
    def __fillList(model, aspect, properties):
        model.clear()
        for prop in properties:
            item = PropertyModel()
            item.setParameter(prop)
            item.setIcon(_IMG_PATH.dyn(aspect).dyn(prop)())
            model.addViewModel(item)

        model.invalidate()
