# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_cfg_view.py
from __future__ import absolute_import
from adisp import adisp_process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.Scaleform.daapi.view.meta.VehiclePostProgressionViewMeta import VehiclePostProgressionViewMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.event_dispatcher import showVehicleHubModules, showVehicleHubOverview, selectVehicleInHangar
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.veh_post_progression.sounds import PP_VIEW_SOUND_SPACE
from gui.veh_post_progression.vo_builders.cfg_page_vos import getDataVO, getTitleVO
from helpers import dependency
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from skeletons.gui.game_control import IVehicleComparisonBasket, IHeroTankController
from skeletons.gui.shared import IItemsCache

class VehiclePostProgressionCfgView(VehiclePostProgressionViewMeta):
    _COMMON_SOUND_SPACE = PP_VIEW_SOUND_SPACE
    _PROGRESSION_INJECT_ALIAS = HANGAR_ALIASES.POST_PROGRESSION_INJECT
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __itemsCache = dependency.descriptor(IItemsCache)
    __heroTanks = dependency.descriptor(IHeroTankController)

    def __init__(self, ctx=None):
        super(VehiclePostProgressionCfgView, self).__init__(ctx)
        self._intCD = ctx['intCD']
        self._goToVehicleAllowed = ctx.get('goToVehicleAllowed', False)
        self._overrideVehiclePreviewEvent = ctx.get('overrideVehiclePreviewEvent', None)
        return

    def compareVehicle(self):
        self.__cmpBasket.addVehicle(self._intCD)

    @adisp_process
    def demountAllPairs(self):
        vehicle = self._vehicle
        toDiscardIDs = vehicle.postProgression.getInstalledMultiIds()
        action = ActionsFactory.getAction(ActionsFactory.DISCARD_POST_PROGRESSION_PAIRS, vehicle, *toDiscardIDs)
        yield ActionsFactory.asyncDoAction(action)

    def goToVehicleView(self):
        if self._vehicle.isInInventory:
            selectVehicleInHangar(self._intCD)
        elif self._overrideVehiclePreviewEvent:
            g_eventBus.handleEvent(self._overrideVehiclePreviewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            showVehicleHubOverview(self._intCD)

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

    def _getDiffVehicle(self):
        return self.__itemsCache.items.getVehicleCopy(self._vehicle)

    def _getModVehicle(self):
        return self.__itemsCache.items.getVehicleCopy(self._vehicle)

    def _getVehicle(self):
        return self.__itemsCache.items.getItemByCD(self._intCD)

    def _checkNationChange(self):
        if not self._vehicle.activeInNationGroup:
            self._intCD = next(iterVehTypeCDsInNationGroup(self._vehicle.intCD))
            self._progressionInject.getInjectView().invalidateVehicle(self._intCD)
            g_postProgressionVehicle.setCustomVehicle(None)
            self._updateVehicle()
        return

    def _updateData(self, *_):
        freeExp = self.__itemsCache.items.stats.actualFreeXP
        dataVO = getDataVO(self._vehicle, freeExp, self._goToVehicleAllowed)
        self.as_setDataS(dataVO)

    def _updateTitle(self):
        self.as_setVehicleTitleS(getTitleVO(self._vehicle))

    def __onCmpBasketChange(self, changedData):
        if changedData.isFullChanged:
            self._updateData()

    def __onGoBackAction(self):
        self.onClose()

    def __onResearchAction(self):
        showVehicleHubModules(self._intCD)
