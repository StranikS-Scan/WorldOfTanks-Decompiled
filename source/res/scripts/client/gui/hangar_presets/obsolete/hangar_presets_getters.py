# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/obsolete/hangar_presets_getters.py
import typing
from gui.hangar_presets.obsolete.hangar_gui_helpers import ifComponentInPreset
from gui.Scaleform.daapi.view.lobby.hangar.controls_helpers import DefaultHangarControlsHelper, RandomHangarControlsHelper
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import DefaultQuestFlagsGetter, RankedQuestFlagsGetter, MapboxQuestFlagsGetter
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS
from helpers import dependency
from skeletons.gui.game_control import IMapboxController, IRankedBattlesController
if typing.TYPE_CHECKING:
    from gui.hangar_presets.obsolete.hangar_gui_config import HangarGuiPreset
    from gui.periodic_battles.models import AlertData
    from gui.Scaleform.daapi.view.lobby.hangar.controls_helpers import IHangarControlsHelper
    from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import IQuestFlagsGetter

class IPresetsGetter(object):

    def getAmmoInjectViewAlias(self):
        raise NotImplementedError

    def getAmmoSetupViewAlias(self):
        raise NotImplementedError

    def getCarouselSettings(self):
        raise NotImplementedError

    def getHangarAlertBlock(self):
        raise NotImplementedError

    def getHangarHeaderBlock(self):
        raise NotImplementedError

    def getHangarWidgetAlias(self):
        raise NotImplementedError

    def getHangarControlsHelper(self):
        raise NotImplementedError

    def getPreset(self):
        raise NotImplementedError


class EmptyPresetsGetter(IPresetsGetter):
    _DEFAULT_AMMO_INJECT_VIEW_ALIAS = None
    _DEFAULT_AMMO_SETUP_VIEW_ALIAS = None

    @classmethod
    def getDefaultAmmoInjectViewAlias(cls):
        return cls._DEFAULT_AMMO_INJECT_VIEW_ALIAS

    @classmethod
    def getDefaultAmmoSetupViewAlias(cls):
        return cls._DEFAULT_AMMO_SETUP_VIEW_ALIAS

    @classmethod
    def getDefaultCarouselSettings(cls):
        return (None, None)

    @classmethod
    def getDefaultHangarAlertBlock(cls):
        return (False, None, None)

    @classmethod
    def getDefaultHangarControlsHelper(cls):
        return None

    @classmethod
    def getDefaultHangarHeaderBlock(cls):
        return (False, None)

    @classmethod
    def getDefaultHangarWidgetAlias(cls):
        return None

    @classmethod
    def getDefaultPreset(cls):
        return None

    def getAmmoInjectViewAlias(self):
        return self.getDefaultAmmoInjectViewAlias()

    def getAmmoSetupViewAlias(self):
        return self.getDefaultAmmoSetupViewAlias()

    def getCarouselSettings(self):
        return self.getDefaultCarouselSettings()

    def getHangarAlertBlock(self):
        return self.getDefaultHangarAlertBlock()

    def getHangarControlsHelper(self):
        return self.getDefaultHangarControlsHelper()

    def getHangarHeaderBlock(self):
        return self.getDefaultHangarHeaderBlock()

    def getHangarWidgetAlias(self):
        return self.getDefaultHangarWidgetAlias()

    def getPreset(self):
        return self.getDefaultPreset()


class BasePresetsGetter(EmptyPresetsGetter):
    _QUEST_FLAGS_GETTER = None
    _HANGAR_CONTROLS_HELPER = None

    def __init__(self, preset):
        self._preset = preset

    @ifComponentInPreset(HANGAR_CONSTS.AMMUNITION_INJECT, abortAction='getDefaultAmmoInjectViewAlias')
    def getAmmoInjectViewAlias(self, preset=None):
        return preset.visibleComponents[HANGAR_CONSTS.AMMUNITION_INJECT].type

    @ifComponentInPreset(HANGAR_CONSTS.CAROUSEL, abortAction='getDefaultCarouselSettings')
    def getCarouselSettings(self, preset=None):
        component = preset.visibleComponents[HANGAR_CONSTS.CAROUSEL]
        return (component.type, component.layout)

    @ifComponentInPreset(HANGAR_CONSTS.HEADER, abortAction='getDefaultHangarHeaderBlock')
    def getHangarHeaderBlock(self, preset=None):
        isHangarHeaderVisible = HANGAR_CONSTS.HEADER in preset.visibleComponents
        isFlagsVisible = HANGAR_CONSTS.HEADER_QUEST_FLAGS in preset.visibleComponents
        flagsGetter = self._getQuestFlagsGetter() if isFlagsVisible else None
        return (isHangarHeaderVisible, flagsGetter)

    @ifComponentInPreset(HANGAR_CONSTS.HEADER_WIDGET, abortAction='getDefaultHangarWidgetAlias')
    def getHangarWidgetAlias(self, preset=None):
        return preset.visibleComponents[HANGAR_CONSTS.HEADER_WIDGET].type

    def getHangarControlsHelper(self):
        return self._HANGAR_CONTROLS_HELPER

    def getPreset(self):
        return self._preset

    def _getQuestFlagsGetter(self):
        return self._QUEST_FLAGS_GETTER


class DefaultPresetsGetter(BasePresetsGetter):
    _QUEST_FLAGS_GETTER = DefaultQuestFlagsGetter
    _HANGAR_CONTROLS_HELPER = DefaultHangarControlsHelper


class RandomPresetsGetter(DefaultPresetsGetter):
    _HANGAR_CONTROLS_HELPER = RandomHangarControlsHelper


class RankedPresetsGetter(DefaultPresetsGetter):
    _QUEST_FLAGS_GETTER = RankedQuestFlagsGetter
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def getHangarAlertBlock(self):
        return self.__rankedController.getAlertBlock()


class MapboxPresetsGetter(DefaultPresetsGetter):
    _QUEST_FLAGS_GETTER = MapboxQuestFlagsGetter
    __mapboxController = dependency.descriptor(IMapboxController)

    def getHangarAlertBlock(self):
        return self.__mapboxController.getAlertBlock()


class SpecBattlePresetsGetter(DefaultPresetsGetter):
    GUI_TYPE_TO_QUEST_FLAGS = {}

    def __init__(self, preset, guiType):
        super(SpecBattlePresetsGetter, self).__init__(preset)
        self._flagsGetter = self.GUI_TYPE_TO_QUEST_FLAGS.get(guiType, self._QUEST_FLAGS_GETTER)

    def _getQuestFlagsGetter(self):
        return self._flagsGetter
