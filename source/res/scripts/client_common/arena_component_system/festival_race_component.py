# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/festival_race_component.py
import AnimationSequence
import BigWorld
from helpers import isPlayerAvatar
import math_utils
import Math
import ResMgr
from PlayerEvents import g_playerEvents
from client_arena_component_system import ClientArenaComponent
from constants import RACE_CHECKPOINTS, ARENA_PERIOD
from helpers import dependency
from vehicle_systems.stricted_loading import makeCallbackWeak
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider

class FestivalRaceComponent(ClientArenaComponent):
    _MAX_EFFECT_TRIGGER_Z_POS = -260
    settingsCore = dependency.descriptor(ISettingsCore)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self._raceVisualController = FestivalRaceVFXController()

    def activate(self):
        super(FestivalRaceComponent, self).activate()
        g_playerEvents.onAvatarReady += self.__onAvatarReady

    def deactivate(self):
        player = BigWorld.player()
        if isPlayerAvatar() and player.onCheckpointEvent is not None:
            player.onCheckpointEvent -= self.__onCheckpoint
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self._raceVisualController.removeAll()
        super(FestivalRaceComponent, self).deactivate()
        return

    def __onAvatarReady(self):
        if isPlayerAvatar():
            BigWorld.player().onCheckpointEvent += self.__onCheckpoint
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def __onArenaPeriodChange(self, period, *args):
        if period == ARENA_PERIOD.BATTLE:
            self._raceVisualController.playRaceStartEffect()

    def __onCheckpoint(self, vehicleID, name):
        player = BigWorld.player()
        vId = player.vehicle.id if player.vehicle else 0
        if vehicleID != vId:
            return
        position = Math.Vector3(player.vehicle.position)
        if name == RACE_CHECKPOINTS.SHOW_FINISH and position.z > self._MAX_EFFECT_TRIGGER_Z_POS:
            self._raceVisualController.playFinishRaceEffect()

    def destroy(self):
        self._raceVisualController = None
        ClientArenaComponent.destroy(self)
        return


class FestivalRaceVFXController(object):
    _DYN_OBJECTS_CONFIG_PATH = 'scripts/dynamic_objects.xml'

    def __init__(self):
        self._animations = []
        self._effectsConfig = self._readConfig()

    def handleEvent(self):
        self.playFinishRaceEffect()

    def playRaceStartEffect(self):
        self._prepareSequence(**self._effectsConfig['start'])

    def playFinishRaceEffect(self):
        self._prepareSequence(**self._effectsConfig['finish']['right'])
        self._prepareSequence(**self._effectsConfig['finish']['left'])

    def removeAll(self):
        for animator in self._animations:
            if animator is not None:
                animator.stop()

        self._animations = []
        return

    def _prepareSequence(self, path, position, yaw=0.0):
        spaceID = BigWorld.player().spaceID
        loader = AnimationSequence.Loader(path, spaceID)
        BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self._onAnimationLoaded, path, position, yaw))

    def _onAnimationLoaded(self, path, position, yaw, animators):
        if path not in animators.failedIDs:
            rotation = (yaw, 0.0, 0.0)
            transform = math_utils.createRTMatrix(rotation, position)
            animator = animators[path]
            animator.bindToWorld(transform)
            animator.loopCount = 1
            animator.start()
            self._animations.append(animator)

    def _readConfig(self):
        section = ResMgr.openSection(self._DYN_OBJECTS_CONFIG_PATH)['FestivalRaceStartFinishEffect']
        return {'start': self._fillParams(section['start']),
         'finish': {'left': self._fillParams(section['finish']['left']),
                    'right': self._fillParams(section['finish']['right'])}}

    def _fillParams(self, section):
        params = {'path': section.readString('path'),
         'position': section.readVector3('position')}
        if section.has_key('yaw'):
            params['yaw'] = section.readFloat('yaw')
        return params
