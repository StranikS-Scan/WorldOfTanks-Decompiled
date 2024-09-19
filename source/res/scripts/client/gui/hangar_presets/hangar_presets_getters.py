# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_presets_getters.py
import typing
from collections import namedtuple
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from battle_modifiers_common import BattleModifiers, BattleParams, getGlobalModifiers
from constants import QUEUE_TYPE, ARENA_GUI_TYPE, ARENA_BONUS_TYPE, IS_DEVELOPMENT
from gui.hangar_presets.hangar_gui_helpers import ifComponentInPreset
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import DefaultQuestFlagsGetter, RankedQuestFlagsGetter, MapboxQuestFlagsGetter, Comp7QuestFlagsGetter, Comp7TournamentQuestFlagsGetter
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper, EventLobbyHeaderHelper, RankedLobbyHeaderHelper, MapboxLobbyHeaderHelper, MapsTrainingLobbyHeaderHelper, Comp7LobbyHeaderHelper
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller, IRankedBattlesController, IMapboxController
if typing.TYPE_CHECKING:
    from gui.hangar_presets.hangar_gui_config import HangarGuiPreset
    from gui.periodic_battles.models import AlertData
    from gui.prb_control.entities.base.entity import BasePrbEntity
    from gui.prb_control.entities.base.legacy.entity import BaseLegacyEntity
    from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import IQuestFlagsGetter
    from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import ILobbyHeaderControlsHelper

class IPresetsGetter(object):
    __slots__ = ()

    def createAllBonusTypes(self):
        raise NotImplementedError

    def createByPrbEntity(self, prbEntity):
        raise NotImplementedError

    def getAmmoInjectViewAlias(self):
        raise NotImplementedError

    def getBattleModifiers(self):
        raise NotImplementedError

    def getBonusCapsOverrides(self):
        raise NotImplementedError

    def getCarouselSettings(self):
        raise NotImplementedError

    def getHangarAlertBlock(self):
        raise NotImplementedError

    def getHangarHeaderBlock(self):
        raise NotImplementedError

    def getHangarWidgetAlias(self):
        raise NotImplementedError

    def getLobbyHeaderHelper(self):
        raise NotImplementedError

    def getSuggestedBonusType(self):
        raise NotImplementedError

    def getPreset(self):
        raise NotImplementedError


class EmptyPresetsGetter(IPresetsGetter):
    __slots__ = ()
    _DEFAULT_AMMO_INJECT_VIEW_ALIAS = None
    _DEFAULT_BATTLE_MODIFIERS = BattleModifiers()

    @classmethod
    def getDefaultAmmoInjectViewAlias(cls):
        return cls._DEFAULT_AMMO_INJECT_VIEW_ALIAS

    @classmethod
    def getDefaultBattleModifiers(cls):
        return getGlobalModifiers() if IS_DEVELOPMENT else cls._DEFAULT_BATTLE_MODIFIERS

    @classmethod
    def getDefaultBonusCapsOverrides(cls):
        return BONUS_CAPS.OVERRIDE_BONUS_CAPS or {}

    @classmethod
    def getDefaultCarouselSettings(cls):
        return (None, None)

    @classmethod
    def getDefaultHangarAlertBlock(cls):
        return (False, None, None)

    @classmethod
    def getDefaultHangarHeaderBlock(cls):
        return (False, None)

    @classmethod
    def getDefaultHangarWidgetAlias(cls):
        return None

    @classmethod
    def getDefaultLobbyHeaderHelper(cls):
        return None

    @classmethod
    def getDefaultSuggestedBonusType(cls):
        return ARENA_BONUS_TYPE.UNKNOWN

    @classmethod
    def getDefaultPreset(cls):
        return None

    def createAllBonusTypes(self):
        return {}

    def createByPrbEntity(self, prbEntity):
        return self

    def getAmmoInjectViewAlias(self):
        return self.getDefaultAmmoInjectViewAlias()

    def getBattleModifiers(self):
        return self.getDefaultBattleModifiers()

    def getBonusCapsOverrides(self):
        return self.getDefaultBonusCapsOverrides()

    def getCarouselSettings(self):
        return self.getDefaultCarouselSettings()

    def getHangarAlertBlock(self):
        return self.getDefaultHangarAlertBlock()

    def getHangarHeaderBlock(self):
        return self.getDefaultHangarHeaderBlock()

    def getHangarWidgetAlias(self):
        return self.getDefaultHangarWidgetAlias()

    def getLobbyHeaderHelper(self):
        return self.getDefaultLobbyHeaderHelper()

    def getSuggestedBonusType(self):
        return self.getDefaultSuggestedBonusType()

    def getPreset(self):
        return self.getDefaultPreset()


class BasePresetsGetter(EmptyPresetsGetter):
    __slots__ = ('_config',)
    _QUEUE_TYPE = None
    _BONUS_TYPES = (ARENA_BONUS_TYPE.UNKNOWN,)
    _QUEST_FLAGS_GETTER = None
    _LOBBY_HEADER_HELPER = None

    def __init__(self, config):
        self._config = config

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

    def getBonusCapsOverrides(self):
        return self.getBattleModifiers()(BattleParams.BONUS_CAPS_OVERRIDES, self.getDefaultBonusCapsOverrides())

    def getLobbyHeaderHelper(self):
        return self._LOBBY_HEADER_HELPER

    def getSuggestedBonusType(self):
        return self._BONUS_TYPES[0]

    def createAllBonusTypes(self):
        return {bonusType:self for bonusType in self._BONUS_TYPES if bonusType != ARENA_BONUS_TYPE.UNKNOWN}

    def _getQuestFlagsGetter(self):
        return self._QUEST_FLAGS_GETTER


