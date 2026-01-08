# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/hangar/states.py
import logging
import typing
from WeakMethod import WeakMethodProxy
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from comp7.gui.impl.lobby.comp7_intro_screen import Comp7IntroScreen
from comp7.gui.impl.lobby.comp7_no_vehicles_screen import Comp7NoVehiclesScreen
from comp7.gui.impl.lobby.hangar.meta_tab_state import IMetaTabState
from comp7.gui.impl.lobby.meta_view.meta_root_view import MetaRootView
from comp7.gui.impl.lobby.tournaments.wci_view import WciView
from comp7.gui.impl.lobby.tournaments.ols_view import OlsView
from comp7.gui.shared.event_dispatcher import showComp7InfoPage, showComp7WhatsNewScreen, showWciInfoPage, showOlsInfoPage
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import generateBasicLoadoutStateClasses, _LoadoutConfirmStatePrototype
from gui.impl.lobby.hangar.easy_tank_equip_state import generateEasyTankEquipStates
from gui.impl.lobby.hangar.states import HangarState, EasyTankEquipState
from gui.lobby_state_machine.states import LobbyState, LobbyStateFlags, GuiImplViewLobbyState
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from gui.lobby_state_machine.transitions import HijackTransition
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from comp7.gui.impl.lobby.hangar.comp7_hangar import Comp7Hangar
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(Comp7ModeState())


def registerTransitions(machine):
    comp7Mode = machine.getStateByCls(Comp7ModeState)
    machine.addNavigationTransitionFromParent(comp7Mode)


@SubScopeSubLayerState.parentOf
class Comp7ModeState(LobbyState):
    STATE_ID = 'comp7'
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(Comp7HangarState(StateFlags.INITIAL))
        lsm.addState(Comp7AllVehiclesState())
        lsm.addState(Comp7EasyTankEquipState())
        lsm.addState(Comp7LoadoutState())
        lsm.addState(Comp7NoVehiclesState())
        lsm.addState(Comp7IntroState())
        lsm.addState(Comp7PrimeTimeState())
        lsm.addState(Comp7MetaState())
        lsm.addState(Comp7StylePreviewState())
        lsm.addState(Comp7VehiclePreviewState())
        lsm.addState(Comp7WCIState())
        lsm.addState(Comp7OLSState())

    def registerTransitions(self):
        lsm = self.getMachine()
        parent = self.getParent()
        comp7Hangar = lsm.getStateByCls(Comp7RootHangarState)
        comp7EasyTankEquip = lsm.getStateByCls(Comp7EasyTankEquipState)
        hijackCondition = WeakMethodProxy(self._hijackTransitionCondition)
        parent.addNavigationTransition(comp7Hangar)
        parent.addTransition(HijackTransition(HangarState, hijackCondition), comp7Hangar)
        parent.addTransition(HijackTransition(EasyTankEquipState, hijackCondition), comp7EasyTankEquip)
        for cls in (Comp7AllVehiclesState,
         Comp7NoVehiclesState,
         Comp7IntroState,
         Comp7PrimeTimeState,
         Comp7OLSState,
         Comp7EasyTankEquipState):
            state = lsm.getStateByCls(cls)
            comp7Hangar.addNavigationTransition(state)

        randomHangar = lsm.getStateByCls(HangarState)
        wci = lsm.getStateByCls(Comp7WCIState)
        randomHangar.addNavigationTransition(wci)

    def _hijackTransitionCondition(self, _):
        return self.__comp7Controller.isEnabled() and self.__comp7Controller.isModePrbActive()


@Comp7ModeState.parentOf
class Comp7HangarState(SFViewLobbyState):
    STATE_ID = 'hangar'
    VIEW_KEY = ViewKey(COMP7_HANGAR_ALIASES.COMP7_LOBBY_HANGAR)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(Comp7HangarState, self).__init__(flags | LobbyStateFlags.HANGAR)

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(Comp7RootHangarState(flags=StateFlags.INITIAL))

    def __getView(self):
        app = self.__appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        return view.getParentWindow().content


@Comp7HangarState.parentOf
class Comp7RootHangarState(LobbyState):
    STATE_ID = '{root}'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(Comp7RootHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    def _onEntered(self, event):
        super(Comp7RootHangarState, self)._onEntered(event)
        lsm = self.getMachine()
        lsm.getRelatedView(self).blur.disable()


@Comp7HangarState.parentOf
class Comp7AllVehiclesState(LobbyState):
    STATE_ID = 'allVehicles'

    def _onEntered(self, event):
        super(Comp7AllVehiclesState, self)._onEntered(event)
        lsm = self.getMachine()
        lsm.getRelatedView(self).blur.enable()

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.allVehicles()))


