# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_gui_controller.py
import typing
from itertools import chain
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from gui.prb_control.entities.listener import IPrbListener
from gui.hangar_presets.hangar_gui_config import getHangarGuiConfig
from gui.hangar_presets.hangar_gui_helpers import hasCurrentPreset
from gui.hangar_presets.hangar_presets_getters import EmptyPresetsGetter
from gui.shared.system_factory import collectHangarPresetsReaders, collectHangarPresetsGetters
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from battle_modifiers_common import BattleModifiers
    from gui.hangar_presets.hangar_presets_getters import IPresetsGetter
    from gui.hangar_presets.hangar_gui_config import HangarGuiPreset
    from gui.periodic_battles.models import AlertData
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
    from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import IQuestFlagsGetter
    from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import ILobbyHeaderControlsHelper

class HangarGuiController(IHangarGuiController, IPrbListener):
    __slots__ = ('__hangar', '__presetsGetters', '__bonusPresetGetters', '__isChangeableComponentsVisible')
    _EMPTY_PRESETS_GETTER = EmptyPresetsGetter()
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__hangar = None
        self.__presetsGetters = {}
        self.__bonusPresetGetters = {}
        self.__isChangeableComponentsVisible = None
        return

    def init(self):
        readers = collectHangarPresetsReaders()
        config = getHangarGuiConfig(sorted(readers, key=lambda r: not r.isDefault()))
        self.__presetsGetters = collectHangarPresetsGetters(config)
        self.__bonusPresetGetters = {bonusType:bonusPresetGetter for bonusType, bonusPresetGetter in chain(*(p.createAllBonusTypes().iteritems() for p in self.__presetsGetters.itervalues()))}

    def fini(self):
        self.__isChangeableComponentsVisible = None
        self.__bonusPresetGetters = {}
        self.__presetsGetters = {}
        self.__hangar = None
        super(HangarGuiController, self).fini()
        return

    @hasCurrentPreset(defReturn=False)
    def isComponentAvailable(self, preset, componentType):
        return componentType in preset.visibleComponents

    def getCurrentPreset(self):
        return self.__getCurrentPresetGetter(defaultQueueType=QUEUE_TYPE.RANDOMS).getPreset()

    def getAmmoInjectViewAlias(self):
        return self.__getCurrentPresetGetter(defaultQueueType=QUEUE_TYPE.RANDOMS).getAmmoInjectViewAlias()

    def getHangarAlertBlock(self):
        return self.__getCurrentPresetGetter(defaultQueueType=QUEUE_TYPE.RANDOMS).getHangarAlertBlock()

    def getHangarCarouselSettings(self):
        return self.__getCurrentPresetGetter(defaultQueueType=QUEUE_TYPE.RANDOMS).getCarouselSettings()

    def getHangarHeaderBlock(self):
        return self.__getCurrentPresetGetter(defaultQueueType=QUEUE_TYPE.RANDOMS).getHangarHeaderBlock()

    def getHangarWidgetAlias(self):
        return self.__getCurrentPresetGetter(defaultQueueType=QUEUE_TYPE.RANDOMS).getHangarWidgetAlias()

    def getLobbyHeaderHelper(self):
        return self.__getCurrentPresetGetter(defaultQueueType=QUEUE_TYPE.RANDOMS).getLobbyHeaderHelper()

    def getBattleModifiers(self):
        return self.__getCurrentPresetGetter().getBattleModifiers()

    def checkBonusCaps(self, bonusType, bonusCaps):
        presetsGetter = self.__bonusPresetGetters.get(bonusType, self._EMPTY_PRESETS_GETTER)
        return self.__checkBonusCaps(bonusType, bonusCaps, presetsGetter)

    def checkCurrentBonusCaps(self, bonusCaps, default=False):
        presetsGetter = self.__getCurrentPresetGetter()
        bType = presetsGetter.getSuggestedBonusType()
        return self.__checkBonusCaps(bType, bonusCaps, presetsGetter) if bType != ARENA_BONUS_TYPE.UNKNOWN else default

    def checkCrystalRewards(self, bonusType):
        presetsGetter = self.__bonusPresetGetters.get(bonusType, self._EMPTY_PRESETS_GETTER)
        return self.__checkCrystalRewards(bonusType, presetsGetter)

    def checkCurrentCrystalRewards(self, default=False):
        presetGetter = self.__getCurrentPresetGetter()
        bType = presetGetter.getSuggestedBonusType()
        return self.__checkCrystalRewards(bType, presetGetter) if bType != ARENA_BONUS_TYPE.UNKNOWN else default

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

    def __getCurrentPresetGetter(self, defaultQueueType=QUEUE_TYPE.UNKNOWN):
        prbEntity = self.prbEntity
        if prbEntity is None:
            return self._EMPTY_PRESETS_GETTER
        else:
            defaultPresetsGetter = self.__presetsGetters.get(defaultQueueType, self._EMPTY_PRESETS_GETTER)
            presetsGetter = self.__presetsGetters.get(prbEntity.getQueueType(), defaultPresetsGetter)
            return presetsGetter.createByPrbEntity(prbEntity)

    def __checkBonusCaps(self, bonusType, bonusCaps, presetsGetter):
        return BONUS_CAPS.checkAny(bonusType, bonusCaps, specificOverrides=presetsGetter.getBonusCapsOverrides())

    def __checkCrystalRewards(self, bonusType, presetsGetter):
        crystalConfig = self.__lobbyContext.getServerSettings().getCrystalRewardConfig()
        return crystalConfig.isCrystalEarnPossible(bonusType, battleModifiers=presetsGetter.getBattleModifiers())
