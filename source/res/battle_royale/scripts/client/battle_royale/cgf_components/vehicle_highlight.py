# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/cgf_components/vehicle_highlight.py
import BigWorld
import CGF
import GenericComponents
from aih_constants import CTRL_MODES, CTRL_MODE_NAME
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from constants import IS_CLIENT
if IS_CLIENT:
    from Avatar import PlayerAvatar
else:

    class PlayerAvatar(object):
        pass


@bonusCapsManager(bonusCap=ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, domain=CGF.DomainOption.DomainClient)
class VehicleHighlightComponentManager(CGF.ComponentManager):

    @onAddedQuery(GenericComponents.ControlModeStatus, PlayerAvatar)
    def onAdded(self, controlModeStatus, *args):
        if controlModeStatus.mode == CTRL_MODES.index(CTRL_MODE_NAME.VIDEO):
            BigWorld.wg_setHideEdges(True)

    @onRemovedQuery(GenericComponents.ControlModeStatus, PlayerAvatar)
    def onRemoved(self, controlModeStatus, *args):
        if controlModeStatus.mode == CTRL_MODES.index(CTRL_MODE_NAME.VIDEO):
            BigWorld.wg_setHideEdges(False)
