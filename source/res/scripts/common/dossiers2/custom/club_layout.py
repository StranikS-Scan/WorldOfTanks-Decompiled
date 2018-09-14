# Embedded file name: scripts/common/dossiers2/custom/club_layout.py
from dossiers2.common.DossierBlockBuilders import *
from battle_statistics_layouts import *
_rated7x7BlockBuilder = StaticSizeBlockBuilder('rated7x7', RATED_7X7_BLOCK_LAYOUT, {}, [])
_maxRated7x7BlockBuilder = StaticSizeBlockBuilder('maxRated7x7', MAX_AND_BEST_VEHICLE_BLOCK_LAYOUT, {}, [])
rated7x7DossierLayout = (_rated7x7BlockBuilder, _maxRated7x7BlockBuilder)
_clubTotalBlockLayout = ['creationTime', 'lastBattleTime']
_clubTotalBlockBuilder = StaticSizeBlockBuilder('total', _clubTotalBlockLayout, {}, [])
_clubBattlesBlockLayout = ['battlesCount',
 'wins',
 'losses',
 'killedVehicles',
 'lostVehicles',
 'capturePoints',
 'droppedCapturePoints',
 'damageDealt',
 'damageReceived',
 'battlesCountInAttack',
 'damageDealtInAttack',
 'damageDealtInDefence']
_clubBattlesBlockBuilder = StaticSizeBlockBuilder('clubBattles', _clubBattlesBlockLayout, {}, [])
_clubBestVehiclesBlockBuilder = DictBlockBuilder('vehicles', 'I', 'II', {})
_clubBestMapsBlockBuilder = DictBlockBuilder('maps', 'I', 'II', {})
CLUB_ACHIEVEMENTS_BLOCK_LAYOUT = ['tacticalAdvantage']
_clubAchievementsBlockBuilder = StaticSizeBlockBuilder('achievementsRated7x7', CLUB_ACHIEVEMENTS_BLOCK_LAYOUT, {}, [])
clubDossierLayout = (_clubTotalBlockBuilder,
 _clubBattlesBlockBuilder,
 _clubBestVehiclesBlockBuilder,
 _clubBestMapsBlockBuilder,
 _clubAchievementsBlockBuilder)
