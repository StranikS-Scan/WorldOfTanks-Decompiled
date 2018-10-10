# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/atlases.py
from .atlas_entries.battle_atlas import BattleAtlas
from .atlas_entries.common_battle_lobby import CommonBattleLobby
from .atlas_entries.components import Components
from .atlas_entries.damage_indicator import DamageIndicator
from .atlas_entries.quests_progress import QuestsProgress
from .atlas_entries.store import Store
from .atlas_entries.vehicle_marker_atlas import VehicleMarkerAtlas

class Atlases(object):
    __slots__ = ()
    battleAtlas = BattleAtlas()
    commonBattleLobby = CommonBattleLobby()
    components = Components()
    damageIndicator = DamageIndicator()
    questsProgress = QuestsProgress()
    store = Store()
    vehicleMarkerAtlas = VehicleMarkerAtlas()
