# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rts_battles/rts_battle_prime_times.py
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.rts_battles.sound_manager import RTS_PRIME_TIME_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.EpicPrimeTimeMeta import EpicPrimeTimeMeta
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from skeletons.gui.game_control import IRTSBattlesController

class RtsServerPresenter(ServerListItemPresenter):
    _RES_ROOT = R.strings.rts_battles.primeTimes.serverTooltip
    _periodsController = dependency.descriptor(IRTSBattlesController)


class RtsBattlesPrimeTimeView(EpicPrimeTimeMeta):
    _COMMON_SOUND_SPACE = RTS_PRIME_TIME_SOUND_SPACE
    _RES_ROOT = R.strings.rts_battles.primeTimes
    _serverPresenterClass = RtsServerPresenter
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def _populate(self):
        super(RtsBattlesPrimeTimeView, self)._populate()
        self.as_setHeaderTextS(backport.text(R.strings.rts_battles.primeTimes.headerText()))
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.rtsBattles.bg.meta()))

    def _getController(self):
        return self.__rtsController

    def _getPrbActionName(self):
        return self._getPrbForcedActionName()

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.RTS_1x1 if self.__rtsController.isWarmup() else PREBATTLE_ACTION_NAME.RTS