@Comp7ModeState.parentOf
class Comp7NoVehiclesState(GuiImplViewLobbyState):
    STATE_ID = 'noVehicles'
    VIEW_KEY = ViewKey(R.views.comp7.mono.lobby.no_vehicles_screen())

    def __init__(self):
        super(Comp7NoVehiclesState, self).__init__(Comp7NoVehiclesScreen, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.noVehicles()))


@Comp7ModeState.parentOf
class Comp7IntroState(GuiImplViewLobbyState):
    STATE_ID = 'intro'
    VIEW_KEY = ViewKey(R.views.comp7.mono.lobby.intro_screen())

    def __init__(self):
        super(Comp7IntroState, self).__init__(Comp7IntroScreen, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.intro()))


@SubScopeSubLayerState.parentOf
class Comp7WCIState(GuiImplViewLobbyState):
    STATE_ID = 'wci'
    VIEW_KEY = ViewKey(R.views.comp7.mono.lobby.tournaments.wci_view())

    def __init__(self):
        super(Comp7WCIState, self).__init__(WciView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.tournament()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showWciInfoPage, tooltipHeader=backport.text(R.strings.comp7_ext.tournament.tooltip.infoPageButton.header())),))

    def registerTransitions(self):
        lsm = self.getMachine()
        state = lsm.getStateByCls(ShopState)
        self.addNavigationTransition(state, record=True)


@Comp7ModeState.parentOf
class Comp7OLSState(GuiImplViewLobbyState):
    STATE_ID = 'ols'
    VIEW_KEY = ViewKey(R.views.comp7.mono.lobby.tournaments.ols_view())

    def __init__(self):
        super(Comp7OLSState, self).__init__(OlsView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.tournament()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showOlsInfoPage, tooltipHeader=backport.text(R.strings.comp7_ext.tournament.tooltip.infoPageButton.header())),))

    def registerTransitions(self):
        lsm = self.getMachine()
        state = lsm.getStateByCls(ShopState)
        self.addNavigationTransition(state, record=True)


@Comp7ModeState.parentOf
class Comp7PrimeTimeState(SFViewLobbyState):
    STATE_ID = 'primeTime'
    VIEW_KEY = ViewKey(COMP7_HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.primeTime()))


@Comp7ModeState.parentOf
class Comp7MetaState(GuiImplViewLobbyState):
    STATE_ID = 'meta'
    VIEW_KEY = ViewKey(R.views.comp7.mono.lobby.meta_root_view())
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(Comp7MetaState, self).__init__(MetaRootView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(Comp7MetaProgressionState(StateFlags.INITIAL))
        lsm.addState(Comp7MetaQualificationState())
        lsm.addState(Comp7MetaRankRewardsState())
        lsm.addState(Comp7MetaYearlyRewardsState())
        lsm.addState(Comp7MetaWeeklyQuestsState())
        lsm.addState(Comp7MetaShopState())
        lsm.addState(Comp7MetaLeaderboardState())
        lsm.addState(Comp7MetaYearlyStatisticsState())

    def registerTransitions(self):
        parent = self.getParent()
        for state in self.getChildrenStates():
            parent.addNavigationTransition(state)

        lsm = self.getMachine()
        qualification = lsm.getStateByCls(Comp7MetaQualificationState)
        parent.addTransition(HijackTransition(Comp7MetaProgressionState, WeakMethodProxy(self._hijackQualificationCondition)), qualification)
        rootState = parent.getParent()
        shopState = lsm.getStateByCls(Comp7MetaShopState)
        rootState.addNavigationTransition(shopState)

    def _hijackQualificationCondition(self, _):
        return self.__comp7Controller.isQualificationActive()

    def _onEntered(self, event):
        super(Comp7MetaState, self)._onEntered(event)
        self.__comp7Controller.onQualificationStateUpdated += self.__onQualificationUpdated

    def _onExited(self):
        super(Comp7MetaState, self)._onExited()
        self.__comp7Controller.onQualificationStateUpdated -= self.__onQualificationUpdated

    def __onQualificationUpdated(self):
        Comp7MetaProgressionState.goTo()


metaStateNavigationButtons = (LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showComp7InfoPage, tooltipHeader=backport.text(R.strings.comp7_ext.tooltip.infoPageButton.header())), LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.QUESTION, onMoreInfoRequested=showComp7WhatsNewScreen, tooltipHeader=backport.text(R.strings.comp7_ext.tooltip.whatsNewButton.header())))

@Comp7MetaState.parentOf
class Comp7MetaProgressionState(LobbyState, IMetaTabState):
    STATE_ID = 'progression'

    def registerTransitions(self):
        lsm = self.getMachine()
        from gui.Scaleform.daapi.view.lobby.profile.states import ServiceRecordState
        self.addNavigationTransition(lsm.getStateByCls(ServiceRecordState), record=True)

    @property
    def tabId(self):
        return MetaRootViews.PROGRESSION

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.progression()), infos=metaStateNavigationButtons)


