# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/crew_info_view.py
import logging
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.shared.gui_items.Tankman import Tankman
from helpers import dependency
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.gui.doc_loaders.gui_settings_loader import getVehicleCharacteristics
from white_tiger.gui.impl.lobby.tooltips.tankman_info_adapters import WTTankmanInfoAdapter
from white_tiger.gui.impl.lobby.tooltips.tankman_tooltip_view import WTTankmanTooltipView
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.crew_info_view_model import CrewInfoViewModel
from CurrentVehicle import g_currentVehicle
_logger = logging.getLogger(__name__)

class CrewInfoView(ViewComponent[CrewInfoViewModel]):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.Crewman(), **kwargs):
        super(CrewInfoView, self).__init__(layoutID=layoutID, model=CrewInfoViewModel)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.white_tiger.mono.lobby.tooltips.crew_info_tooltip():
            vehicle = g_currentVehicle.item
            if vehicle is None:
                return
            tankmanInfo = WTTankmanInfoAdapter(self.__getCommander(vehicle))
            return WTTankmanTooltipView(tankmanInfo=tankmanInfo)
        else:
            return super(CrewInfoView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(CrewInfoView, self).getViewModel()

    @sf_lobby
    def __app(self):
        return None

    def _onLoading(self, *args, **kwargs):
        super(CrewInfoView, self)._onLoading(*args, **kwargs)
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
            commander = self.__getCommander(vehicle)
            if commander is None:
                _logger.error('There is no commander in the event vehicle %s', vehicle.name)
                return
            with self.viewModel.transaction() as model:
                model.setName(commander.fullUserName)
                model.setTankmanID(info.role)
            return

    def __getCommander(self, vehicle):
        return next((tman for _, tman in vehicle.crew if tman.role == Tankman.ROLES.COMMANDER), None)
