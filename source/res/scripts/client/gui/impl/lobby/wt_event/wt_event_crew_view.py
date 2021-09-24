# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_crew_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.doc_loaders.event_settings_loader import getVehicleCharacteristics
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_crew_model import WtEventCrewModel
from gui.impl.lobby.tooltips.tankman_tooltip_adapters import WTTankmanInfoAdapter
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.daapi.view.meta.WTEventCrewWidgetMeta import WTEventCrewWidgetMeta
from gui.shared.gui_items.Vehicle import getCommander
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from gui.impl.lobby.tooltips.tankman_tooltip_view import TankmanTooltipView
_logger = logging.getLogger(__name__)
_SIXTH_SENSE = 'commander_sixthSense'

def _hasSixthSense(commander):
    return _SIXTH_SENSE in commander.skillsMap


class WTEventCrewWidget(WTEventCrewWidgetMeta, WTEventInjectWidget):

    def _makeInjectView(self):
        return WTEventCrewView()


class WTEventCrewView(ViewImpl, IGlobalListener):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCrew(), flags=ViewFlags.COMPONENT, model=WtEventCrewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventCrewView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            if tooltipData is None:
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is None:
                return
            window.load()
            return window
        else:
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

    def __removeListeners(self):
        self.__prebattleVehicle.onChanged -= self.__updateViewModel

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

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if not tooltipId:
            return None
        else:
            return TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=[_SIXTH_SENSE, int(event.getArgument('invID'))]) if tooltipId == WtEventCrewModel.SKILL_TOOLTIP else None
