# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_cfg_view.py
from functools import partial
from adisp import adisp_process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.go_back_helper import BackButtonContextKeys
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VEHICLE_PREVIEW_ALIASES
from gui.Scaleform.daapi.view.meta.VehiclePostProgressionViewMeta import VehiclePostProgressionViewMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.lobby.veh_post_progression.post_progression_intro import getPostProgressionInfoWindowProc
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.veh_post_progression.sounds import PP_VIEW_SOUND_SPACE
from gui.veh_post_progression.vo_builders.cfg_page_vos import getDataVO, getTitleVO
from helpers import dependency
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from skeletons.gui.game_control import IVehicleComparisonBasket, IHeroTankController
from skeletons.gui.shared import IItemsCache
_HERO_PREVIEW_ALIASES = (VIEW_ALIAS.HERO_VEHICLE_PREVIEW, VIEW_ALIAS.RESOURCE_WELL_HERO_VEHICLE_PREVIEW)

def _defaultExitEvent():
    return events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR), name=VIEW_ALIAS.LOBBY_HANGAR)


class VehiclePostProgressionCfgView(VehiclePostProgressionViewMeta):
    _COMMON_SOUND_SPACE = PP_VIEW_SOUND_SPACE
    _PROGRESSION_INJECT_ALIAS = HANGAR_ALIASES.POST_PROGRESSION_INJECT
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __itemsCache = dependency.descriptor(IItemsCache)
    __heroTanks = dependency.descriptor(IHeroTankController)

    def __init__(self, ctx=None):
        super(VehiclePostProgressionCfgView, self).__init__(ctx)
        self._intCD = ctx['intCD']
        self._exitEvent = ctx.get(BackButtonContextKeys.EXIT) or _defaultExitEvent()

    def onAboutClick(self):
        getPostProgressionInfoWindowProc().show(self.getParentWindow())

    def onGoBackClick(self):
        self._onExit()

    def compareVehicle(self):
        self.__cmpBasket.addVehicle(self._intCD)

    @adisp_process
    def demountAllPairs(self):
        vehicle = self._vehicle
        toDiscardIDs = vehicle.postProgression.getInstalledMultiIds()
        action = ActionsFactory.getAction(ActionsFactory.DISCARD_POST_PROGRESSION_PAIRS, vehicle, *toDiscardIDs)
        yield ActionsFactory.asyncDoAction(action)

    def goToVehicleView(self):
        if self._vehicle.isPreviewAllowed():
            if self._exitEvent.alias in VEHICLE_PREVIEW_ALIASES:
                self._onExit()
            else:
                backCb = partial(shared_events.showVehPostProgressionView, self._intCD, self._exitEvent)
                shared_events.showVehiclePreview(self._intCD, self.alias, previewBackCb=backCb)
        elif self._vehicle.isInInventory:
            shared_events.selectVehicleInHangar(self._intCD)

    def _addListeners(self):
        super(VehiclePostProgressionCfgView, self)._addListeners()
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self._updateData,
         'cache.mayConsumeWalletResources': self._updateData})
        self.__cmpBasket.onChange += self.__onCmpBasketChange
        self.__cmpBasket.onSwitchChange += self._updateData
        progressionInjectView = self._progressionInject.getInjectView()
        progressionInjectView.onGoBackAction += self.__onGoBackAction
        progressionInjectView.onResearchAction += self.__onResearchAction

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__cmpBasket.onSwitchChange -= self._updateData
        self.__cmpBasket.onChange -= self.__onCmpBasketChange
        progressionInjectView = self._progressionInject.getInjectView()
        if progressionInjectView:
            progressionInjectView.onResearchAction -= self.__onResearchAction
            progressionInjectView.onGoBackAction -= self.__onGoBackAction
        super(VehiclePostProgressionCfgView, self)._removeListeners()

    def _onExit(self):
        if self._exitEvent.alias in _HERO_PREVIEW_ALIASES and self._exitEvent.ctx.get('itemCD') == self.__heroTanks.getCurrentTankCD():
            self.__goToHeroTank()
        else:
            g_eventBus.handleEvent(self._exitEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def _getDiffVehicle(self):
        return self.__itemsCache.items.getVehicleCopy(self._vehicle)

    def _getModVehicle(self):
        return self.__itemsCache.items.getVehicleCopy(self._vehicle)

    def _getVehicle(self):
        return self.__itemsCache.items.getItemByCD(self._intCD)

    def _checkNationChange(self):
        if not self._vehicle.activeInNationGroup:
            self._intCD = iterVehTypeCDsInNationGroup(self._vehicle.intCD).next()
            self._progressionInject.getInjectView().invalidateVehicle(self._intCD)
            g_postProgressionVehicle.setCustomVehicle(None)
            self._updateVehicle()
        return

    def _updateData(self, *_):
        freeExp = self.__itemsCache.items.stats.actualFreeXP
        self.as_setDataS(getDataVO(self._vehicle, freeExp, self._exitEvent))

    def _updateTitle(self):
        self.as_setVehicleTitleS(getTitleVO(self._vehicle))

    def __onCmpBasketChange(self, changedData, _=None):
        if changedData.isFullChanged:
            self._updateData()

    def __onGoBackAction(self):
        self.as_onEscPressedS()

    def __onResearchAction(self):
        exitToTechTree = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={BackButtonContextKeys.NATION: self._vehicle.nationName})
        exitToResearchPage = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_RESEARCH), ctx={BackButtonContextKeys.ROOT_CD: self._vehicle.intCD,
         BackButtonContextKeys.EXIT: exitToTechTree})
        g_eventBus.handleEvent(exitToResearchPage, scope=EVENT_BUS_SCOPE.LOBBY)

    def __goToHeroTank(self):
        ctx = self._exitEvent.ctx
        shared_events.goToHeroTankOnScene(vehTypeCompDescr=ctx.get('itemCD'), previewAlias=ctx.get('previewAlias'), previewBackCb=ctx.get('previewBackCb'), previousBackAlias=ctx.get('previousBackAlias'), hangarVehicleCD=ctx.get('hangarVehicleCD'), instantly=True)
