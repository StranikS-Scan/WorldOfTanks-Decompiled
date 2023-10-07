# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/halloween_constants.py
import constants
import UnitBase
from constants_utils import ConstInjector, AbstractBattleMode
from halloween_common.battle_results import halloween
from constants_utils import addInvitationTypeFromArenaBonusTypeMapping

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    HALLOWEEN_BATTLES = 200


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    HALLOWEEN_BATTLES = 200
    HALLOWEEN_BATTLES_WHEEL = 201


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    HALLOWEEN_BATTLES = 200
    HALLOWEEN_BATTLES_WHEEL = 201


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    HALLOWEEN_BATTLES = 200


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    HALLOWEEN_BATTLES = 8388608


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    HALLOWEEN_BATTLES = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.HALLOWEEN_BATTLES


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    HALLOWEEN_BATTLES = PREBATTLE_TYPE.HALLOWEEN_BATTLES


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    START_UNIT_HALLOWEEN_BATTLES = 200


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    HALLOWEEN_BATTLES = 200


HALLOWEEN_GAME_PARAMS_KEY = 'halloween_config'
HALLOWEEN_EVENT_PREFIX = 'hw23'
PHASE_TO_DAILY_QUEST = HALLOWEEN_EVENT_PREFIX + '_phase_{}:rquest_1'
PHASE_TO_DAILY_TOKEN = HALLOWEEN_EVENT_PREFIX + '_phase{}:daily_bonus'

class HalloweenBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.HALLOWEEN_BATTLES
    _QUEUE_TYPE = QUEUE_TYPE.HALLOWEEN_BATTLES
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.HALLOWEEN_BATTLES
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.HALLOWEEN_BATTLES
    _INVITATION_TYPE = INVITATION_TYPE.HALLOWEEN_BATTLES
    _NEW_VEHICLES_TAGS = 'event_battles'
    _BATTLE_MGR_NAME = 'HalloweenMgr'
    _UNIT_MGR_NAME = 'HWUnitMgr'
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.HALLOWEEN_BATTLES
    _ROSTER_TYPE = ROSTER_TYPE.HALLOWEEN_BATTLES
    _GAME_PARAMS_KEY = HALLOWEEN_GAME_PARAMS_KEY
    _SEASON_TYPE_BY_NAME = 'halloween'
    _SEASON_TYPE = GameSeasonType.HALLOWEEN_BATTLES
    _SEASON_MANAGER_TYPE = (GameSeasonType.HALLOWEEN_BATTLES, HALLOWEEN_GAME_PARAMS_KEY)
    _BATTLE_RESULTS_CONFIG = halloween

    @property
    def _ROSTER_CLASS(self):
        from unit_roster_config import HalloweenRoster
        return HalloweenRoster

    @property
    def _battleMgrConfig(self):
        return (self._BATTLE_MGR_NAME,
         0.2,
         4,
         ('periphery', 'standalone'))

    def registerBattleResultsConfig(self, *args, **kwargs):
        multipleKeys = (ARENA_BONUS_TYPE.HALLOWEEN_BATTLES, ARENA_BONUS_TYPE.HALLOWEEN_BATTLES_WHEEL)
        super(HalloweenBattleMode, self).registerBattleResultsConfig(multipleKeys)

    def registerSquadTypes(self):
        super(HalloweenBattleMode, self).registerSquadTypes()
        addInvitationTypeFromArenaBonusTypeMapping(ARENA_BONUS_TYPE.HALLOWEEN_BATTLES_WHEEL, self._INVITATION_TYPE, self._personality)
