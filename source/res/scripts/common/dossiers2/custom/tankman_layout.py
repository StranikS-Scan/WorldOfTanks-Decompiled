# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/tankman_layout.py
from dossiers2.common.DossierBlockBuilders import *
from dossiers2.custom.dependencies import MEDAL_ALIASES
_tmanTotalBlockLayout = ['battlesCount']
_tmanTotalBlockBuilder = StaticSizeBlockBuilder('total', _tmanTotalBlockLayout, {}, [])
TMAN_ACHIEVEMENTS_BLOCK_LAYOUT = ['warrior',
 'invader',
 'sniper',
 'defender',
 'steelwall',
 'supporter',
 'scout',
 'evileye',
 'medalUshakov',
 'medalOrlik',
 'medalOskin',
 'medalKrysov',
 'medalBurda',
 'medalBillotte',
 'medalKolobanov',
 'medalFadin',
 'medalRadleyWalters',
 'medalFokin',
 'medalLyubushkin',
 'medalSlyunyayev',
 'medalDumitru',
 'medalKhazov',
 'medalNikolas',
 'medalLafayettePool',
 'heroesOfRassenay',
 'medalDeLanglade',
 'medalTrubin',
 'huntsman',
 'sniper2',
 'mainGun',
 'medalFomin',
 'medalKrockenberger',
 'medalGavryushov']
_tankmanAchievementsBlockBuilder = StaticSizeBlockBuilder('achievements', TMAN_ACHIEVEMENTS_BLOCK_LAYOUT, {}, [], aliases=MEDAL_ALIASES)
tmanDossierLayout = (_tmanTotalBlockBuilder, _tankmanAchievementsBlockBuilder)
TANKMAN_DOSSIER_BLOCKS = {b.name:b for b in tmanDossierLayout}