@Comp7MetaState.parentOf
class Comp7MetaQualificationState(LobbyState, IMetaTabState):
    STATE_ID = 'qualification'

    @property
    def tabId(self):
        return MetaRootViews.PROGRESSION

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.qualification()), infos=metaStateNavigationButtons)


@Comp7MetaState.parentOf
class Comp7MetaRankRewardsState(LobbyState, IMetaTabState):
    STATE_ID = 'rankRewards'
    __guiLoader = dependency.descriptor(IGuiLoader)

    @property
    def tabId(self):
        return MetaRootViews.RANKREWARDS

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.rankRewards()), infos=metaStateNavigationButtons)

    def registerTransitions(self):
        lsm = self.getMachine()
        state = lsm.getStateByCls(Comp7StylePreviewState)
        self.addNavigationTransition(state, record=True)

    def serializeParams(self):
        view = self.__getView()
        if view is not None:
            page = view.getPageById(self.tabId)
            if page is not None:
                return {'index': page.itemIndex}
        return {}

    def __getView(self):
        viewKey = self.getParent().getViewKey()
        return self.__guiLoader.windowsManager.getViewByLayoutID(viewKey.alias)


@Comp7MetaState.parentOf
class Comp7MetaYearlyRewardsState(LobbyState, IMetaTabState):
    STATE_ID = 'yearlyRewards'

    @property
    def tabId(self):
        return MetaRootViews.YEARLYREWARDS

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.yearlyRewards()), infos=metaStateNavigationButtons)

    def registerTransitions(self):
        lsm = self.getMachine()
        state = lsm.getStateByCls(Comp7StylePreviewState)
        self.addNavigationTransition(state, record=True)

    def compareParams(self, params, otherParams):
        return True


@Comp7MetaState.parentOf
class Comp7MetaWeeklyQuestsState(LobbyState, IMetaTabState):
    STATE_ID = 'weeklyQuests'

    @property
    def tabId(self):
        return MetaRootViews.WEEKLYQUESTS

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.weeklyQuests()), infos=metaStateNavigationButtons)


@Comp7MetaState.parentOf
class Comp7MetaShopState(LobbyState, IMetaTabState):
    STATE_ID = 'shop'
    __guiLoader = dependency.descriptor(IGuiLoader)

    @property
    def tabId(self):
        return MetaRootViews.SHOP

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.shop()), infos=metaStateNavigationButtons)

    def registerTransitions(self):
        lsm = self.getMachine()
        for cls in (Comp7StylePreviewState, Comp7VehiclePreviewState):
            state = lsm.getStateByCls(cls)
            self.addNavigationTransition(state, record=True)

    def serializeParams(self):
        view = self.__getView()
        if view is not None:
            page = view.getPageById(self.tabId)
            if page is not None:
                return {'productCD': page.currentItemCD}
        return {}

    def __getView(self):
        viewKey = self.getParent().getViewKey()
        return self.__guiLoader.windowsManager.getViewByLayoutID(viewKey.alias)


@Comp7MetaState.parentOf
class Comp7MetaLeaderboardState(LobbyState, IMetaTabState):
    STATE_ID = 'leaderboard'

    @property
    def tabId(self):
        return MetaRootViews.LEADERBOARD

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.leaderboard()), infos=metaStateNavigationButtons)


@Comp7MetaState.parentOf
class Comp7MetaYearlyStatisticsState(LobbyState, IMetaTabState):
    STATE_ID = 'yearlyStatistics'

    @property
    def tabId(self):
        return MetaRootViews.YEARLYSTATISTICS

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.meta.yearlyStatistics()), infos=metaStateNavigationButtons)


@Comp7ModeState.parentOf
class Comp7StylePreviewState(SFViewLobbyState):
    STATE_ID = 'preview/style'
    VIEW_KEY = ViewKey(COMP7_HANGAR_ALIASES.COMP7_STYLE_PREVIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(Comp7StylePreviewState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.preview.style()))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(Comp7StylePreviewState, self)._onEntered(event)

    def _onExited(self):
        self.__cachedParams = {}
        super(Comp7StylePreviewState, self)._onExited()


@Comp7ModeState.parentOf
class Comp7VehiclePreviewState(SFViewLobbyState):
    STATE_ID = 'preview/vehicle'
    VIEW_KEY = ViewKey(COMP7_HANGAR_ALIASES.COMP7_CONFIGURABLE_VEHICLE_PREVIEW)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7.preview.vehicle()))


class _Comp7LoadoutConfirmStatePrototype(_LoadoutConfirmStatePrototype):
    STATE_ID = 'comp7/loadoutConfirmLeave'


Comp7LoadoutState, _, _, Comp7ShellsLoadoutState, Comp7EquipmentLoadoutState, _, _ = generateBasicLoadoutStateClasses(Comp7HangarState, R.invalid, confirmStatePrototypeCls=_Comp7LoadoutConfirmStatePrototype)
Comp7EasyTankEquipState = generateEasyTankEquipStates(Comp7HangarState)
