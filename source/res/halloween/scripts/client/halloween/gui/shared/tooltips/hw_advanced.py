# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/shared/tooltips/hw_advanced.py
from gui.shared.tooltips.advanced import MODULE_MOVIES, BaseAdvancedTooltip
from gui.Scaleform.daapi.settings.config import ADVANCED_COMPLEX_TOOLTIPS

def registerHWEquipmentTooltipMovies():
    MODULE_MOVIES.update({'hw22_shield': 'hw22_shield',
     'hw22_hpRepair': 'hw22_resuply',
     'hw22_nitro': 'hw22_nitro',
     'hw22_instantReload': 'hw22_machineGun',
     'hw22_superShellFireball': 'hw22_fireshot',
     'hw22_damageVehicleModules': 'hw22_modulesBraker',
     'hw22_enlargeMaxHealth': 'hw22_improvedHarding',
     'hw22_ramBoost': 'hw22_ramming',
     'hw22_bullseye': 'hw22_smoothRide'})
    ADVANCED_COMPLEX_TOOLTIPS.update({'#halloween.tooltips.extend:hangar/ammo_panel/hw_equipment/empty': 'hw22_setup'})
    BaseAdvancedTooltip._MOVIE_TEXT_RIGHT_PADDING.update({'hw22_setup': -70})
