# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCMessageWindow.py
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.view.meta.BCMessageWindowMeta import BCMessageWindowMeta
from gui.Scaleform.genConsts.BOOTCAMP_MESSAGE_ALIASES import BOOTCAMP_MESSAGE_ALIASES
import SoundGroups

class BCMessageWindow(BCMessageWindowMeta):

    def onMessageButtonClicked(self):
        self.onCustomButton(needStopEffect=True, needCloseWindow=False)

    def onWindowClose(self):
        pass

    def onMessageAppear(self, type):
        if type == BOOTCAMP_MESSAGE_ALIASES.RENDERER_FIN_UI:
            SoundGroups.g_instance.playSound2D('bc_info_line_graduate')
        elif type != BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO:
            SoundGroups.g_instance.playSound2D('bc_info_line_universal')
        voiceover = self._content['voiceovers'].pop(0)
        if voiceover:
            SoundGroups.g_instance.playSound2D(voiceover)

    def onMessageDisappear(self, type):
        if type != BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO:
            SoundGroups.g_instance.playSound2D('bc_info_line_disappear')

    def onMessageRemoved(self):
        self.submit()

    def _populate(self):
        super(BCMessageWindow, self)._populate()
        self.as_setMessageDataS(self._content['messages'])
        g_bootcampEvents.onRequestBootcampMessageWindowClose += self.onMessageRemoved

    def _dispose(self):
        super(BCMessageWindow, self)._dispose()
        g_bootcampEvents.onRequestBootcampMessageWindowClose -= self.onMessageRemoved
