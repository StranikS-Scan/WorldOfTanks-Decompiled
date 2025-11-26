# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/obsolete/hangar_gui_sf_controller.py
import typing
from gui.hangar_presets.obsolete.hangar_gui_helpers import hasCurrentPreset
from skeletons.gui.game_control import IHangarGuiController
if typing.TYPE_CHECKING:
    from gui.hangar_presets.obsolete.hangar_gui_config import HangarGuiPreset
    from gui.hangar_presets.obsolete.hangar_presets_getters import IPresetsGetter
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar

class HangarGuiScaleformController(IHangarGuiController.IHangarGuiScaleformController):

    def __init__(self, providersHolder):
        self.__providersHolder = providersHolder
        self.__isChangeableComponentsVisible = None
        self.__hangar = None
        return

    def fini(self):
        self.__hangar = None
        self.__isChangeableComponentsVisible = None
        self.__providersHolder = None
        return

    @property
    def currentPresetGetter(self):
        return self.__providersHolder.getCurrentGuiProvider().getPresetsGetter()

    @hasCurrentPreset(defReturn=False)
    def isComponentAvailable(self, preset, componentType):
        return componentType in preset.visibleComponents

    def getCurrentPreset(self):
        return self.currentPresetGetter.getPreset()

    def holdHangar(self, hangar):
        self.__hangar = hangar
        self.__isChangeableComponentsVisible = None
        return

    def releaseHangar(self):
        self.__hangar = None
        self.__isChangeableComponentsVisible = None
        return

    @hasCurrentPreset()
    def updateComponentsVisibility(self, preset=None):
        if self.__hangar is not None:
            visibleComponents = set(preset.visibleComponents.keys()) - set(self.__getChangeableComponents())
            self.__hangar.as_updateHangarComponentsS(list(visibleComponents), preset.hiddenComponents.keys())
        return

    def updateChangeableComponents(self, isVisible, force=False):
        if force:
            self.__isChangeableComponentsVisible = None
        if isVisible == self.__isChangeableComponentsVisible or self.__hangar is None:
            return
        else:
            components = self.__getChangeableComponents()
            isChangeableComponentsVisible = len(components) > 0 and isVisible
            if isChangeableComponentsVisible:
                shownComponents, hiddenComponents = components, []
            else:
                shownComponents, hiddenComponents = [], components
            self.__hangar.as_setControlsVisibleS(isChangeableComponentsVisible)
            self.__hangar.as_updateHangarComponentsS(shownComponents, hiddenComponents)
            self.__isChangeableComponentsVisible = isChangeableComponentsVisible
            return

    @hasCurrentPreset(defReturn=())
    def __getChangeableComponents(self, preset=None):
        return [ k for k, v in preset.visibleComponents.items() if v.isChangeable ]
