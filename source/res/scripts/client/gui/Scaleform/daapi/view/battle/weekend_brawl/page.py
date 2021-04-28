# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/page.py
import logging
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.game_control.wb_battle_sounds import WBBattleSoundController, EnemyPoiSound, AllyPoiSound, UsedAbilitySound
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage, COMMON_CLASSIC_CONFIG, EXTENDED_CLASSIC_CONFIG
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.weekend_brawl.markers2d import WeekendBrawlMarkersManager
from gui.Scaleform.daapi.view.battle.weekend_brawl.battle_messages import BattleMessagesPlayer
from shared_utils import CONST_CONTAINER
_logger = logging.getLogger(__name__)

class _DynamicAliases(CONST_CONTAINER):
    ENEMY_POI_SOUND = 'enemyPoiSound'
    ALLY_POI_SOUND = 'allyPoiSound'
    USED_ABILITY_SOUND = 'usedAbilitySound'
    BATTLE_MESSAGES_PLAYER = 'battleMessagesPlayer'


_WEEKEND_BRAWL_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.POINTS_OF_INTEREST_CTRL, (BATTLE_VIEW_ALIASES.INTEREST_POINT_NOTIFICATION_PANEL,
   BATTLE_VIEW_ALIASES.ABILITY_CHOICE_PANEL,
   _DynamicAliases.ENEMY_POI_SOUND,
   _DynamicAliases.ALLY_POI_SOUND,
   _DynamicAliases.USED_ABILITY_SOUND,
   _DynamicAliases.BATTLE_MESSAGES_PLAYER)),), viewsConfig=((_DynamicAliases.ENEMY_POI_SOUND, EnemyPoiSound),
 (_DynamicAliases.ALLY_POI_SOUND, AllyPoiSound),
 (_DynamicAliases.USED_ABILITY_SOUND, UsedAbilitySound),
 (_DynamicAliases.BATTLE_MESSAGES_PLAYER, BattleMessagesPlayer)))
_FULL_CONFIG = COMMON_CLASSIC_CONFIG + _WEEKEND_BRAWL_CONFIG
_EXTENDED_CONFIG = EXTENDED_CLASSIC_CONFIG + _WEEKEND_BRAWL_CONFIG
_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, WeekendBrawlMarkersManager)

class WeekendBrawlBattlePage(ClassicPage):

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS):
        if components is None:
            components = _FULL_CONFIG if self.sessionProvider.isReplayPlaying else _EXTENDED_CONFIG
        super(WeekendBrawlBattlePage, self).__init__(components=components, external=external)
        self.__wbSoundController = None
        return

    def _populate(self):
        super(WeekendBrawlBattlePage, self)._populate()
        _logger.debug('WeekendBrawl battle page is created.')
        self.__wbSoundController = WBBattleSoundController()
        self.__wbSoundController.init()

    def _dispose(self):
        _logger.debug('WeekendBrawl battle page is destroyed.')
        if self.__wbSoundController is not None:
            self.__wbSoundController.destroy()
            self.__wbSoundController = None
        super(WeekendBrawlBattlePage, self)._dispose()
        return
