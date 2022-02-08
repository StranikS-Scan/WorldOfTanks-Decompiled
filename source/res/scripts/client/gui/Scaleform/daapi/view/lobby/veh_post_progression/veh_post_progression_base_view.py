# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_base_view.py
import typing
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehPostProgressionDataProvider
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.Scaleform.daapi.view.meta.VehicleParametersWithHighlightMeta import VehicleParametersWithHighlightMeta
from gui.Scaleform.daapi.view.meta.VehiclePostProgressionViewBaseMeta import VehiclePostProgressionViewBaseMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from post_progression_common import VehicleState

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


class VehiclePostProgressionBaseView(VehiclePostProgressionViewBaseMeta):
    _PROGRESSION_INJECT_ALIAS = ''
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(VehiclePostProgressionBaseView, self).__init__()
        self._progressionInject = None
        self._vehicle = None
        self._parametersView = None
        self.__ctx = ctx
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == self._PROGRESSION_INJECT_ALIAS:
            self.__ctx['parentAlias'] = self.alias
            super(VehiclePostProgressionBaseView, self).registerFlashComponent(component, alias, self.__ctx)
        else:
            super(VehiclePostProgressionBaseView, self).registerFlashComponent(component, alias)

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == HANGAR_ALIASES.POST_PROGRESSION_VEHICLE_PARAMS:
            self._parametersView = viewPy
        elif alias == self._PROGRESSION_INJECT_ALIAS:
            self._progressionInject = viewPy

    def _populate(self):
        super(VehiclePostProgressionBaseView, self)._populate()
        self._updateVehicle()
        self._checkPostProgressionExists()
        self._updateTitle()
        self._updateData()
        self._parametersView.update()
        self._addListeners()

    def _dispose(self):
        self._removeListeners()
        self._parametersView = None
        self._progressionInject = None
        g_postProgressionVehicle.clear()
        super(VehiclePostProgressionBaseView, self)._dispose()
        return

    def _addListeners(self):
        self.__itemsCache.onSyncCompleted += self._onSyncCompleted
        progressionInjectView = self._progressionInject.getInjectView()
        progressionInjectView.onViewRendered += self.__onViewRendered
        progressionInjectView.onCustomProgressionState += self.__onCustomProgressionState

    def _removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self._onSyncCompleted
        progressionInjectView = self._progressionInject.getInjectView()
        if progressionInjectView:
            progressionInjectView.onViewRendered -= self.__onViewRendered
            progressionInjectView.onCustomProgressionState -= self.__onCustomProgressionState

    def _onExit(self):
        raise NotImplementedError

    def _getDiffVehicle(self):
        raise NotImplementedError

    def _getModVehicle(self):
        raise NotImplementedError

    def _getVehicle(self):
        raise NotImplementedError

    def _checkNationChange(self):
        raise NotImplementedError

    def _updateData(self, *_):
        raise NotImplementedError

    def _updateTitle(self):
        raise NotImplementedError

    def _onSyncCompleted(self, reason, diff):
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self._vehicle.intCD in changedVehicles or reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self._updateVehicle()
            self._checkPostProgressionExists()
            self._checkNationChange()
            self._updateTitle()
            self._updateData()
            self._parametersView.update(useAnim=False)

    def _checkPostProgressionExists(self):
        if not self._vehicle.isPostProgressionExists:
            self._onExit()

    def _updateVehicle(self):
        self._vehicle = self._getVehicle()
        g_postProgressionVehicle.setDefaultVehicle(self._vehicle)
        prevProgressionState = g_postProgressionVehicle.item.postProgression.getState()
        g_postProgressionVehicle.setCustomVehicle(self._getModVehicle())
        self.__updateCustomVehicle(prevProgressionState, isMerge=True)

    def __onViewRendered(self):
        self.as_showS()

    def __createDiffVehicle(self, prevState, customState):
        diffState = g_postProgressionVehicle.defaultItem.postProgression.getState()
        for stepID, pairType in customState.pairs.iteritems():
            if prevState.getPair(stepID) != pairType:
                diffState.addUnlock(stepID)
                diffState.setPair(stepID, pairType)

        diffVehicle = self._getDiffVehicle()
        diffVehicle.installPostProgression(diffState, True)
        return diffVehicle

    def __onCustomProgressionState(self, state, needDiff):
        self.__updateCustomVehicle(state, needDiff=needDiff)
        self._parametersView.update(useAnim=False)

    def __updateCustomVehicle(self, state, isMerge=False, needDiff=False):
        prevState = g_postProgressionVehicle.item.postProgression.getState()
        customState = prevState | state if isMerge else state
        g_postProgressionVehicle.item.installPostProgression(customState, True)
        g_postProgressionVehicle.setDiffVehicle(self.__createDiffVehicle(prevState, customState) if needDiff else None)
        return
