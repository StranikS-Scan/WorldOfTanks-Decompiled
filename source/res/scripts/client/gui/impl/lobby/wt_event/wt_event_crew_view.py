# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_crew_view.py
import logging
from Event import Event
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.WTEventCrewWidgetMeta import WTEventCrewWidgetMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.doc_loaders.event_settings_loader import getVehicleCharacteristics
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_crew_model import WtEventCrewModel
from gui.impl.lobby.tooltips.tankman_tooltip_adapters import WTTankmanInfoAdapter
from gui.impl.lobby.tooltips.tankman_tooltip_view import TankmanTooltipView
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.Vehicle import getCommander
from helpers import dependency
from helpers.dependency import descriptor
from skeletons.gui.app_loader import IAppLoader
from skeletons.prebattle_vehicle import IPrebattleVehicle
_logger = logging.getLogger(__name__)
_SIXTH_SENSE = 'commander_sixthSense'

def _hasSixthSense(commander):
    return _SIXTH_SENSE in commander.skillsMap


class WTEventCrewWidget(WTEventCrewWidgetMeta, WTEventInjectWidget):

    def _makeInjectView(self):
        return WTEventCrewView()

    def getOnEscKeyDown(self):
        return self.getInjectView().onEscKeyDown


class WTEventCrewView(ViewImpl, IGlobalListener):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __appLoader = descriptor(IAppLoader)
    __slots__ = ('onEscKeyDown',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCrew(), flags=ViewFlags.COMPONENT, model=WtEventCrewModel())
        settings.args = args
        settings.kwargs = kwargs
        self.onEscKeyDown = Event()
        super(WTEventCrewView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            args = [_SIXTH_SENSE, int(event.getArgument('invID'))]
            if tooltipId == WtEventCrewModel.SKILL_TOOLTIP:
                tooltipMgr = self.__appLoader.getApp().getToolTipMgr()
                tooltipMgr.onCreateWulfTooltip(tooltipId, args, event.mouse.positionX, event.mouse.positionY)
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
        return super(WTEventCrewView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.TankmanTooltipView():
            vehicle = self.__prebattleVehicle.item
            if vehicle is None:
                return
            tankmanInfo = WTTankmanInfoAdapter(getCommander(vehicle))
            return TankmanTooltipView(tankmanInfo)
        else:
            return super(WTEventCrewView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WTEventCrewView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        super(WTEventCrewView, self)._finalize()

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
            commander = getCommander(vehicle)
            if commander is None:
                _logger.error('There is not commander in the event vehicle')
                return
            info = getVehicleCharacteristics().get(vehicle.name)
            if info is None:
                _logger.error('There is not special characteristics of the event vehicle to get commander role')
                return
            with self.viewModel.transaction() as model:
                model.setName(commander.fullUserName)
                model.setTankmanID(info.role)
                model.setInvID(commander.invID)
                model.setHasSixthSense(_hasSixthSense(commander))
            return

    def __onEscKeyDown(self):
        self.onEscKeyDown()
