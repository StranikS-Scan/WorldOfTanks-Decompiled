# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/battle_v2/settings.py
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from tutorial.gui.Scaleform.battle_v2.pop_ups import ReplenishAmmoDialog

class BATTLE_VIEW_ALIAS(object):
    REPLENISH_AMMO_DIALOG = 'replenishAmmoDialog'


BATTLE_VIEW_SETTINGS = (GroupedViewSettings(BATTLE_VIEW_ALIAS.REPLENISH_AMMO_DIALOG, ReplenishAmmoDialog, 'replenishAmmoDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),)
DIALOG_ALIAS_MAP = {'replenishAmmo': BATTLE_VIEW_ALIAS.REPLENISH_AMMO_DIALOG}
