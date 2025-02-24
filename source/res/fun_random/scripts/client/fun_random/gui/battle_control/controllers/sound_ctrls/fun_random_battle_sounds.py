# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_control/controllers/sound_ctrls/fun_random_battle_sounds.py
import typing
from functools import partial
import WWISE
import BattleReplay
import SoundGroups
from fun_random_common.fun_constants import UNKNOWN_WWISE_REMAPPING
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasBattleSubMode
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.sounds.epic_sound_constants import EPIC_SOUND
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayersBattleController, BaseEfficiencySoundPlayer
from shared_utils import nextTick
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers import BattleSessionSetup
    from gui.battle_control.controllers.sound_ctrls.common import SoundPlayer
    from skeletons.gui.battle_session import IClientArenaVisitor

class FunRandomBattleSoundController(SoundPlayersBattleController, FunSubModesWatcher):

    def __init__(self, setup):
        super(FunRandomBattleSoundController, self).__init__()
        self._remappingName = self._getRemappingName(setup.arenaVisitor)

    def startControl(self, *args):
        self._activateRemapping()
        super(FunRandomBattleSoundController, self).startControl()

    def stopControl(self):
        self._deactivateRemapping()
        super(FunRandomBattleSoundController, self).stopControl()

    def _initializeSoundPlayers(self):
        return (FunRandomStepRepairPointSoundPlayer(),)

    def _activateRemapping(self):
        if self._remappingName != UNKNOWN_WWISE_REMAPPING:
            WWISE.activateRemapping(self._remappingName)

    def _deactivateRemapping(self):
        if self._remappingName != UNKNOWN_WWISE_REMAPPING:
            nextTick(partial(WWISE.deactivateRemapping, self._remappingName))()

    @hasBattleSubMode(defReturn=UNKNOWN_WWISE_REMAPPING)
    def _getRemappingName(self, arenaVisitor=None):
        return self.getBattleSubMode(arenaVisitor).getSettings().client.wwiseRemapping


class FunRandomBattleReplaySoundController(FunRandomBattleSoundController):

    def startControl(self, *args):
        super(FunRandomBattleReplaySoundController, self).startControl(args)
        self.startSubSettingsListening(self.__onSubModesLoaded)

    def stopControl(self):
        self.stopSubSettingsListening(self.__onSubModesLoaded)
        super(FunRandomBattleReplaySoundController, self).stopControl()

    def _activateRemapping(self):
        if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            super(FunRandomBattleReplaySoundController, self)._activateRemapping()

    def _deactivateRemapping(self):
        if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            super(FunRandomBattleReplaySoundController, self)._deactivateRemapping()

    def __onSubModesLoaded(self, *_):
        self._remappingName = self._getRemappingName()
        self._activateRemapping()


def createFunRandomBattleSoundsController(setup):
    return FunRandomBattleReplaySoundController(setup) if BattleReplay.g_replayCtrl.isPlaying else FunRandomBattleSoundController(setup)


class FunRandomStepRepairPointSoundPlayer(BaseEfficiencySoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__isRepairing = False
        self.__curPointIdx = -1

    def destroy(self):
        super(FunRandomStepRepairPointSoundPlayer, self).destroy()
        self.__playResupplyStop()
        self.__curPointIdx = -1

    def _subscribe(self):
        super(FunRandomStepRepairPointSoundPlayer, self)._subscribe()
        ctrl = self.__sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onVehicleEntered += self.__onVehicleEntered
            ctrl.onCircleStatusChanged += self.__onCircleStatusChanged
            ctrl.onVehicleLeft += self.__onVehicleLeft
        return

    def _unsubscribe(self):
        super(FunRandomStepRepairPointSoundPlayer, self)._unsubscribe()
        ctrl = self.__sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onVehicleEntered -= self.__onVehicleEntered
            ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
            ctrl.onVehicleLeft -= self.__onVehicleLeft
        return

    def __onVehicleEntered(self, type_, pointIdx, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__curPointIdx = pointIdx
        if state == EPIC_CONSTS.RESUPPLY_READY:
            self.__playResupplyReady()

    def __onVehicleLeft(self, type_, _):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__playResupplyStop()
        self.__curPointIdx = -1

    def __onCircleStatusChanged(self, type_, pointIdx, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        if self.__curPointIdx != pointIdx:
            return
        if state == EPIC_CONSTS.RESUPPLY_FULL:
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_REPPAIR_POINT_COMPLETED)
        elif state == EPIC_CONSTS.RESUPPLY_READY:
            self.__playResupplyReady()
        elif state == EPIC_CONSTS.RESUPPLY_BLOCKED:
            self.__playResupplyStop()

    def __playResupplyReady(self):
        if not self.__isRepairing and self.__curPointIdx != -1:
            self.__isRepairing = True
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_REPPAIR_POINT_PROGRESS)

    def __playResupplyStop(self):
        if self.__isRepairing and self.__curPointIdx != -1:
            self.__isRepairing = False
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_REPPAIR_POINT_PROGRESS_STOP)
