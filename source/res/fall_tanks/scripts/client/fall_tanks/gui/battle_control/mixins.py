# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/mixins.py
import typing
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from fall_tanks.gui.fall_tanks_gui_constants import BATTLE_CTRL_ID
from fall_tanks.gui.battle_control.arena_info.arena_vos import FallTanksVehicleInfo
if typing.TYPE_CHECKING:
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksBattleController, IFallTanksVehicleInfo

class FallTanksBattleMixin(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def getFallTanksAttachedVehicleInfo(cls):
        ctrl = cls._getFallTanksBattleCtrl()
        return ctrl.getFallTanksAttachedVehicleInfo() if ctrl is not None else FallTanksVehicleInfo()

    @classmethod
    def getFallTanksPlayerVehicleInfo(cls):
        ctrl = cls._getFallTanksBattleCtrl()
        return ctrl.getFallTanksPlayerVehicleInfo() if ctrl is not None else FallTanksVehicleInfo()

    @classmethod
    def startFallTanksAttachedListening(cls, listener):
        ctrl = cls._getFallTanksBattleCtrl()
        if ctrl is not None:
            ctrl.onFallTanksAttachedInfoUpdate += listener
        return

    @classmethod
    def stopFallTanksAttachedListening(cls, listener):
        ctrl = cls._getFallTanksBattleCtrl()
        if ctrl is not None:
            ctrl.onFallTanksAttachedInfoUpdate -= listener
        return

    @classmethod
    def _getFallTanksBattleCtrl(cls):
        return cls.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FALL_TANKS_BATTLE_CTRL)


class PostmortemMixin(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def isInPostmortem(cls):
        ctrl = cls.__sessionProvider.shared.vehicleState
        return ctrl.isInPostmortem if ctrl is not None else False

    @classmethod
    def startPostmortemListening(cls, switchedListener, movingListener):
        ctrl = cls.__sessionProvider.shared.vehicleState
        if ctrl:
            ctrl.onPostMortemSwitched += switchedListener
            ctrl.onRespawnBaseMoving += movingListener

    @classmethod
    def stopPostmortemListening(cls, switchedListener, movingListener):
        ctrl = cls.__sessionProvider.shared.vehicleState
        if ctrl:
            ctrl.onPostMortemSwitched -= switchedListener
            ctrl.onRespawnBaseMoving -= movingListener
