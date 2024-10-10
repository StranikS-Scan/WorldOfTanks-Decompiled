# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/hangar_feature_state.py
import logging
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.gen import R
from gui.impl.lobby.early_access.early_access_window_events import updateVisibilityHangarHeaderMenu
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)
_VEHICLE_STATE_VIEW_ID = R.views.lobby.early_access.EarlyAccessVehicleView()

class EarlyAccessHangarFeatureState(object):
    __slots__ = ('__activeLayoutIDs', '__isInVehicleState', '__spaceID')
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.__activeLayoutIDs = dict()
        self.__isInVehicleState = False
        self.__spaceID = None
        return

    def init(self):
        self.__hangarSpace.onVehicleChanged += self.__onVehicleChanged

    def fini(self):
        self.__hangarSpace.onVehicleChanged -= self.__onVehicleChanged

    def enter(self, layoutID):
        if layoutID in self.__activeLayoutIDs:
            self.__increaseCounter(layoutID)
            return
        if not self.__activeLayoutIDs:
            updateVisibilityHangarHeaderMenu(isVisible=False)
        self.__increaseCounter(layoutID)
        self.__updateVehicleState()
        self.__updateCgfComponents()

    def exit(self, layoutID):
        self.__decreaseCounter(layoutID)
        self.__updateVehicleState()
        self.__updateCgfComponents()
        if not self.__activeLayoutIDs:
            updateVisibilityHangarHeaderMenu(isVisible=True)

    def isInVehicleState(self):
        return self.__isInVehicleState

    def isLayoutIdActive(self, layoutID):
        return layoutID in self.__activeLayoutIDs

    def __updateCgfComponents(self):
        cgfCameraManager = self.__earlyAccessController.cgfCameraManager
        if cgfCameraManager and self.__isInVehicleState != cgfCameraManager.isShifted:
            cgfCameraManager.allowSetMinDist(not self.__isInVehicleState)
            cgfCameraManager.enableShiftedMode(self.__isInVehicleState)
            cgfCameraManager.switchToTank(instantly=False)
            if not self.__isInVehicleState:
                g_currentPreviewVehicle.selectNoVehicle()

    def __updateVehicleState(self):
        self.__isInVehicleState = _VEHICLE_STATE_VIEW_ID in self.__activeLayoutIDs

    def __increaseCounter(self, layoutID):
        count = self.__activeLayoutIDs.get(layoutID, 0) + 1
        self.__activeLayoutIDs[layoutID] = count

    def __decreaseCounter(self, layoutID):
        if layoutID not in self.__activeLayoutIDs:
            _logger.warning('Cannot decrease usage count for unknown layoutID - %s', layoutID)
            return
        count = self.__activeLayoutIDs[layoutID] - 1
        self.__activeLayoutIDs[layoutID] = count
        if count == 0:
            self.__activeLayoutIDs.pop(layoutID)

    def __onVehicleChanged(self):
        self.__updateVehicleState()
        self.__updateCgfComponents()
