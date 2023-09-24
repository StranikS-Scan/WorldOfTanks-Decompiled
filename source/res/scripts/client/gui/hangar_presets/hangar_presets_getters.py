# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_presets_getters.py
import typing
from constants import QUEUE_TYPE, ARENA_GUI_TYPE
from gui.hangar_presets.hangar_gui_helpers import ifComponentInPreset
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS
if typing.TYPE_CHECKING:
    from gui.hangar_presets.hangar_gui_config import HangarGuiPreset
    from gui.prb_control.entities.base.entity import BasePrbEntity
    from gui.prb_control.entities.base.legacy.entity import BaseLegacyEntity

class IPresetsGetter(object):

    def createByPrbEntity(self, prbEntity):
        raise NotImplementedError

    def getPreset(self):
        raise NotImplementedError

    def getAmmoInjectViewAlias(self):
        raise NotImplementedError

    def getCarouselSettings(self):
        raise NotImplementedError


class BasePresetsGetter(IPresetsGetter):
    __slots__ = ('_config',)
    _QUEUE_TYPE = None

    def __init__(self, config):
        self._config = config

    def createByPrbEntity(self, prbEntity):
        return self

    @ifComponentInPreset(HANGAR_CONSTS.AMMUNITION_INJECT)
    def getAmmoInjectViewAlias(self, preset=None):
        return preset.visibleComponents[HANGAR_CONSTS.AMMUNITION_INJECT].type

    @ifComponentInPreset(HANGAR_CONSTS.CAROUSEL, defReturn=(None, None))
    def getCarouselSettings(self, preset=None):
        component = preset.visibleComponents[HANGAR_CONSTS.CAROUSEL]
        return (component.type, component.layout)


class DefaultPresetsGetter(BasePresetsGetter):
    __slots__ = ('_presetName',)
    _QUEUE_TYPE = QUEUE_TYPE.RANDOMS

    def __init__(self, config):
        super(DefaultPresetsGetter, self).__init__(config)
        self._presetName = config.modes.get(self._QUEUE_TYPE)

    def getPreset(self):
        return self._config.presets.get(self._presetName)


class SpecBattlePresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.SPEC_BATTLE

    def __init__(self, config, guiType=ARENA_GUI_TYPE.RANDOM):
        super(SpecBattlePresetsGetter, self).__init__(config)
        guiTypesPresets = config.modes.get(self._QUEUE_TYPE, {})
        self._presetName = guiTypesPresets.get(guiType)

    def createByPrbEntity(self, prbEntity):
        return SpecBattlePresetsGetter(self._config, prbEntity.getSettings()['arenaGuiType'])


class Comp7PresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.COMP7


class MapboxPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.MAPBOX
