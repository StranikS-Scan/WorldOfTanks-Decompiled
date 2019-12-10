# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/background_blur.py
import GUI
from gui.app_loader.decorators import sf_lobby, sf_battle

class BackgroundBlurSupport(object):

    def enable(self, ownLayer, layers, blurAnimRepeatCount=10):
        pass

    def disable(self):
        pass


class WGUIBackgroundBlurSupportImpl(BackgroundBlurSupport):
    __slots__ = ('__blur', '__blur3dScene')

    def __init__(self, blur3dScene=True):
        self.__blur = None
        self.__blur3dScene = blur3dScene
        return

    @sf_lobby
    def lobby(self):
        return None

    @sf_battle
    def battle(self):
        return None

    def enable(self, ownLayer, layers, blurAnimRepeatCount=10, fadeTime=0):
        if self.__blur3dScene:
            if self.__blur is None:
                self.__blur = GUI.WGUIBackgroundBlur()
                self.__blur.fadeTime = fadeTime
            self.__blur.enable = True
        if self.lobby is not None:
            self.lobby.blurBackgroundViews(ownLayer, layers, blurAnimRepeatCount)
        if self.battle is not None:
            self.battle.blurBackgroundViews()
        return

    def disable(self):
        if self.__blur3dScene:
            if self.__blur is not None:
                self.__blur.enable = False
                self.__blur = None
        if self.lobby:
            self.lobby.unblurBackgroundViews()
        if self.battle:
            self.battle.unblurBackgroundViews()
        return
