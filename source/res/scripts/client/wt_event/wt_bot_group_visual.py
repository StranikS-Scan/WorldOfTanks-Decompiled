# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/wt_event/wt_bot_group_visual.py
import logging
import BigWorld
import Svarog
import AnimationSequence
import WtEffects
from gui.battle_control import avatar_getter
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import WtGameEvent
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from wt_event.components import WtArenaComponent
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from math_utils import createTranslationMatrix, clamp
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)
_GROUP_DEATH_COOLDOWN = 10.0
_SEQUENCE_DURATION = 7.65

class WtBotGroupVisual(WtArenaComponent, CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self, componentSystem):
        super(WtBotGroupVisual, self).__init__(componentSystem)
        CallbackDelayer.__init__(self)
        self.__animators = {}
        self.__mappedEffects = set()

    def _initialize(self):
        super(WtBotGroupVisual, self)._initialize()
        g_eventBus.addListener(WtGameEvent.GROUPDRPOP_POSITIONS, self.__onUpdateDropPositions, scope=EVENT_BUS_SCOPE.BATTLE)
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onWavesIncoming += self.__onWavesIncoming
        self.__mappedEffects.clear()
        return

    def _finalize(self):
        super(WtBotGroupVisual, self)._finalize()
        g_eventBus.removeListener(WtGameEvent.GROUPDRPOP_POSITIONS, self.__onUpdateDropPositions, scope=EVENT_BUS_SCOPE.BATTLE)
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onWavesIncoming -= self.__onWavesIncoming
        self.clearCallbacks()
        self.__mappedEffects.clear()
        return

    def __onWavesIncoming(self, wavesPositions):
        for waveInfo in wavesPositions:
            if waveInfo.id not in self.__mappedEffects and not waveInfo.isUpcoming:
                self.__addEffect(waveInfo)

    def __onUpdateDropPositions(self, event):
        if event.ctx['addPositions']:
            arenaInfo = BigWorld.player().arena.arenaInfo
            if arenaInfo is not None:
                for waveInfo in arenaInfo.wavesPositions:
                    if waveInfo.id not in self.__mappedEffects:
                        if waveInfo.isUpcoming:
                            coolDown = self.__getGroupDeathCooldown()
                            delay = clamp(0, coolDown, coolDown - _SEQUENCE_DURATION)
                            self.delayCallback(delay, self.__addEffect, waveInfo)
                        else:
                            self.__addEffect(waveInfo)

        return

    def __addEffect(self, waveInfo):
        if waveInfo.id in self.__mappedEffects:
            return
        else:
            _logger.info('Bot group appear animation started %s', waveInfo)
            self.__mappedEffects.add(waveInfo.id)
            spaceID = BigWorld.player().spaceID
            arenaGuiType = self.__sessionProvider.arenaVisitor.getArenaGuiType()
            effectDescr = self.__dynObjectsCache.getConfig(arenaGuiType).botGroupAppearEffect
            vehicleDescr = avatar_getter.getVehicleTypeDescriptor()
            if vehicleDescr is not None and waveInfo.id > 2:
                if VEHICLE_EVENT_TYPE.EVENT_BOSS in vehicleDescr.type.tags:
                    avatar_getter.getSoundNotifications().play('ev_wt_w_vo_spawn_allies')
                elif VEHICLE_EVENT_TYPE.EVENT_HUNTER in vehicleDescr.type.tags:
                    avatar_getter.getSoundNotifications().play('ev_wt_krieger_vo_spawn_allies')
            BigWorld.loadResourceListBG((AnimationSequence.Loader(effectDescr.path, spaceID),), makeCallbackWeak(self.__onResourcesLoaded, waveInfo, effectDescr.path))
            return

    def __onResourcesLoaded(self, waveInfo, resourceName, resourceRefs):
        if resourceName in resourceRefs.failedIDs:
            _logger.warning('Resource loading is failed %s', resourceName)
        spaceID = BigWorld.player().spaceID
        animator = resourceRefs[resourceName]
        matrix = createTranslationMatrix(waveInfo.position)
        animator.bindToWorld(matrix)
        animator.loopCount = 1
        handler = Svarog.GameObject(spaceID)
        handler.createComponent(WtEffects.SequenceTimer, animator, lambda : Svarog.removeGameObject(spaceID, handler))
        Svarog.addGameObject(spaceID, handler)
        handler.activate()

    def __getGroupDeathCooldown(self):
        arenaInfo = BigWorld.player().arena.arenaInfo
        return arenaInfo.getWtConfig()['groupDeathCooldown'] if arenaInfo is not None else _GROUP_DEATH_COOLDOWN
