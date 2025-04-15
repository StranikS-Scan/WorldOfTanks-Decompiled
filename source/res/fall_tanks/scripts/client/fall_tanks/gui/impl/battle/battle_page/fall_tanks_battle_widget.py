# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/impl/battle/battle_page/fall_tanks_battle_widget.py
import typing
from constants import ARENA_PERIOD
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_control.arena_info.interfaces import IArenaPeriodController
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from fall_tanks.gui.battle_control.mixins import FallTanksBattleMixin
from fall_tanks.gui.fall_tanks_gui_constants import BATTLE_CTRL_ID
from fall_tanks.gui.impl.gen.view_models.views.battle.battle_page.fall_tanks_battle_widget_model import FallTanksBattleWidgetModel, WidgetState
if typing.TYPE_CHECKING:
    from skeletons.gui.battle_session import IBattleContext, IClientArenaVisitor
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksVehicleInfo
_UNKNOWN_VEHICLE_ID = 0
_WIDGET_STATE_MAP = {(ARENA_PERIOD.BATTLE, False): WidgetState.INRACE,
 (ARENA_PERIOD.BATTLE, True): WidgetState.FINISHED,
 (ARENA_PERIOD.AFTERBATTLE, False): WidgetState.NOTFINISHED,
 (ARENA_PERIOD.AFTERBATTLE, True): WidgetState.FINISHED}

class FallTanksBattleWidgetView(ViewImpl, IArenaPeriodController, FallTanksBattleMixin):
    __slots__ = ('__arenaPeriod',)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.fall_tanks.battle.FallTanksBattleWidgetView(), flags=ViewFlags.VIEW, model=FallTanksBattleWidgetModel())
        super(FallTanksBattleWidgetView, self).__init__(settings)
        self.__arenaPeriod = ARENA_PERIOD.IDLE

    @property
    def viewModel(self):
        return super(FallTanksBattleWidgetView, self).getViewModel()

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def startControl(self, battleCtx, arenaVisitor):
        self.__arenaPeriod = self.__sessionProvider.shared.arenaPeriod.getPeriod()

    def stopControl(self):
        self.__arenaPeriod = ARENA_PERIOD.IDLE

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriod(period)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriod(period)

    def _onLoading(self, *args, **kwargs):
        super(FallTanksBattleWidgetView, self)._onLoading(*args, **kwargs)
        self.startFallTanksAttachedListening(self.__invalidateAll)
        self.__sessionProvider.addArenaCtrl(self)

    def _finalize(self):
        self.__sessionProvider.removeArenaCtrl(self)
        self.stopFallTanksAttachedListening(self.__invalidateAll)
        super(FallTanksBattleWidgetView, self)._finalize()

    def __updatePeriod(self, period):
        self.__arenaPeriod = period
        self.__invalidateAll()

    def __invalidateAll(self, attachedInfo=None):
        self.__updateModel(attachedInfo or self.getFallTanksAttachedVehicleInfo())

    @replaceNoneKwargsModel
    def __updateModel(self, attachedInfo, model=None):
        model.setState(_WIDGET_STATE_MAP.get((self.__arenaPeriod, attachedInfo.isFinished), WidgetState.DISABLED))
        model.setObservable(not attachedInfo.isPlayerVehicle)
        model.setCheckpoint(attachedInfo.checkpoint)
        model.setSpentTime(attachedInfo.finishTime)
        model.setPosition(attachedInfo.racePosition)
