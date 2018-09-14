# Embedded file name: scripts/client/gui/battle_results/formatters.py
from helpers import i18n
_UNKNOWN_TEAMMATE_NAME = i18n.makeString('#battle_results:players/teammate/unknown')
_UNKNOWN_ENEMY_NAME = i18n.makeString('#battle_results:players/enemy/unknown')

def getUnknownPlayerName(isEnemy = False):
    if isEnemy:
        return _UNKNOWN_ENEMY_NAME
    else:
        return _UNKNOWN_TEAMMATE_NAME
