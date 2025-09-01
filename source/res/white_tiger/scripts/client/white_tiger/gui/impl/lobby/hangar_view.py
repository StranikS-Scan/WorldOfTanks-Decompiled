# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/hangar_view.py
import typing
from frameworks.wulf import WindowLayer
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.prb_control import prbEntityProperty
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.lobby_state_machine.router import SubstateRouter
from helpers import dependency
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.gui.impl.gen.view_models.views.lobby.hangar_view_model import HangarViewModel
from gui.shared.utils import SelectorBattleTypesUtils
from white_tiger.gui.white_tiger_gui_constants import PREBATTLE_ACTION_NAME, WT_HANGAR_SELECTED_VEHICLE
from gui.impl.lobby.hangar.presenters.utils import getSharedMenuItems
from white_tiger.gui.impl.lobby.widgets.main_menu_view import MainMenuView
from white_tiger.gui.impl.lobby.widgets.carousel_view import CarouselView
from white_tiger.gui.impl.lobby.widgets.consumables_panel_view import ConsumablesPanelView
from white_tiger.gui.impl.lobby.widgets.progression_entry_point_view import ProgressionEntryPointView
from white_tiger.gui.impl.lobby.widgets.crew_info_view import CrewInfoView
from white_tiger.gui.impl.lobby.widgets.tank_info_view import TankInfoView
from white_tiger.gui.impl.lobby.widgets.lootbox_entry_point_view import LootboxEntryView
from helpers.CallbackDelayer import CallbackDelayer
from CurrentVehicle import g_currentVehicle
from gui.impl.pub import WindowImpl
from frameworks.wulf import WindowFlags
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from white_tiger.gui.impl.lobby.widgets.progression_content_view import ProgressionContentView
from white_tiger.gui.impl.lobby.widgets.quests_view import QuestsView
from white_tiger.gui.shared.event_dispatcher import showInfoPage
from white_tiger.gui.sounds.sound_constants import WT_HANGAR_VIEW_SOUND_SPACE
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

class HangarView(ViewComponent[HangarViewModel], IRoutableView):
    LAYOUT_ID = R.views.white_tiger.mono.lobby.main()
    __slots__ = ('__childViews',)
    __wtCtrl = dependency.descriptor(IWhiteTigerController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = WT_HANGAR_VIEW_SOUND_SPACE

    def __init__(self):
        super(HangarView, self).__init__(R.views.white_tiger.mono.lobby.main(), HangarViewModel)
        self.__childViews = []
        self.__router = None
        return

    def getRouterModel(self):
        return self.getViewModel().router

    def _initChildren(self):
        hangar = R.aliases.hangar.shared
        whiteTiger = R.aliases.white_tiger.shared
        self._registerChild(hangar.MainMenu(), MainMenuView(getSharedMenuItems()))
        self._registerChild(whiteTiger.Carousel(), CarouselView())
        self._registerChild(whiteTiger.Progression(), ProgressionEntryPointView())
        self._registerChild(whiteTiger.Crewman(), CrewInfoView())
        self._registerChild(whiteTiger.VehicleStats(), TankInfoView())
        self._registerChild(whiteTiger.ConsumablesPanel(), ConsumablesPanelView())
        self._registerChild(whiteTiger.ProgressionContent(), ProgressionContentView())
        self._registerChild(whiteTiger.ProgressionQuests(), QuestsView())
        self._registerChild(whiteTiger.LootboxEntryPoint(), LootboxEntryView())

    def _getEvents(self):
        model = self.getViewModel()
        return [(model.onEscPressed, self.__onEscape),
         (model.onViewLoaded, self.__onViewLoaded),
         (model.onInfoClicked, self.__onInfoClicked),
         (g_currentVehicle.onChanged, self.__onCurrentVehicleChanged)]

    @property
    def viewModel(self):
        return super(HangarView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    @sf_lobby
    def __app(self):
        return None

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(HangarView, self).createToolTip(event)

    def getTooltipData(self, event):
        for childView in self.__childViews:
            tooltipData = childView.getTooltipData(event)
            if tooltipData:
                return tooltipData

        return None

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def _onLoading(self, *args, **kwargs):
        super(HangarView, self)._onLoading()
        self.__timer = CallbackDelayer()

    def _onLoaded(self, *args, **kwargs):
        super(HangarView, self)._onLoaded(*args, **kwargs)
        if not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.WHITE_TIGER):
            SelectorBattleTypesUtils.setBattleTypeAsKnown(PREBATTLE_ACTION_NAME.WHITE_TIGER)
        self.__highlightSelectedVehicle()
        contentChildPos = self._childrenUidByPosition[R.aliases.white_tiger.shared.ProgressionContent()]
        questChildPos = self._childrenUidByPosition[R.aliases.white_tiger.shared.ProgressionQuests()]
        self.__childViews.append(self._childrenByUid[contentChildPos])
        self.__childViews.append(self._childrenByUid[questChildPos])
        lsm = getLobbyStateMachine()
        self.__router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self.__router.init()

    def __onCurrentVehicleChanged(self):
        self.__highlightSelectedVehicle()

    def _finalize(self):
        self.__baseCriteria = None
        self.__childViews[:] = []
        if self.__router:
            self.__router.fini()
            self.__router = None
        super(HangarView, self)._finalize()
        return

    def __onInfoClicked(self):
        showInfoPage()

    def __onEscape(self):
        dialogsContainer = self.__app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __highlightSelectedVehicle(self):
        if not self.__wtCtrl.isEventPrbActive() or not self.__wtCtrl.isSelectedVehicleWTVehicle():
            return
        vehicle = g_currentVehicle.item
        if vehicle.name in WT_HANGAR_SELECTED_VEHICLE:
            with self.viewModel.transaction() as vm:
                vm.setSelectedVehicle(WT_HANGAR_SELECTED_VEHICLE[vehicle.name])


class HangarWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = 1.0
        super(HangarWindow, self).__init__(content=HangarView(), wndFlags=WindowFlags.WINDOW, layer=layer)
