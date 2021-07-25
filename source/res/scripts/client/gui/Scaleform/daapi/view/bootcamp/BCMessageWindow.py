# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCMessageWindow.py
from functools import partial
import BigWorld
from bootcamp.BootCampEvents import g_bootcampEvents
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.meta.BCMessageWindowMeta import BCMessageWindowMeta
from gui.server_events.pm_constants import SOUNDS
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.Scaleform.genConsts.BOOTCAMP_MESSAGE_ALIASES import BOOTCAMP_MESSAGE_ALIASES
import SoundGroups
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from bootcamp.subtitles.decorators import subtitleDecorator

class BCMessageWindow(BCMessageWindowMeta):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    BC_NEW_MODULE_UNLOCK_SOUND_ID = 'bc_new_module_unlock'
    BC_RESOURCE_FLY_SOUND_ID = 'bc_resources_fly'
    BC_RESOURCE_GLOW_SOUND_ID = 'bc_resources_glow'
    BC_INFO_LINE_DISAPPEAR_SOUND_ID = 'bc_info_line_disappear'
    FLY_ANIMATIONS = ['gold',
     'prem',
     'credits',
     'experience']
    RTPC_EXT_BC_ELEMENT_POSITION = 'RTPC_ext_bc_element_position'

    def __init__(self, content):
        super(BCMessageWindow, self).__init__(content)
        self.__blur = None
        return

    def needRTPCCorection(self, animation):
        return self.isFlyAnimation(animation)

    def isFlyAnimation(self, animation):
        return animation in self.FLY_ANIMATIONS

    def setParentWindow(self, window):
        super(BCMessageWindow, self).setParentWindow(window)
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer, blurAnimRepeatCount=1)

    def onMessageButtonClicked(self):
        self.onCustomButton(needStopEffect=True, needCloseWindow=False)

    def onTryClosing(self):
        return False

    @subtitleDecorator
    def onMessageAppear(self, type):
        pass

    def onMessageDisappear(self, type, animation):
        if type != BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO and not self.isFlyAnimation(animation):
            SoundGroups.g_instance.playSound2D(self.BC_INFO_LINE_DISAPPEAR_SOUND_ID)

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
        self.__blur.disable()

    def onMessageAnimationStopped(self, animation):
        if self.needRTPCCorection(animation):
            self.soundManager.setRTPC(self.RTPC_EXT_BC_ELEMENT_POSITION, SOUNDS.MIN_MISSIONS_ZOOM)

    def onMessageAnimationStarted(self, animation):
        if self.needRTPCCorection(animation):
            self.soundManager.playSound(self.BC_RESOURCE_FLY_SOUND_ID)
            self.soundManager.playSound(self.BC_RESOURCE_GLOW_SOUND_ID)
            self.soundManager.setRTPC(self.RTPC_EXT_BC_ELEMENT_POSITION, SOUNDS.MAX_MISSIONS_ZOOM)
        else:
            self.soundManager.playSound(self.BC_NEW_MODULE_UNLOCK_SOUND_ID)

    def _populate(self):
        super(BCMessageWindow, self)._populate()
        self.as_setMessageDataS(self._content['messages'])
        self.as_blurOtherWindowsS(WindowLayer.TOP_WINDOW)
        g_bootcampEvents.onRequestBootcampMessageWindowClose += self.onMessageRemoved
        if self._hangarSpace.spaceInited:
            self.__setCameraDisabled(True)
        else:
            self._hangarSpace.onSpaceCreate += self.__onSpaceCreated

    def _dispose(self):
        super(BCMessageWindow, self)._dispose()
        if self.__blur is not None:
            self.__blur.fini()
        g_bootcampEvents.onRequestBootcampMessageWindowClose -= self.onMessageRemoved
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.__setCameraDisabled(False)
        return

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
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': disabled,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, ctx={'disable': disabled}), EVENT_BUS_SCOPE.LOBBY)
