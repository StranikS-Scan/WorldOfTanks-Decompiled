# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/bonus_type.py
from constants import ARENA_BONUS_TYPE

class ArenaBonusTypeLabel(object):
    LABELS = {ARENA_BONUS_TYPE.UNKNOWN: 'special',
     ARENA_BONUS_TYPE.REGULAR: 'random',
     ARENA_BONUS_TYPE.TRAINING: 'training',
     ARENA_BONUS_TYPE.BOOTCAMP: 'bootcamp',
     ARENA_BONUS_TYPE.RANKED: 'ranked',
     ARENA_BONUS_TYPE.EPIC_RANDOM: 'epicRandom',
     ARENA_BONUS_TYPE.EPIC_BATTLE: 'epicQueue',
     ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD: 'battleRoyaleQueue',
     ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: 'battleRoyaleQueue',
     ARENA_BONUS_TYPE.MAPBOX: 'mapbox',
     ARENA_BONUS_TYPE.MAPS_TRAINING: 'mapsTraining',
     ARENA_BONUS_TYPE.COMP7: 'comp7',
     ARENA_BONUS_TYPE.VERSUS_AI: 'versusAI'}
