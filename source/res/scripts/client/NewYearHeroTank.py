# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearHeroTank.py
from HeroTank import HeroTank
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.impl.new_year.navigation import NewYearNavigation

class NewYearHeroTank(HeroTank):

    def onSelect(self):
        self.setState(CameraMovementStates.MOVING_TO_OBJECT)
        NewYearNavigation.switchToHeroTank()
        self.setState(CameraMovementStates.ON_OBJECT)

    def onDeselect(self, newSelectedObject):
        self.setState(CameraMovementStates.FROM_OBJECT)
        if not newSelectedObject:
            return
        newSelectedObject.setState(CameraMovementStates.MOVING_TO_OBJECT)
        NewYearNavigation.switchFromHeroTank()
        newSelectedObject.setState(CameraMovementStates.ON_OBJECT)
