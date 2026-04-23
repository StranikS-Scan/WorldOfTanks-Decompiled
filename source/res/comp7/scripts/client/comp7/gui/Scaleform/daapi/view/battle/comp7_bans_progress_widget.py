# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/comp7_bans_progress_widget.py
import logging
from comp7_core.gui.comp7_core_constants import BATTLE_CTRL_ID
from comp7.gui.impl.battle.vehicle_ban.ban_progression import BanProgressionView
from constants import ARENA_PERIOD
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class Comp7BansProgressWidget(InjectComponentAdaptor):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onPopulate(self):
        vehicleBanCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.COMP7_VEHICLE_BAN_CTRL)
        if vehicleBanCtrl is None or not vehicleBanCtrl.isVehicleBanEnabled:
            return
        elif self.__sessionProvider.arenaVisitor.getArenaPeriod() == ARENA_PERIOD.BATTLE:
            return
        else:
            self._createInjectView()
            return

    def _makeInjectView(self):
        return BanProgressionView()
