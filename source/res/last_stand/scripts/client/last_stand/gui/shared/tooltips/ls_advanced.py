# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/tooltips/ls_advanced.py
from gui.shared.tooltips.advanced import MODULE_MOVIES
from gui.Scaleform.daapi.settings.config import ADVANCED_COMPLEX_TOOLTIPS
from last_stand.gui.impl.lobby.tank_setup.backports.tooltips import LS_CONSUMABLE_EMPTY_TOOLTIP

def registerLSEquipmentTooltipMovies():
    MODULE_MOVIES.update({'ls_selfRepairKit': 'last_stand|ls_selfRepairKit',
     'ls_teamRepairKit': 'last_stand|ls_teamRepairKit',
     'ls_damageShield': 'last_stand|ls_damageShield',
     'ls_fastReload': 'last_stand|ls_fastReload',
     'ls_invisibility': 'last_stand|ls_invisibility',
     'ls_aoeDamageInstantShot': 'last_stand|ls_aoeDamageInstantShot',
     'ls_aoeStunInstantShot': 'last_stand|ls_aoeStunInstantShot',
     'ls_aoeDrainEnemyHpInstantShot': 'last_stand|ls_aoeDrainEnemyHpInstantShot',
     'ls_doubleDamage': 'last_stand|ls_doubleDamage',
     'ls_nitro': 'last_stand|ls_nitro'})
    ADVANCED_COMPLEX_TOOLTIPS.update({LS_CONSUMABLE_EMPTY_TOOLTIP: 'last_stand|ls_equipment'})
