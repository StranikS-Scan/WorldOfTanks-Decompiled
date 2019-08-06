# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/animated_dialog_window.py
from frameworks.wulf import ViewFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.windows.animated_dialog_window_model import AnimatedDialogWindowModel
from gui.impl.pub.dialog_window import DialogWindow, DialogLayer
from gui.impl.pub.view_impl import ViewImpl

class AnimatedDialogWindow(DialogWindow):
    __slots__ = ('__parentDialogWindow', '__delayBtnItem', '__setAllWindowStack')

    def __init__(self, content=None, bottomContent=None, parent=None, parentDialogWindow=None, balanceContent=None, enableBlur=True, enableBlur3dScene=True, preset=DialogPresets.DEFAULT, layer=DialogLayer.TOP_WINDOW):
        decorator = ViewImpl(R.views.common.dialog_view.animated_dialog_window.AnimatedDialogWindow(), ViewFlags.WINDOW_DECORATOR, AnimatedDialogWindowModel)
        super(AnimatedDialogWindow, self).__init__(content=content, bottomContent=bottomContent, parent=parent, balanceContent=balanceContent, enableBlur=enableBlur, enableBlur3dScene=enableBlur3dScene, layer=layer, decorator=decorator)
        self.__parentDialogWindow = parentDialogWindow
        self.__delayBtnItem = None
        self.__setAllWindowStack = True
        self._setPreset(preset)
        return

    def setParentDialogState(self, state, forceSetAllChain):
        if self.__parentDialogWindow:
            self.__parentDialogWindow.viewModel.setCurrentState(state)
            if forceSetAllChain:
                self.__parentDialogWindow.setParentDialogState(state, forceSetAllChain)

    def processAnimatedAction(self, actionType, btnItem, setAllStack=True):
        self.__setAllWindowStack = setAllStack
        self.__delayBtnItem = btnItem
        if actionType == AnimatedDialogWindowModel.ACTION_CLOSE:
            self.viewModel.setForceCloseWindowWithAnim(True)
        elif actionType == AnimatedDialogWindowModel.ACTION_RETURN:
            self.viewModel.setForceReturnToPrevWithAnim(True)

    def _initialize(self):
        super(AnimatedDialogWindow, self)._initialize()
        self.viewModel.onCloseAnimationComplete += self._onCloseAnimationComplete
        self.viewModel.onReturnAnimationComplete += self._onReturnAnimationComplete
        self.viewModel.onCloseAnimationStart += self._onStartCloseAnimation
        self.viewModel.onReturnAnimationStart += self._onStartTransitionAnimation

    def _finalize(self):
        self.viewModel.onCloseAnimationComplete -= self._onCloseAnimationComplete
        self.viewModel.onReturnAnimationComplete -= self._onReturnAnimationComplete
        self.viewModel.onCloseAnimationStart -= self._onStartCloseAnimation
        self.viewModel.onReturnAnimationStart -= self._onStartTransitionAnimation
        super(AnimatedDialogWindow, self)._finalize()

    def _onReturnAnimationComplete(self):
        self.__processDelayedBtnClick()

    def _onCloseAnimationComplete(self):
        self.__processDelayedBtnClick()

    def _onStartCloseAnimation(self):
        self.setParentDialogState(AnimatedDialogWindowModel.STATE_HIDDEN, self.__setAllWindowStack)

    def _onStartTransitionAnimation(self):
        self.setParentDialogState(AnimatedDialogWindowModel.STATE_SHOWN, self.__setAllWindowStack)

    def __processDelayedBtnClick(self):
        if self.__delayBtnItem:
            super(AnimatedDialogWindow, self)._onButtonClick(self.__delayBtnItem)
            self.__delayBtnItem = None
        else:
            self._onClosed()
        return
