# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/animated_dialog_window_model.py
from gui.impl.gen.view_models.windows.dialog_window_model import DialogWindowModel

class AnimatedDialogWindowModel(DialogWindowModel):
    __slots__ = ('onCloseAnimationStart', 'onCloseAnimationComplete', 'onReturnAnimationStart', 'onReturnAnimationComplete')
    STATE_SHOWN = 'showed'
    STATE_HIDDEN = 'hided'
    ACTION_CLOSE = 'close'
    ACTION_RETURN = 'return'

    def getCurrentState(self):
        return self._getString(13)

    def setCurrentState(self, value):
        self._setString(13, value)

    def getForceCloseWindowWithAnim(self):
        return self._getBool(14)

    def setForceCloseWindowWithAnim(self, value):
        self._setBool(14, value)

    def getForceReturnToPrevWithAnim(self):
        return self._getBool(15)

    def setForceReturnToPrevWithAnim(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(AnimatedDialogWindowModel, self)._initialize()
        self._addStringProperty('currentState', 'showed')
        self._addBoolProperty('forceCloseWindowWithAnim', False)
        self._addBoolProperty('forceReturnToPrevWithAnim', False)
        self.onCloseAnimationStart = self._addCommand('onCloseAnimationStart')
        self.onCloseAnimationComplete = self._addCommand('onCloseAnimationComplete')
        self.onReturnAnimationStart = self._addCommand('onReturnAnimationStart')
        self.onReturnAnimationComplete = self._addCommand('onReturnAnimationComplete')
