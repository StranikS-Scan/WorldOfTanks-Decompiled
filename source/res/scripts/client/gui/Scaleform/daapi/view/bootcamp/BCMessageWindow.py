# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCMessageWindow.py
from functools import partial
import BigWorld
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.view.meta.BCMessageWindowMeta import BCMessageWindowMeta
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.Scaleform.genConsts.BOOTCAMP_MESSAGE_ALIASES import BOOTCAMP_MESSAGE_ALIASES
import SoundGroups
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.shared import EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from bootcamp.subtitles.decorators import subtitleDecorator

class BCMessageWindow(BCMessageWindowMeta):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, content):
        super(BCMessageWindow, self).__init__(content)
        self.__blur = WGUIBackgroundBlurSupportImpl()
        self.__blurHidden = False

    def onMessageButtonClicked(self):
        self.onCustomButton(needStopEffect=True, needCloseWindow=False)

    def onTryClosing(self):
        return False

    @subtitleDecorator
    def onMessageAppear(self, type):
        if type == BOOTCAMP_MESSAGE_ALIASES.RENDERER_FIN_UI:
            SoundGroups.g_instance.playSound2D('bc_info_line_graduate')
        elif type != BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO:
            SoundGroups.g_instance.playSound2D('bc_info_line_universal')

    def onMessageDisappear(self, type):
        if type != BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO:
            SoundGroups.g_instance.playSound2D('bc_info_line_disappear')

    def onMessageRemoved(self):
        callback = self._content.get('callback')
        if callback is not None:
            callback(False)
        self.submit()
        return

    def onMessageExecuted(self, renderedType):
        callback = self._content.get('callback')
        if callback is not None:
            callback(True)
        return

    def hideBlur(self):
        if not self.__blurHidden:
            self.__blur.disable()
            self.__blurHidden = True

    def _populate(self):
        super(BCMessageWindow, self)._populate()
        self.as_setMessageDataS(self._content['messages'])
        self.__blur.enable(APP_CONTAINERS_NAMES.VIEWS, (APP_CONTAINERS_NAMES.TOP_SUB_VIEW, APP_CONTAINERS_NAMES.SUBVIEW, APP_CONTAINERS_NAMES.WINDOWS), blurAnimRepeatCount=1)
        self.as_blurOtherWindowsS(APP_CONTAINERS_NAMES.DIALOGS)
        g_bootcampEvents.onRequestBootcampMessageWindowClose += self.onMessageRemoved
        if self._hangarSpace.spaceInited:
            self.__setCameraDisabled(True)
        else:
            self._hangarSpace.onSpaceCreate += self.__onSpaceCreated

    def _dispose(self):
        super(BCMessageWindow, self)._dispose()
        self.hideBlur()
        g_bootcampEvents.onRequestBootcampMessageWindowClose -= self.onMessageRemoved
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.__setCameraDisabled(False)

    def _stop(self, needCloseWindow=True):
        self._content.clear()
        for _, effect in self._gui.effects.iterEffects():
            if effect.isStillRunning(self.uniqueName):
                effect.stop()

        if needCloseWindow:
            self.destroy()

    def __onSpaceCreated(self):
        BigWorld.callback(0.1, partial(self.__setCameraDisabled, True))

    def __setCameraDisabled(self, disabled):
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': disabled}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, ctx={'disable': disabled}), EVENT_BUS_SCOPE.LOBBY)
