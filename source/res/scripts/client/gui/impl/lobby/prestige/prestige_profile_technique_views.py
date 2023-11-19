# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/prestige/prestige_profile_technique_views.py
import logging
import typing
from constants import Configs
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.prestige.prestige_profile_technique_emblem_model import PrestigeProfileTechniqueEmblemModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_profile_technique_model import PrestigeProfileTechniqueModel
from gui.prestige.prestige_helpers import getCurrentProgress, fillPrestigeEmblemModel, getNextGradeLevel, getVehiclePrestige
from gui.impl.lobby.prestige.prestige_level_grades_tooltip_view import PrestigeLevelGradesTooltipView
from gui.impl.pub import ViewImpl
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, View
_logger = logging.getLogger(__name__)

class PrestigeProfileTechniqueCommon(ViewImpl):
    __slots__ = ('_selectedVehIntCD', '_databaseID')
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._selectedVehIntCD = None
        self._databaseID = None
        super(PrestigeProfileTechniqueCommon, self).__init__(self._createViewSettings())
        return

    def setDatabaseID(self, value):
        self._databaseID = value

    def setSelectedVehicleIntCD(self, value):
        self._selectedVehIntCD = value
        if self.viewStatus in (ViewStatus.LOADING, ViewStatus.LOADED):
            self._updateModel()

    def _getEvents(self):
        return super(PrestigeProfileTechniqueCommon, self)._getEvents() + ((self._lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange), (self._itemsCache.onSyncCompleted, self.__onSyncCompleted))

    def _initialize(self, *args, **kwargs):
        super(PrestigeProfileTechniqueCommon, self)._initialize()
        self._updateModel()

    def _createViewSettings(self):
        raise NotImplementedError

    def _updateModel(self):
        raise NotImplementedError

    def _checkData(self, method):
        if self._selectedVehIntCD is None:
            self._selectedVehIntCD = -1
            _logger.error('Error in stack of initialize.')
            nextTick(method)()
        return

    def __onServerSettingsChange(self, diff):
        if Configs.PRESTIGE_CONFIG.value in diff:
            self._updateModel()

    def __onSyncCompleted(self, *args):
        self._updateModel()


class PrestigeProfileTechniqueView(PrestigeProfileTechniqueCommon):

    def setDatabaseID(self, value):
        pass

    def createToolTipContent(self, event, contentID):
        return PrestigeLevelGradesTooltipView(vehIntCD=self._selectedVehIntCD) if contentID == R.views.lobby.prestige.tooltips.EliteLevelGradesTooltip() else super(PrestigeProfileTechniqueView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(PrestigeProfileTechniqueView, self).getViewModel()

    def _createViewSettings(self):
        return ViewSettings(R.views.lobby.prestige.views.PrestigeProfileTechniqueView(), flags=ViewFlags.VIEW, model=PrestigeProfileTechniqueModel())

    def _updateModel(self):
        self._checkData(self._updateModel)
        currentLevel, remainingPts = getVehiclePrestige(self._selectedVehIntCD, itemsCache=self._itemsCache)
        currentXP, nextLvlXP = getCurrentProgress(self._selectedVehIntCD, currentLevel, remainingPts, lobbyContext=self._lobbyContext)
        nextLevel = getNextGradeLevel(currentLevel, self._selectedVehIntCD)
        with self.viewModel.transaction() as tx:
            tx.setCurrentProgress(currentXP)
            tx.setMaxProgress(nextLvlXP)
            fillPrestigeEmblemModel(tx.emblem, currentLevel, self._selectedVehIntCD)
            fillPrestigeEmblemModel(tx.nextEmblem, nextLevel, self._selectedVehIntCD)


class PrestigeProfileTechniqueEmblemView(PrestigeProfileTechniqueCommon):

    @property
    def viewModel(self):
        return super(PrestigeProfileTechniqueEmblemView, self).getViewModel()

    def _createViewSettings(self):
        return ViewSettings(R.views.lobby.prestige.views.PrestigeProfileTechniqueEmblemView(), flags=ViewFlags.VIEW, model=PrestigeProfileTechniqueEmblemModel())

    def _updateModel(self):
        self._checkData(self._updateModel)
        currentLevel, _ = getVehiclePrestige(self._selectedVehIntCD, databaseID=self._databaseID, itemsCache=self._itemsCache)
        with self.viewModel.transaction() as tx:
            fillPrestigeEmblemModel(tx.emblem, currentLevel, self._selectedVehIntCD)
