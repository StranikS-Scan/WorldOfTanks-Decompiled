# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_view.py
import typing
from functools import partial
from adisp import process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehPostProgressionDataProvider
from gui.Scaleform.daapi.view.lobby.go_back_helper import BackButtonContextKeys
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.Scaleform.daapi.view.meta.VehicleParametersWithHighlightMeta import VehicleParametersWithHighlightMeta
from gui.Scaleform.daapi.view.meta.VehiclePostProgressionViewMeta import VehiclePostProgressionViewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.lobby.veh_post_progression.post_progression_intro import getPostProgressionInfoWindowProc
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.veh_post_porgression.vo_builders.main_page_vos import getDataVO, getTitleVO
from helpers import dependency
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from uilogging.veh_post_progression.constants import LogGroups, ParentScreens
from uilogging.veh_post_progression.loggers import VehPostProgressionLogger
if typing.TYPE_CHECKING:
    from post_progression_common import VehicleState

def _defaultExitEvent():
    return events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR), name=VIEW_ALIAS.LOBBY_HANGAR)


class VehPostProgressionVehicleParams(VehicleParametersWithHighlightMeta):

    def __init__(self):
        super(VehPostProgressionVehicleParams, self).__init__()
        self._expandedGroups = {key:False for key in self._expandedGroups.iterkeys()}

    def onParamClick(self, paramID):
        isOpened = not self._expandedGroups[paramID]
        self._expandedGroups[paramID] = isOpened
        self._setDPUseAnimAndRebuild(False)

    def rebuildParams(self):
        super(VehPostProgressionVehicleParams, self).rebuildParams()
        self.as_showChangesS()

    def _createDataProvider(self):
        return VehPostProgressionDataProvider(TOOLTIPS_CONSTANTS.VEHICLE_POST_PROGRESSION_PARAMETERS)

    def _getVehicleCache(self):
        return g_postProgressionVehicle


