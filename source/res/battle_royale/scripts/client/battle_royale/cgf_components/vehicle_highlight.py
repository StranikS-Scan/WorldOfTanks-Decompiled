# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/cgf_components/vehicle_highlight.py
import BigWorld
import CGF
import GenericComponents
from aih_constants import CTRL_MODES, CTRL_MODE_NAME
from constants import IS_CLIENT
if IS_CLIENT:
    from Avatar import PlayerAvatar
else:

    class PlayerAvatar(object):
        pass


class VehicleHighlightSystem(CGF.System):
    AvatarActivated = CGF.ActivateReaction(CGF.ReactRo(PlayerAvatar), CGF.Ro(GenericComponents.ControlModeStatus))
    AvatarDeactivated = CGF.DeactivateReaction(CGF.ReactRo(PlayerAvatar), CGF.Ro(GenericComponents.ControlModeStatus))
    Reactions = CGF.Reactions(AvatarActivated, AvatarDeactivated)

    def update(self):
        for _, controlModeStatus in self.reaction(self.AvatarDeactivated):
            self.onRemoved(controlModeStatus)

        for _, controlModeStatus in self.reaction(self.AvatarActivated):
            self.onAdded(controlModeStatus)

    def onAdded(self, controlModeStatus):
        if controlModeStatus.mode == CTRL_MODES.index(CTRL_MODE_NAME.VIDEO):
            BigWorld.wg_setHideEdges(True)

    def onRemoved(self, controlModeStatus):
        if controlModeStatus.mode == CTRL_MODES.index(CTRL_MODE_NAME.VIDEO):
            BigWorld.wg_setHideEdges(False)
