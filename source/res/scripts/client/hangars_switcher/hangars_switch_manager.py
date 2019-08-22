# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangars_switcher/hangars_switch_manager.py
from helpers import dependency
from skeletons.hangars_switcher import IHangarsSwitchManager
from skeletons.hangars_switcher import IHangarsSwitcher
from skeletons.gui.shared.utils import IHangarSpace
from gui.Scaleform.Waiting import Waiting
_WAITING_MSG = 'waitForHangarsSwitcher'

class HangarsSwitchManager(IHangarsSwitchManager):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HangarsSwitchManager, self).__init__()
        self.__switcher = None
        self.__postponedHangarName = None
        self.__lastHangarName = None
        return

    def init(self):
        self.hangarSpace.onSpaceDestroy += self.__onHangarSpaceDestroy
        self.hangarSpace.onSpaceChangedByAction += self.__onSpaceChangeByEventNotification

    def destroy(self):
        self.hangarSpace.onSpaceDestroy -= self.__onHangarSpaceDestroy
        self.hangarSpace.onSpaceChangedByAction -= self.__onSpaceChangeByEventNotification
        self.unregisterHangarsSwitcher()
        self.__lastHangarName = None
        return

    def changeHangar(self, hangarName):
        if not hangarName:
            return
        elif self.__switcher is None:
            self.__postponedHangarName = hangarName
            Waiting.show(_WAITING_MSG, isSingle=True)
            return
        else:
            self.__lastHangarName = hangarName
            self.__switcher.switchToHangar(hangarName)
            return

    def registerHangarsSwitcher(self, switcher):
        if not isinstance(switcher, IHangarsSwitcher):
            return False
        else:
            if self.__switcher is not None:
                self.unregisterHangarsSwitcher()
            self.__switcher = switcher
            postponedHangarName = self.__removePostponedHangarName()
            if postponedHangarName:
                self.__switcher.switchToHangar(postponedHangarName)
            return True

    def unregisterHangarsSwitcher(self):
        self.__removePostponedHangarName()
        self.__switcher = None
        return

    @property
    def lastHangarName(self):
        return self.__lastHangarName

    def __removePostponedHangarName(self):
        postponedHangarName = None
        if self.__postponedHangarName:
            postponedHangarName = self.__postponedHangarName
            self.__postponedHangarName = None
            Waiting.hide(_WAITING_MSG)
        return postponedHangarName

    def __onHangarSpaceDestroy(self, _):
        self.unregisterHangarsSwitcher()

    def __onSpaceChangeByEventNotification(self):
        self.__lastHangarName = None
        return
