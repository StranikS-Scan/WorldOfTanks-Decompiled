# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/web_blocks.py
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT
from visual_script.dependency import dependencyImporter
events, dependency, guiShared, views, browserView, skeletons, WWISE = dependencyImporter('gui.shared.events', 'helpers.dependency', 'gui.shared', 'gui.Scaleform.daapi.settings.views', 'gui.Scaleform.daapi.view.lobby.hangar.BrowserView', 'skeletons.gui.game_control', 'WWISE')

class WebMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class OpenWebLinkFullScreen(Block, WebMeta):
    __HANGAR_SOUND_FILTERED_STATE_NAME = 'STATE_hangar_filtered'
    __HANGAR_SOUND_FILTERED_STATE_ON = 'STATE_hangar_filtered_on'
    __HANGAR_SOUND_FILTERED_STATE_OFF = 'STATE_hangar_filtered_off'
    __browserCtrl = dependency.descriptor(skeletons.IBrowserController)

    def __init__(self, *args, **kwargs):
        super(OpenWebLinkFullScreen, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._url = self._makeDataInputSlot('url', SLOT_TYPE.STR)
        self._filterSounds = self._makeDataInputSlot('filterSounds', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def filterSoundsOn(self, browserId):
        if browserId == views.VIEW_ALIAS.BROWSER_OVERLAY:
            if self._filterSounds.getValue():
                WWISE.WW_setState(self.__HANGAR_SOUND_FILTERED_STATE_NAME, self.__HANGAR_SOUND_FILTERED_STATE_ON)
            self.__browserCtrl.onBrowserAdded -= self.filterSoundsOn

    def filterSoundsOff(self, browserId):
        if browserId == views.VIEW_ALIAS.BROWSER_OVERLAY:
            if self._filterSounds.getValue():
                WWISE.WW_setState(self.__HANGAR_SOUND_FILTERED_STATE_NAME, self.__HANGAR_SOUND_FILTERED_STATE_OFF)
            self.__browserCtrl.onBrowserDeleted -= self.filterSoundsOff

    def onFinishScript(self):
        self.__browserCtrl.onBrowserAdded -= self.filterSoundsOn
        self.__browserCtrl.onBrowserDeleted -= self.filterSoundsOff

    def _exec(self):
        self.__browserCtrl.onBrowserAdded += self.filterSoundsOn
        self.__browserCtrl.onBrowserDeleted += self.filterSoundsOff
        guiShared.event_dispatcher.showBrowserOverlayView(self._url.getValue(), alias=views.VIEW_ALIAS.BROWSER_OVERLAY)
        self._out.call()