class DefaultPresetsGetter(BasePresetsGetter):
    __slots__ = ('_presetName',)
    _QUEUE_TYPE = QUEUE_TYPE.RANDOMS
    _BONUS_TYPES = (ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.EPIC_RANDOM, ARENA_BONUS_TYPE.EPIC_RANDOM_TRAINING)
    _QUEST_FLAGS_GETTER = DefaultQuestFlagsGetter
    _LOBBY_HEADER_HELPER = DefaultLobbyHeaderHelper

    def __init__(self, config):
        super(DefaultPresetsGetter, self).__init__(config)
        self._presetName = config.modes.get(self._QUEUE_TYPE)

    def getPreset(self):
        return self._config.presets.get(self._presetName)


class EventPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.EVENT_BATTLES
    _BONUS_TYPES = (ARENA_BONUS_TYPE.EVENT_BATTLES, ARENA_BONUS_TYPE.EVENT_BATTLES_2)
    _LOBBY_HEADER_HELPER = EventLobbyHeaderHelper

    def getLobbyHeaderHelper(self):
        return self._LOBBY_HEADER_HELPER(self.getSuggestedBonusType(), self.getBonusCapsOverrides())


class RankedPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.RANKED
    _BONUS_TYPES = (ARENA_BONUS_TYPE.RANKED,)
    _QUEST_FLAGS_GETTER = RankedQuestFlagsGetter
    _LOBBY_HEADER_HELPER = RankedLobbyHeaderHelper
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def getHangarAlertBlock(self):
        return self.__rankedController.getAlertBlock()


class MapboxPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.MAPBOX
    _BONUS_TYPES = (ARENA_BONUS_TYPE.MAPBOX,)
    _QUEST_FLAGS_GETTER = MapboxQuestFlagsGetter
    _LOBBY_HEADER_HELPER = MapboxLobbyHeaderHelper
    __mapboxController = dependency.descriptor(IMapboxController)

    def getHangarAlertBlock(self):
        return self.__mapboxController.getAlertBlock()


class MapsTrainingPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.MAPS_TRAINING
    _BONUS_TYPES = (ARENA_BONUS_TYPE.MAPS_TRAINING,)
    _LOBBY_HEADER_HELPER = MapsTrainingLobbyHeaderHelper


class Comp7PresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.COMP7
    _BONUS_TYPES = (ARENA_BONUS_TYPE.COMP7,)
    _QUEST_FLAGS_GETTER = Comp7QuestFlagsGetter
    _LOBBY_HEADER_HELPER = Comp7LobbyHeaderHelper
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @classmethod
    def getBattleModifiers(cls):
        return BattleModifiers(cls.__comp7Controller.battleModifiers)

    def getHangarAlertBlock(self):
        return self.__comp7Controller.getAlertBlock()


class WinbackPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.WINBACK
    _BONUS_TYPES = (ARENA_BONUS_TYPE.WINBACK,)


class RandomNP2PresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.RANDOM_NP2
    _BONUS_TYPES = (ARENA_BONUS_TYPE.RANDOM_NP2,)


class SpecBattlePresetsGetter(DefaultPresetsGetter):
    __slots__ = ('_guiType',)
    _QUEUE_TYPE = QUEUE_TYPE.SPEC_BATTLE
    _SpecGuiSettings = namedtuple('_SpecGuiSettings', ['bonusType',
     'modifiersGetter',
     'flagsGetter',
     'lobbyHelper'])
    _DEFAULT_GUI_SETTINGS = _SpecGuiSettings(ARENA_BONUS_TYPE.UNKNOWN, EmptyPresetsGetter.getDefaultBattleModifiers, DefaultQuestFlagsGetter, DefaultLobbyHeaderHelper)
    _GUI_TYPE_TO_SETTINGS = {ARENA_GUI_TYPE.TOURNAMENT_COMP7: _SpecGuiSettings(ARENA_BONUS_TYPE.TOURNAMENT_COMP7, Comp7PresetsGetter.getBattleModifiers, Comp7TournamentQuestFlagsGetter, DefaultLobbyHeaderHelper)}

    def __init__(self, config, guiType=ARENA_GUI_TYPE.RANDOM):
        super(SpecBattlePresetsGetter, self).__init__(config)
        guiTypesPresets = config.modes.get(self._QUEUE_TYPE, {})
        self._presetName = guiTypesPresets.get(guiType)
        self._guiType = guiType

    def createAllBonusTypes(self):
        return {settings.bonusType:SpecBattlePresetsGetter(self._config, guiType) for guiType, settings in self._GUI_TYPE_TO_SETTINGS.iteritems()}

    def createByPrbEntity(self, prbEntity):
        return SpecBattlePresetsGetter(self._config, prbEntity.getSettings()['arenaGuiType'])

    def getBattleModifiers(self):
        return self._GUI_TYPE_TO_SETTINGS.get(self._guiType, self._DEFAULT_GUI_SETTINGS).modifiersGetter()

    def getLobbyHeaderHelper(self):
        return self._GUI_TYPE_TO_SETTINGS.get(self._guiType, self._DEFAULT_GUI_SETTINGS).lobbyHelper

    def getSuggestedBonusType(self):
        return self._GUI_TYPE_TO_SETTINGS.get(self._guiType, self._DEFAULT_GUI_SETTINGS).bonusType

    def _getQuestFlagsGetter(self):
        return self._GUI_TYPE_TO_SETTINGS.get(self._guiType, self._DEFAULT_GUI_SETTINGS).flagsGetter


class WtEventPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.EVENT_BATTLES
