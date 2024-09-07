# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/quests_packer.py
import logging
from winback.gui.impl.lobby.views.winback_bonus_packer import getWinbackBonusPacker
import constants
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
_logger = logging.getLogger(__name__)

def getEventUIDataPacker(event):
    if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS:
        return BattleQuestUIDataPacker(event, bonusPackerGetter=getWinbackBonusPacker)
    else:
        _logger.warning('Only LIKE_BATTLE_QUESTS allowed')
        return None
