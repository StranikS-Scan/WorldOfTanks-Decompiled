# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/Comp7BattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class Comp7BattlePageMeta(ClassicPage):

    def showHelp(self):
        self._printOverrideError('showHelp')

    def moveSpace(self, x, y, delta):
        self._printOverrideError('moveSpace')

    def notifyCursorOver3dScene(self, isOver3dScene):
        self._printOverrideError('notifyCursorOver3dScene')

    def notifyCursorDragging(self, isDragging):
        self._printOverrideError('notifyCursorDragging')

    def as_updateVehicleStatusS(self, data):
        return self.flashObject.as_updateVehicleStatus(data) if self._isDAAPIInited() else None

    def as_onVehicleSelectionConfirmedS(self):
        return self.flashObject.as_onVehicleSelectionConfirmed() if self._isDAAPIInited() else None

    def as_onBattleStartedS(self):
        return self.flashObject.as_onBattleStarted() if self._isDAAPIInited() else None

    def as_onPrebattleInputStateLockedS(self, isStateLocked):
        return self.flashObject.as_onPrebattleInputStateLocked(isStateLocked) if self._isDAAPIInited() else None
