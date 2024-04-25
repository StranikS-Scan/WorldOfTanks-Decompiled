# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/common/respawn_ability.py
import logging
from constants import ARENA_BONUS_TYPE
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_tooltips import EquipmentPanelCmpTooltips
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
_logger = logging.getLogger(__name__)

class RespawnAbility(object):
    __brController = dependency.descriptor(IBattleRoyaleController)
    name = R.strings.artefacts.br_respawn.name()
    description = R.strings.artefacts.br_respawn.solo.descr()
    icon = R.images.gui.maps.icons.battleRoyale.artefact.respawn()
    tooltipType = EquipmentPanelCmpTooltips.TOOLTIP_RESPAWN
    soloTooltip = R.strings.artefacts.br_respawn.solo
    platoonTooltip = R.strings.artefacts.br_respawn.platoon
    soloRespawnPeriod = property(lambda self: int(self.getParams(ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, 'respawnPeriod')))
    soloTimeToRessurect = property(lambda self: self.getParams(ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, 'timeToRessurect'))
    platoonRespawnPeriod = property(lambda self: int(self.getParams(ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD, 'respawnPeriod')))
    platoonTimeToRessurect = property(lambda self: self.getParams(ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD, 'timeToRessurect'))

    @classmethod
    def getParams(cls, battleType, key):
        config = cls.__brController.getModeSettings().respawns.get(battleType)
        if config:
            return config[key]
        config = cls.__brController.getModeSettings().respawns.get(str(battleType))
        if config:
            return config[key]
        _logger.warning('RespawnAbility have no config or no key %s in config', key)
