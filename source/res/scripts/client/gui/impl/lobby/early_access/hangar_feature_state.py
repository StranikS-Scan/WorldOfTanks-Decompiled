# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/hangar_feature_state.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.lobby.early_access.early_access_window_events import updateVisibilityHangarHeaderMenu
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController

class EarlyAccessHangarFeatureState(object):
    __slots__ = ('__activeLayoutIDs', '__isInVehicleState')
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)

    def __init__(self):
        self.__activeLayoutIDs = set()
        self.__isInVehicleState = False

    def enter(self, layoutID, activateVehicleState=False):
        if layoutID in self.__activeLayoutIDs:
            return
        if not self.__activeLayoutIDs:
            updateVisibilityHangarHeaderMenu(isVisible=False)
        if activateVehicleState and not self.__isInVehicleState:
            self.__isInVehicleState = True
            cgfCameraManager = self.__earlyAccessController.cgfCameraManager
            cgfCameraManager.allowSetMinDist(False)
            cgfCameraManager.enableShiftedMode(True)
            cgfCameraManager.switchToTank(instantly=False)
        self.__activeLayoutIDs.add(layoutID)

    def exit(self, layoutID):
        self.__activeLayoutIDs.remove(layoutID)
        if not self.__activeLayoutIDs:
            updateVisibilityHangarHeaderMenu(isVisible=True)
            if self.__isInVehicleState:
                g_currentPreviewVehicle.selectNoVehicle()
                cgfCameraManager = self.__earlyAccessController.cgfCameraManager
                if cgfCameraManager:
                    cgfCameraManager.allowSetMinDist(True)
                    cgfCameraManager.enableShiftedMode(False)
                    cgfCameraManager.switchToTank(instantly=False)
                self.__isInVehicleState = False

    def isInVehicleState(self):
        return self.__isInVehicleState

    def isLayoutIdActive(self, layoutID):
        return layoutID in self.__activeLayoutIDs
