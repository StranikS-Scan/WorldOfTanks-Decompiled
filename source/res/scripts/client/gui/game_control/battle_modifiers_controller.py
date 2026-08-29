# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_modifiers_controller.py
import logging
import pkgutil
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE, ARENA_GUI_TYPE
from ExtensionsManager import g_extensionsManager
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity, StrongholdBrowserEntity
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.game_control import IBattleModifiersController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
if 'battle_modifiers' in [ ext.name for ext in g_extensionsManager.activeExtensions ] and pkgutil.find_loader('battle_modifiers_ext'):
    from battle_modifiers_ext.battle_modifiers import BattleModifiers
    bmClazz = BattleModifiers
else:
    _logger.error('Missing battle_modifiers_ext')
    bmClazz = lambda *_, **__: None
GLOBAL_MAP = 'global_map'
QUEUE_SORTIE_PREFIX = 'sortie_'
QUEUE_SORTIE_10 = 'sortie_10'
QUEUE_SORTIE_8 = 'sortie_8'
QUEUE_SORTIE_6 = 'sortie_6'
QUEUE_FORT_BATTLE_10 = 'fortBattle_10'
ALL_STRONGHOLD_QUEUE = (QUEUE_SORTIE_10,
 QUEUE_SORTIE_8,
 QUEUE_SORTIE_6,
 QUEUE_FORT_BATTLE_10)
SORTIE_QUEUES = (QUEUE_SORTIE_10, QUEUE_SORTIE_8, QUEUE_SORTIE_6)

class BattleModifiersController(IBattleModifiersController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(BattleModifiersController, self).__init__()
        self.__bmFunctionMapper = {self.ModifiersDomains.COMP7: self._comp7BattleModifiers,
         self.ModifiersDomains.GLOBAL_MAP: self._globalMapBattleModifiers,
         self.ModifiersDomains.STRONGHOLD: self._strongholdBattleModifiers}

    def getCurrentDomain(self):
        if self.prbEntity is None:
            return
        elif bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.COMP7):
            return self.ModifiersDomains.COMP7
        elif isinstance(self.prbEntity, (StrongholdEntity, StrongholdBrowserEntity)):
            return self.ModifiersDomains.STRONGHOLD
        else:
            if self.prbEntity.getQueueType() == QUEUE_TYPE.SPEC_BATTLE:
                if self.prbEntity.getSettings()['arenaGuiType'] == ARENA_GUI_TYPE.TOURNAMENT_COMP7:
                    return self.ModifiersDomains.COMP7
                if self.prbEntity.getBonusType() == ARENA_BONUS_TYPE.GLOBAL_MAP:
                    return self.ModifiersDomains.GLOBAL_MAP
            return

    def isBattleModifiersAvailable(self):
        return bool(self.getCurrentDomain())

    def modifiersInStrongholdBrowser(self):
        return isinstance(self.prbEntity, StrongholdBrowserEntity) and self.getBattleModifiersQueues()

    def getBattleModifiersObject(self):
        modifiers = self.battleModifiers
        return bmClazz(modifiers) if modifiers is not None else None

    def _comp7BattleModifiers(self, battleModifiersConfig):
        return getattr(battleModifiersConfig, self.ModifiersDomains.COMP7)

    def _strongholdBattleModifiers(self, battleModifiersConfig):
        if not battleModifiersConfig.isEnabled:
            return ()
        elif isinstance(self.prbEntity, StrongholdBrowserEntity):
            return ()
        elif self.prbEntity.getHeaderType() is None:
            return ()
        else:
            return getattr(battleModifiersConfig, QUEUE_SORTIE_PREFIX + str(self.prbEntity.getMinLevel())) if self.prbEntity.isSortie() else getattr(battleModifiersConfig, QUEUE_FORT_BATTLE_10)

    def _globalMapBattleModifiers(self, battleModifiersConfig):
        return () if not battleModifiersConfig.isEnabled else getattr(battleModifiersConfig, GLOBAL_MAP)

    def getBattleModifiersQueues(self):
        battleModifiersConfig = self._getBMConfig()
        bmQueues = []
        for queue in SORTIE_QUEUES:
            if getattr(battleModifiersConfig, queue):
                level = queue.split('_')[-1]
                queueName = queue.split('_')[0]
                bmQueues.append((queueName, level))

        if getattr(battleModifiersConfig, QUEUE_FORT_BATTLE_10):
            queueName = QUEUE_FORT_BATTLE_10.split('_')[0]
            bmQueues.append((queueName, None))
        return bmQueues

    def _isBattleModifierAvailableInQueue(self):
        battleModifiersConfig = self._getBMConfig()
        if not battleModifiersConfig.isEnabled:
            return False
        if isinstance(self.prbEntity, StrongholdBrowserEntity):
            return any((bool(getattr(battleModifiersConfig, queue)) for queue in ALL_STRONGHOLD_QUEUE))
        domain = self.getCurrentDomain()
        if domain == self.ModifiersDomains.GLOBAL_MAP:
            return bool(self._globalMapBattleModifiers(battleModifiersConfig))
        return bool(self._strongholdBattleModifiers(battleModifiersConfig)) if domain == self.ModifiersDomains.STRONGHOLD else False

    @property
    def tooltipConstant(self):
        return TOOLTIPS_CONSTANTS.MODIFIED_CAROUSEL_VEHICLE if self.isBattleModifiersAvailable() else TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE

    @property
    def battleModifiers(self):
        domain = self.getCurrentDomain()
        bmGetter = self.__bmFunctionMapper.get(domain)
        if bmGetter is not None:
            battleModifiersConfig = self._getBMConfig()
            return bmGetter(battleModifiersConfig)
        else:
            return

    def _getBMConfig(self):
        serverSettings = self.__lobbyContext.getServerSettings()
        return serverSettings.battleModifiersConfig

    def onLobbyInited(self, event):
        self.startGlobalListening()

    def onDisconnected(self):
        self.stopGlobalListening()
