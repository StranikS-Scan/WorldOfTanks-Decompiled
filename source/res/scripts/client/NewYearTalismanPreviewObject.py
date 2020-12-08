# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanPreviewObject.py
from NewYearTalismanBaseObject import NewYearTalismanBaseObject
from gui.impl.new_year.sounds import NewYearSoundsManager
_EVENT_REVEAL_OFF = 'ev_reveal_off'

class NewYearTalismanPreviewObject(NewYearTalismanBaseObject):

    def onEnterWorld(self, prereqs):
        super(NewYearTalismanPreviewObject, self).onEnterWorld(prereqs)
        self._talismanController.talismanPreviewAdded(self)

    def onLeaveWorld(self):
        self._talismanController.talismanPreviewRemoved(self)
        super(NewYearTalismanPreviewObject, self).onLeaveWorld()

    def onMouseClick(self):
        if self.__isTalismanReceived():
            return
        if not self._talismanController.mouseEventsAvailable():
            return
        NewYearSoundsManager.setStylesTalismanSwitchBox(self.talismanName)
        self._talismanController.previewMoveTo(self.talismanName)

    def _onAnimatorEvent(self, eventName):
        if eventName == _EVENT_REVEAL_OFF:
            self._stopCongratsEffect()
            self._talismanController.previewCongratsFinished(self.talismanName)

    def _addEdgeDetect(self):
        if not self.__isTalismanReceived():
            super(NewYearTalismanPreviewObject, self)._addEdgeDetect()

    def _delEdgeDetect(self):
        if not self.__isTalismanReceived():
            super(NewYearTalismanPreviewObject, self)._delEdgeDetect()

    def __isTalismanReceived(self):
        selected = [ item.getSetting() for item in self._newYearController.getTalismans(isInInventory=True) ]
        return self.talismanName in selected
