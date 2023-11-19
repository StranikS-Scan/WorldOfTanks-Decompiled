# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_gui_controller.py
import typing
from constants import QUEUE_TYPE
from gui.prb_control.entities.listener import IPrbListener
from gui.hangar_presets.hangar_gui_config import getHangarGuiConfig
from gui.hangar_presets.hangar_gui_helpers import hasCurrentPreset
from gui.shared.system_factory import collectHangarPresetsReaders, collectHangarPresetsGetters
from skeletons.gui.game_control import IHangarGuiController
if typing.TYPE_CHECKING:
    from gui.hangar_presets.hangar_presets_getters import IPresetsGetter
    from gui.hangar_presets.hangar_gui_config import HangarGuiPreset
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar

class HangarGuiController(IHangarGuiController, IPrbListener):
    __slots__ = ('__presetsGetters', '__hangar', '__isChangeableComponentsVisible')

    def __init__(self):
        self.__hangar = None
        self.__presetsGetters = {}
        self.__isChangeableComponentsVisible = None
        return

    def init(self):
        readers = collectHangarPresetsReaders()
        config = getHangarGuiConfig(sorted(readers, key=lambda r: not r.isDefault()))
        self.__presetsGetters = collectHangarPresetsGetters(config)

    def fini(self):
        self.__isChangeableComponentsVisible = None
        self.__presetsGetters = {}
        self.__hangar = None
        super(HangarGuiController, self).fini()
        return

    @hasCurrentPreset(defReturn=False)
    def isComponentAvailable(self, preset, componentType):
        return componentType in preset.visibleComponents

    def getCurrentPreset(self):
        presetGetter = self.__getCurrentPresetGetter()
        return presetGetter.getPreset() if presetGetter is not None else None

    def getAmmoInjectViewAlias(self):
        presetGetter = self.__getCurrentPresetGetter()
        return presetGetter.getAmmoInjectViewAlias() if presetGetter is not None else None

    def getHangarCarouselSettings(self):
        presetGetter = self.__getCurrentPresetGetter()
        return presetGetter.getCarouselSettings() if presetGetter is not None else (None, None)

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

    def __getCurrentPresetGetter(self):
        prbEntity = self.prbEntity
        if prbEntity is None:
            return
        else:
            presetsGetter = self.__presetsGetters.get(self.prbEntity.getQueueType(), self.__presetsGetters[QUEUE_TYPE.RANDOMS])
            return presetsGetter.createByPrbEntity(prbEntity)
