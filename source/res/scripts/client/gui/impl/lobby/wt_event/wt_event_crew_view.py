# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_crew_view.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.WTEventCrewWidgetMeta import WTEventCrewWidgetMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.crew_member_model import CrewMemberModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_crew_model import WtEventCrewModel
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.impl.pub import ViewImpl, WindowImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from gui.shared.gui_items.Tankman import Tankman
from gui.wt_event.wt_event_helpers import getHunterFullUserName
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class WTEventCrewWidget(WTEventCrewWidgetMeta, WTEventInjectWidget):
    __slots__ = ()

    def _makeInjectView(self):
        return WTEventCrewView()


class WTEventCrewView(ViewImpl, IGlobalListener):
    __slots__ = ()
    gameEventController = dependency.instance(IGameEventController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCrew(), flags=ViewFlags.COMPONENT, model=WtEventCrewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventCrewView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTEventCrewView, self).getViewModel()

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

    def onPrbEntitySwitched(self):
        self.__fillCrew()

    def _onLoading(self, *args, **kwargs):
        super(WTEventCrewView, self)._onLoading()
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        self.__fillCrew()

    def _finalize(self):
        super(WTEventCrewView, self)._finalize()
        self.__removeListeners()

    def __addListeners(self):
        g_currentVehicle.onChanged += self.__fillCrew
        self.startGlobalListening()

    def __removeListeners(self):
        g_currentVehicle.onChanged -= self.__fillCrew
        self.stopGlobalListening()

    def __fillCrew(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            if not vehicle.isEvent:
                return
            isBoss = vehicle.eventType in (VEHICLE_EVENT_TYPE.EVENT_BOSS, VEHICLE_EVENT_TYPE.EVENT_SPECIAL_BOSS)
            description = backport.text(R.strings.wt_event.crewPanel.boss.description()) if isBoss else ''
            self.viewModel.crew.clearItems()
            for _, tman in vehicle.crew:
                if tman is None:
                    continue
                if isBoss and tman.role != Tankman.ROLES.COMMANDER:
                    continue
                model = CrewMemberModel()
                model.setTankmanID(tman.invID)
                userName = tman.fullUserName if isBoss else getHunterFullUserName(tman.role)
                model.setName(userName)
                model.setDescription(description)
                model.setType(tman.roleUserName)
                model.setPerk(bool(tman.skills))
                model.setRankIcon(tman.iconRank)
                self.viewModel.crew.addViewModel(model)

            self.viewModel.crew.invalidate()
        return

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if not tooltipId:
            return None
        else:
            if tooltipId == TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED:
                args = ['tman_template:germany::wt_raidboss_commander::::commander_sixthSense::wt_raidboss_commander:']
            elif tooltipId == TOOLTIPS_CONSTANTS.TANKMAN:
                args = [int(event.getArgument('tankmanID'))]
            elif tooltipId == TOOLTIPS_CONSTANTS.TANKMAN_SKILL:
                args = ['commander_sixthSense', int(event.getArgument('tankmanID'))]
            else:
                args = []
            return TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=args)


class WTEventCrewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WTEventCrewWindow, self).__init__(WindowFlags.WINDOW, content=WTEventCrewView(), parent=parent)
