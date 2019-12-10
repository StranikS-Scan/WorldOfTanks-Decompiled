# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanObject.py
from NewYearTalismanBaseObject import NewYearTalismanBaseObject
from gui.Scaleform.managers.cursor_mgr import CursorManager
_EVENT_REVEAL_IN = 'ev_reveal_in'

class NewYearTalismanObject(NewYearTalismanBaseObject):

    def onEnterWorld(self, prereqs):
        super(NewYearTalismanObject, self).onEnterWorld(prereqs)
        self._talismanController.talismanAdded(self)

    def onLeaveWorld(self):
        self._talismanController.talismanRemoved(self)
        super(NewYearTalismanObject, self).onLeaveWorld()

    def onMouseClick(self):
        if self.__isGiftReceived():
            return
        if not self._talismanController.mouseEventsAvailable():
            return
        if not self.__isInInventory():
            return
        self._talismanController.giftMoveTo(self.talismanName)

    def _onAnimatorEvent(self, eventName):
        if eventName == _EVENT_REVEAL_IN:
            self._stopCongratsEffect()

    def _addEdgeDetect(self):
        if not self.__isGiftReceived() and self.__isInInventory():
            super(NewYearTalismanObject, self)._addEdgeDetect()

    def _delEdgeDetect(self):
        if not self.__isGiftReceived() and self.__isInInventory():
            super(NewYearTalismanObject, self)._delEdgeDetect()

    def _onAnimatorStarted(self):
        self._talismanController.talismanAnimatorStarted(self.talismanName)

    def _hoverOutCursorType(self):
        return CursorManager.ARROW if self._talismanController.isInGiftConfirmState() else CursorManager.DRAG_OPEN

    def __isGiftReceived(self):
        return self._newYearController.isTalismanToyTaken()

    def __isInInventory(self):
        inventory = [ item.getSetting() for item in self._newYearController.getTalismans(isInInventory=True) ]
        return self.talismanName in inventory
