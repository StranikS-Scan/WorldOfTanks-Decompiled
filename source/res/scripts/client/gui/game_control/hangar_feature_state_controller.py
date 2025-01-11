# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hangar_feature_state_controller.py
import CGF
import logging
from frameworks.wulf.gui_constants import ShowingStatus
from skeletons.gui.game_control import IHangarFeatureStateController
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared.utils import IHangarSpace
from cgf_components.hangar_camera_manager import HangarCameraManager
from gui.impl.gen import R
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.lobby.early_access.early_access_window_events import updateVisibilityHangarHeaderMenu
_logger = logging.getLogger(__name__)
_VEHICLE_STATE_VIEWS_IDS = {R.views.lobby.early_access.EarlyAccessVehicleView(), R.views.lobby.personal_missions.PersonalMissionsVehicleView()}

class HangarFeatureStateController(IHangarFeatureStateController):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        self.__activeLayoutIDs = dict()
        self.__isInVehicleState = False

    @property
    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def cgfCameraManager(self, hangarSpace=None):
        return CGF.getManager(hangarSpace.space.getSpaceID(), HangarCameraManager) if hangarSpace is not None and hangarSpace.space is not None else None

    def onLobbyInited(self, event):
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreate
        self.__hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def onAccountBecomeNonPlayer(self):
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self.__hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy

    def enter(self, layoutID, doHideHeader=True):
        if layoutID in self.__activeLayoutIDs:
            self.__increaseCounter(layoutID)
            return
        if not self.__activeLayoutIDs and doHideHeader:
            updateVisibilityHangarHeaderMenu(isVisible=False)
        self.__increaseCounter(layoutID)
        self.__updateVehicleState()
        self.__updateScene()

    def exit(self, layoutID):
        if not self.__activeLayoutIDs:
            return
        self.__decreaseCounter(layoutID)
        self.__updateVehicleState()
        self.__updateScene()
        if not self.__activeLayoutIDs:
            updateVisibilityHangarHeaderMenu(isVisible=True)
            g_currentPreviewVehicle.selectNoVehicle()

    def __updateScene(self):
        cgfCameraManager = self.cgfCameraManager
        if cgfCameraManager:
            if self.__isInVehicleState != cgfCameraManager.isShifted:
                cgfCameraManager.allowSetMinDist(not self.__isInVehicleState)
                cgfCameraManager.enableShiftedMode(self.__isInVehicleState)
                cgfCameraManager.switchToTank(instantly=False)
        else:
            _logger.error('HangarCameraManager not found! Hangar space could be None.')

    def __updateVehicleState(self):
        wasVehicleStateEverActive = len(self.__activeLayoutIDs) > 0 and self.__isInVehicleState
        self.__isInVehicleState = wasVehicleStateEverActive or bool(_VEHICLE_STATE_VIEWS_IDS.intersection(self.__activeLayoutIDs))

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

    def __onSpaceCreate(self):
        if self.__activeLayoutIDs:
            self.__updateVehicleState()
            self.__updateScene()

    def __onSpaceDestroy(self, _):
        shownViewIDs = [ layoutID for layoutID in self.__activeLayoutIDs if self.__guiLoader.windowsManager.getViewByLayoutID(layoutID).showingStatus == ShowingStatus.SHOWN ]
        if shownViewIDs:
            for layoutID in shownViewIDs:
                self.exit(layoutID)
