# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/blur.py
from __future__ import absolute_import
from gui.shared.view_helpers.blur_manager import ImmediateSceneBlurConfig
from helpers import dependency
from skeletons.gui.game_control import IBlurController, IBlurEffect
from skeletons.gui.shared.utils import IHangarSpace

def createConfig(enabled=False, spaceID=0, settings=None, persistent=False):
    return (ImmediateSceneBlurConfig(spaceID=spaceID, settings=settings, enabled=enabled, persistent=persistent),)


class RandomHangarBlur(object):
    __blurCtrl = dependency.descriptor(IBlurController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, settings=None, enabled=True, persistent=True):
        self.__settings = settings if settings is not None else self.__blurCtrl.getSettingsByAlias('maximum')
        self.__blur = self.__blurCtrl.createBlur((ImmediateSceneBlurConfig(spaceID=self.__hangarSpace.spaceID, settings=self.__settings, enabled=enabled, persistent=persistent),))
        return

    def init(self):
        self.__hangarSpace.onSpaceChanged += self.__handleSpaceChange

    def destroy(self):
        self.__hangarSpace.onSpaceChanged -= self.__handleSpaceChange
        self.__blur.disable()
        self.__blur.fini()

    def enable(self):
        self.__blur.enable()

    def disable(self):
        self.__blur.disable()

    def __handleSpaceChange(self):
        enabled = False
        for config in self.__blur.config:
            if config.enabled:
                enabled = True
                break

        if enabled:
            self.disable()
        for config in self.__blur.config:
            config.spaceID = self.__hangarSpace.spaceID

        if enabled:
            self.enable()
