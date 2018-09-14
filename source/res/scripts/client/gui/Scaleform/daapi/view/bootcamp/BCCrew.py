# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCCrew.py
from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
from gui.Scaleform.daapi.view.meta.BCCrewMeta import BCCrewMeta
from debug_utils import LOG_DEBUG

class BCCrew(BCCrewMeta):

    def __init__(self, ctx=None):
        super(BCCrew, self).__init__()
        self._showPersonalCase = True
        self._showRecruit = False
        self.__lastClickedSlotIndex = None
        self.__ignoreNextDropDownClose = False
        return

    def _populate(self):
        super(BCCrew, self)._populate()

    def _dispose(self):
        super(BCCrew, self)._dispose()

    def onTankmanClick(self, slotIndex):
        self.__lastClickedSlotIndex = slotIndex
        if slotIndex == 0:
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.runViewAlias('bootcampCrewList')
        self.__ignoreNextDropDownClose = False

    def onDropDownClosed(self, slotIndex):
        if slotIndex == 0 and not self.__ignoreNextDropDownClose:
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.runViewAlias('hangar')
        self.__ignoreNextDropDownClose = False

    def openPersonalCase(self, value, tabNumber):
        if self.__lastClickedSlotIndex == 0:
            self.__ignoreNextDropDownClose = True
        super(BCCrew, self).openPersonalCase(value, tabNumber)

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        pass
