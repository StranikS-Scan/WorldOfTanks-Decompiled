# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/multi_turret_hint_panel.py
import BigWorld
import CommandMapping
from items.components import component_constants
from gui.Scaleform.daapi.view.meta.MultiTurretHintPanelMeta import MultiTurretHintPanelMeta
from gui.shared.utils.key_mapping import getReadableKey
from gui.Scaleform.locale.INGAME_HELP import INGAME_HELP
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency, i18n
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG_DEV
_BLANK_STRING = ' '

class MultiTurretHintPanel(MultiTurretHintPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        self._isVehicleMultiTurret()

    def _isVehicleMultiTurret(self):
        player = BigWorld.player()
        myID = None
        if player is not None:
            myID = player.playerVehicleID
        if myID is not None:
            for vInfo in self.sessionProvider.getArenaDP().getVehiclesInfoIterator():
                vTypeInfoVO = vInfo.vehicleType
                if vInfo.vehicleID == myID and vTypeInfoVO.isMultiTurret:
                    self._submitHintMessage()
                    return

        self.as_hidePanelS()
        return

    def _submitHintMessage(self):
        secondaryKeyOverrideName = getReadableKey(CommandMapping.CMD_SHOOT_SECONDARY)
        if secondaryKeyOverrideName:
            secondaryFireMsg = i18n.makeString(INGAME_HELP.HALLOWEEN_TURRET_HINT_FIRINGSECONDTURRET)
        else:
            secondaryFireMsg = i18n.makeString(INGAME_HELP.HALLOWEEN_TURRET_HINT_NOBINDINGFIRINGSECONDTURRET)
        doubleKeyOverrideName = getReadableKey(CommandMapping.CMD_CM_SHOOT)
        if doubleKeyOverrideName:
            doubleFireMsg = i18n.makeString(INGAME_HELP.HALLOWEEN_TURRET_HINT_DOUBLECLICKFIRING)
        else:
            doubleFireMsg = i18n.makeString(INGAME_HELP.HALLOWEEN_TURRET_HINT_NOBINDINGDOUBLECLICKFIRING)
        vo = {'secondaryFire': secondaryFireMsg,
         'secondaryKeyOverride': secondaryKeyOverrideName,
         'doubleFire': doubleFireMsg,
         'doubleKeyOverride': doubleKeyOverrideName}
        self.as_submitMessagesS(vo)
