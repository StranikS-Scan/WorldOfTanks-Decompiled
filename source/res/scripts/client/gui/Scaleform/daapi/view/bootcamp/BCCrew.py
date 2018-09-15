# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCCrew.py
from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
from bootcamp.BootcampGarage import g_bootcampGarage

class BCCrew(Crew):

    def __init__(self, ctx=None):
        super(BCCrew, self).__init__()
        self._showPersonalCase = True
        self._showRecruit = False
        self.__lastClickedSlotIndex = None
        self.__ignoreNextDropDownClose = False
        return

    def onTankmanClick(self, slotIndex):
        self.__lastClickedSlotIndex = slotIndex
        if slotIndex == 0:
            g_bootcampGarage.runViewAlias('bootcampCrewList')
        self.__ignoreNextDropDownClose = False

    def onDropDownClosed(self, slotIndex):
        if slotIndex == 0 and not self.__ignoreNextDropDownClose:
            g_bootcampGarage.runViewAlias('hangar')
        self.__ignoreNextDropDownClose = False

    def openPersonalCase(self, value, tabNumber):
        if self.__lastClickedSlotIndex == 0:
            self.__ignoreNextDropDownClose = True
        super(BCCrew, self).openPersonalCase(value, tabNumber)

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        pass

    def _populate(self):
        super(BCCrew, self)._populate()
        observer = self.app.bootcampManager.getObserver('BCCrewObserver')
        if observer is not None:
            observer.onTankmanClickEvent += self.onTankmanClick
            observer.onDropDownClosedEvent += self.onDropDownClosed
        return

    def _dispose(self):
        observer = self.app.bootcampManager.getObserver('BCCrewObserver')
        if observer is not None:
            observer.onTankmanClickEvent -= self.onTankmanClick
            observer.onDropDownClosedEvent -= self.onDropDownClosed
        super(BCCrew, self)._dispose()
        return