class VehiclePostProgressionView(VehiclePostProgressionViewMeta):
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __itemsCache = dependency.descriptor(IItemsCache)
    __infoButtonLogger = VehPostProgressionLogger(LogGroups.INFO_BUTTON)
    __compareButtonLogger = VehPostProgressionLogger(LogGroups.ADD_TO_COMPARE)

    def __init__(self, ctx=None):
        super(VehiclePostProgressionView, self).__init__()
        self.__parametersView = None
        self.__progressionInject = None
        self.__vehicle = None
        self.__ctx = ctx
        self.__intCD = self.__ctx['intCD']
        self.__exitEvent = ctx.get(BackButtonContextKeys.EXIT) or _defaultExitEvent()
        return

    def onAboutClick(self):
        getPostProgressionInfoWindowProc().show(self.getParentWindow())
        self.__infoButtonLogger.logClick(parentScreen=ParentScreens.MODIFICATIONS_TREE)

    def onGoBackClick(self):
        g_eventBus.handleEvent(self.__exitEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def compareVehicle(self):
        self.__cmpBasket.addVehicle(self.__intCD)
        self.__compareButtonLogger.logClick(parentScreen=ParentScreens.MODIFICATIONS_TREE)

    @process
    def demountAllPairs(self):
        vehicle = self.__vehicle
        toDiscardIDs = vehicle.postProgression.getInstalledMultiIds()
        action = ActionsFactory.getAction(ActionsFactory.DISCARD_POST_PROGRESSION_PAIRS, vehicle, *toDiscardIDs)
        yield ActionsFactory.asyncDoAction(action)

    def goToVehicleView(self):
        if self.__vehicle.isPreviewAllowed():
            backCb = partial(shared_events.showVehPostProgressionView, self.__intCD, self.__exitEvent)
            shared_events.showVehiclePreview(self.__intCD, self.alias, previewBackCb=backCb)
        elif self.__vehicle.isInInventory:
            shared_events.selectVehicleInHangar(self.__intCD)

    def registerFlashComponent(self, component, alias, *args):
        if alias == HANGAR_ALIASES.POST_PROGRESSION_INJECT:
            super(VehiclePostProgressionView, self).registerFlashComponent(component, alias, self.__ctx)
        else:
            super(VehiclePostProgressionView, self).registerFlashComponent(component, alias)

    def _populate(self):
        super(VehiclePostProgressionView, self)._populate()
        self.__updateVehicle()
        self.__checkPostProgressionExists()
        self.__updateTitle()
        self.__updateData()
        self.__parametersView.update()
        self.__addListeners()

    def _dispose(self):
        self.__removeListeners()
        self.__parametersView = None
        self.__progressionInject = None
        g_postProgressionVehicle.clear()
        super(VehiclePostProgressionView, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == HANGAR_ALIASES.POST_PROGRESSION_VEHICLE_PARAMS:
            self.__parametersView = viewPy
        elif alias == HANGAR_ALIASES.POST_PROGRESSION_INJECT:
            self.__progressionInject = viewPy

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__updateData})
        progressionInjectView = self.__progressionInject.getInjectView()
        self.__cmpBasket.onChange += self.__onCmpBasketChange
        self.__cmpBasket.onSwitchChange += self.__updateData
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        progressionInjectView.onGoBackAction += self.onGoBackClick
        progressionInjectView.onResearchAction += self.__onResearchAction
        progressionInjectView.onCustomProgressionState += self.__onCustomProgressionState
        progressionInjectView.onViewRendered += self.__onViewRendered

    def __removeListeners(self):
        progressionInjectView = self.__progressionInject.getInjectView()
        progressionInjectView.onCustomProgressionState -= self.__onCustomProgressionState
        progressionInjectView.onResearchAction -= self.__onResearchAction
        progressionInjectView.onGoBackAction -= self.onGoBackClick
        progressionInjectView.onViewRendered -= self.__onViewRendered
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__cmpBasket.onSwitchChange -= self.__updateData
        self.__cmpBasket.onChange -= self.__onCmpBasketChange
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onCmpBasketChange(self, changedData):
        if changedData.isFullChanged:
            self.__updateData()

    def __onCustomProgressionState(self, state, needDiff):
        self.__updateCustomVehicle(state, needDiff=needDiff)
        self.__parametersView.update(useAnim=False)

    def __onViewRendered(self):
        self.as_showS()

    def __onResearchAction(self):
        exitToTechTree = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={BackButtonContextKeys.NATION: self.__vehicle.nationName})
        exitToResearchPage = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_RESEARCH), ctx={BackButtonContextKeys.ROOT_CD: self.__vehicle.intCD,
         BackButtonContextKeys.EXIT: exitToTechTree})
        g_eventBus.handleEvent(exitToResearchPage, scope=EVENT_BUS_SCOPE.LOBBY)

    def __onSyncCompleted(self, reason, diff):
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self.__intCD in changedVehicles or reason in (CACHE_SYNC_REASON.SHOW_GUI, CACHE_SYNC_REASON.SHOP_RESYNC):
            self.__updateVehicle()
            self.__checkPostProgressionExists()
            self.__checkNationChange()
            self.__updateTitle()
            self.__updateData()
            self.__parametersView.update(useAnim=False)

    def __checkNationChange(self):
        if not self.__vehicle.activeInNationGroup:
            self.__intCD = iterVehTypeCDsInNationGroup(self.__vehicle.intCD).next()
            self.__progressionInject.getInjectView().invalidateVehicle(self.__intCD)
            g_postProgressionVehicle.setCustomVehicle(None)
            self.__updateVehicle()
        return

    def __checkPostProgressionExists(self):
        if not self.__vehicle.isPostProgressionExists:
            self.onGoBackClick()

    def __createDiffVehicle(self, prevState, customState):
        diffState = g_postProgressionVehicle.defaultItem.postProgression.getState()
        for stepID, pairType in customState.pairs.iteritems():
            if prevState.getPair(stepID) != pairType:
                diffState.addUnlock(stepID)
                diffState.setPair(stepID, pairType)

        diffVehicle = self.__itemsCache.items.getVehicleCopy(g_postProgressionVehicle.defaultItem)
        diffVehicle.installPostProgression(diffState, True)
        return diffVehicle

    def __updateData(self, *_):
        freeExp = self.__itemsCache.items.stats.actualFreeXP
        self.as_setDataS(getDataVO(self.__vehicle, freeExp, self.__exitEvent))

    def __updateTitle(self):
        self.as_setVehicleTitleS(getTitleVO(self.__vehicle))

    def __updateCustomVehicle(self, state, isMerge=False, needDiff=False):
        prevState = g_postProgressionVehicle.item.postProgression.getState()
        customState = prevState | state if isMerge else state
        g_postProgressionVehicle.item.installPostProgression(customState, True)
        g_postProgressionVehicle.setDiffVehicle(self.__createDiffVehicle(prevState, customState) if needDiff else None)
        return

    def __updateVehicle(self):
        self.__vehicle = self.__itemsCache.items.getItemByCD(self.__intCD)
        g_postProgressionVehicle.setDefaultVehicle(self.__vehicle)
        prevProgressionState = g_postProgressionVehicle.item.postProgression.getState()
        g_postProgressionVehicle.setCustomVehicle(self.__itemsCache.items.getVehicleCopy(self.__vehicle))
        self.__updateCustomVehicle(prevProgressionState, isMerge=True)
