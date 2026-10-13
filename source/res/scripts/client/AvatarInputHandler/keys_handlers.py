# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/keys_handlers.py
from __future__ import absolute_import
from future.utils import lrange
import CommandMapping
from helpers.dependency import replace_none_kwargs
from skeletons.gui.battle_session import IBattleSessionProvider

@replace_none_kwargs(guiSessionProvider=IBattleSessionProvider)
def processAmmoSelection(key, guiSessionProvider=None):
    if CommandMapping.g_instance.isFiredList(lrange(CommandMapping.CMD_AMMO_CHOICE_1, CommandMapping.CMD_AMMO_CHOICE_4), key):
        ammoCtrl = guiSessionProvider.shared.ammo
        if ammoCtrl:
            ammoCtrl.handleAmmoChoice(key)
        return True
    else:
        return None
