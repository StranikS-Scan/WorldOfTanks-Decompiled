# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/collector_animator.py
from functools import partial
import BigWorld
import Event
import SoundGroups
from effect_controller import EffectController
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from Math import Vector3, Matrix
from helpers.CallbackDelayer import CallbackDelayer
_ENERGY_RING_Y_OFFSET_STEP = 0.42
_MAX_ENERGY_RINGS = 13

class CollectorSoundsContainer(GameEventGetterMixin):
    _COLLECTOR_LOOP_SOUND_OBJ_NAME = 'ev_hw19_collector_loop'
    _COLLECTOR_LOOP_SOUND = 'ev_halloween_2019_gameplay_collector_loop'
    _COLLECTOR_LOOP_CAPACITY_RTPC = 'RTPC_ext_hw19_collector_capacity'
    _COLLECTOR_ACTIVE_SOUND_OBJ_NAME = 'ev_hw19_collector_collecting'
    _COLLECTING_START_SOUND = 'ev_halloween_2019_gameplay_volot_get_start_idle'
    _COLLECTING_STOP_SOUND = 'ev_halloween_2019_gameplay_volot_get_stop'
    _COLLECTOR_RING_SOUND = 'ev_halloween_2019_gameplay_collector_switch'

    def __init__(self):
        GameEventGetterMixin.__init__(self)
        self._collectorMatrix = Matrix()
        self._eventSource = None
        self._collectingSoundObject = None
        self._collectorSoundObject = None
        return

    def init(self, eventSource, collectorPosition):
        self._collectorMatrix.translation = collectorPosition
        self._eventSource = eventSource
        self._eventSource.onStartSoulCollecting += self._startCollectingSoundObject
        self._eventSource.onStopSoulCollecting += self._stopCollectingSoundObject
        self._eventSource.onCollectorAppear += self._startCollectorAmbientSound
        self._eventSource.onCollectorDisappear += self._stopCollectorAmbientSound
        self._eventSource.onSoulsAndRingUpdate += self._soulsAndRingUpdate
        self._eventSource.onSoulsUpdate += self._soulsUpdate

    def fini(self):
        self._eventSource.onStartSoulCollecting -= self._startCollectingSoundObject
        self._eventSource.onStopSoulCollecting -= self._stopCollectingSoundObject
        self._eventSource.onCollectorAppear -= self._startCollectorAmbientSound
        self._eventSource.onCollectorDisappear -= self._stopCollectorAmbientSound
        self._eventSource.onSoulsAndRingUpdate -= self._soulsAndRingUpdate
        self._eventSource.onSoulsUpdate -= self._soulsUpdate
        self._eventSource = None
        self._stopCollectingSoundObject()
        self._stopCollectorAmbientSound()
        return

    def _startCollectingSoundObject(self):
        if self._collectingSoundObject is None:
            self._collectingSoundObject = SoundGroups.g_instance.WWgetSoundObject(self._COLLECTOR_ACTIVE_SOUND_OBJ_NAME, self._collectorMatrix)
            self._collectingSoundObject.play(self._COLLECTING_START_SOUND)
        return

    def _stopCollectingSoundObject(self):
        if self._collectingSoundObject is not None:
            self._collectingSoundObject.play(self._COLLECTING_STOP_SOUND)
            self._collectingSoundObject = None
        return

    def _startCollectorAmbientSound(self):
        if self._collectorSoundObject is None:
            self._collectorSoundObject = SoundGroups.g_instance.WWgetSoundObject(self._COLLECTOR_LOOP_SOUND_OBJ_NAME, self._collectorMatrix)
            self._collectorSoundObject.play(self._COLLECTOR_LOOP_SOUND)
        return

    def _stopCollectorAmbientSound(self):
        if self._collectorSoundObject is not None:
            self._collectorSoundObject.stopAll()
            self._collectorSoundObject = None
        return

    def _soulsUpdate(self, currentSouls, maxSouls):
        if not currentSouls or not maxSouls:
            return
        else:
            fillPercentage = min(100, max(1, 100 * currentSouls // maxSouls))
            if self._collectorSoundObject is not None:
                self._collectorSoundObject.setRTPC(self._COLLECTOR_LOOP_CAPACITY_RTPC, fillPercentage)
            return

    def _soulsAndRingUpdate(self, ringLevel, currentSouls, maxSouls):
        if not currentSouls or not maxSouls:
            return
        else:
            if self._collectorSoundObject is not None:
                self._collectorSoundObject.play(self._COLLECTOR_RING_SOUND)
            return


class CollectorAnimator(GameEventGetterMixin, CallbackDelayer):

    def __init__(self, collector):
        GameEventGetterMixin.__init__(self)
        CallbackDelayer.__init__(self)
        self.__collector = collector
        self.__effectControllers = []
        self.__fakeModel = self.__createFakeModel()
        self.__energyRingEffects = []
        self.__ringFakeModels = []
        self.__currentFillLevel = 0
        self.__currentFillDivisor = 0
        self.__soulCollectorData = None
        self.__started = False
        self.__collecting = False
        self.__collectingAnimator = None
        self.__stopCollectingCallback = None
        self.onStartSoulCollecting = Event.Event()
        self.onStopSoulCollecting = Event.Event()
        self.onCollectorAppear = Event.Event()
        self.onCollectorDisappear = Event.Event()
        self.onSoulsUpdate = Event.Event()
        self.onSoulsAndRingUpdate = Event.Event()
        self.__collectorSoundsContainer = CollectorSoundsContainer()
        return

    def __createFakeModel(self):
        model = BigWorld.Model('')
        model.position = self.__collector.position
        BigWorld.player().addModel(model)
        return model

    def start(self):
        self.__collectorSoundsContainer.init(self, self.__collector.position)
        self.onCollectorAppear()
        self.soulCollector.onSoulsChanged += self.__onUpdate
        data = self.soulCollector.getSoulCollectorData()
        if isinstance(data, dict):
            collectorData = data.get(self.__collector.id, None)
            if collectorData:
                currentSouls, maxSouls = collectorData
                if maxSouls != 0:
                    self.__currentFillDivisor = maxSouls // _MAX_ENERGY_RINGS
                if currentSouls != 0:
                    self.__currentFillLevel = currentSouls // self.__currentFillDivisor
                    for i in xrange(1, self.__currentFillLevel + 1):
                        self.__energyRing(i)

                if maxSouls != 0 and currentSouls != 0 and currentSouls == maxSouls:
                    self.__aura()
        return

    def stop(self):
        self.soulCollector.onSoulsChanged -= self.__onUpdate
        self.onCollectorDisappear()
        self.__collectorSoundsContainer.fini()
        CallbackDelayer.destroy(self)
        for effectController in self.__effectControllers:
            effectController.reset()

        for effectController in self.__energyRingEffects:
            effectController.reset()

        if self.__collectingAnimator is not None:
            self.__collectingAnimator.reset()
        if self.__stopCollectingCallback is not None:
            BigWorld.cancelCallback(self.__stopCollectingCallback)
            self.__stopCollectingCallback = None
        for model in self.__ringFakeModels:
            if model.inWorld:
                BigWorld.player().delModel(model)

        if self.__fakeModel and self.__fakeModel.inWorld:
            BigWorld.player().delModel(self.__fakeModel)
        return

    def __onUpdate(self, diff):
        data = self.soulCollector.getSoulCollectorData()
        collectorData = data.get(self.__collector.id, None)
        if collectorData:
            currentSouls, maxSouls = collectorData
            if not self.__started and self.__currentFillLevel == 0 and currentSouls != 0 and maxSouls != 0:
                self.__initialStart()
            if currentSouls != 0 and maxSouls != 0:
                if not self.__collecting:
                    self.__startCollecting()
                elif self.__collecting and self.__stopCollectingCallback:
                    BigWorld.cancelCallback(self.__stopCollectingCallback)
                    self.__stopCollectingCallback = BigWorld.callback(1.1, self.__stopCollecting)
            if maxSouls != 0 and currentSouls >= maxSouls:
                currentSouls = maxSouls
                self.__aura()
            self.onSoulsUpdate(currentSouls, maxSouls)
            newCurrentLevel = 0
            if self.__currentFillDivisor == 0 and maxSouls != 0:
                self.__currentFillDivisor = maxSouls // _MAX_ENERGY_RINGS
                newCurrentLevel = currentSouls // self.__currentFillDivisor
            elif self.__currentFillDivisor:
                newCurrentLevel = currentSouls // self.__currentFillDivisor
            if newCurrentLevel > self.__currentFillLevel:
                self.onSoulsAndRingUpdate(newCurrentLevel, currentSouls, maxSouls)
                if newCurrentLevel > _MAX_ENERGY_RINGS:
                    newCurrentLevel = _MAX_ENERGY_RINGS
                for i in xrange(self.__currentFillLevel, newCurrentLevel + 1):
                    self.__energyRing(i)

                self.__currentFillLevel = newCurrentLevel + 1
        return

    def __startCollecting(self):
        self.__collecting = True
        startAnimation = EffectController('volot_collecting_start')
        self.__effectControllers.append(startAnimation)
        startAnimation.playSequence(self.__fakeModel)
        self.onStartSoulCollecting()
        self.delayCallback(1.45, self.__continueCollecting)

    def __continueCollecting(self):
        idleAnimation = EffectController('volot_collecting_idle')
        idleAnimation.playSequence(self.__fakeModel)
        self.__collectingAnimator = idleAnimation
        self.__stopCollectingCallback = BigWorld.callback(1.2, partial(self.__stopCollecting))

    def __stopCollecting(self):
        self.__collecting = False
        if self.__collectingAnimator:
            self.__stopCollectingCallback = None
            endAnimation = EffectController('volot_collecting_end')
            self.__collectingAnimator.stopSequnce()
            self.__collectingAnimator = None
            self.__effectControllers.append(endAnimation)
            endAnimation.playSequence(self.__fakeModel)
        self.onStopSoulCollecting()
        return

    def __aura(self):
        for effectController in self.__effectControllers:
            effectController.reset()

        startAnimation = EffectController('volot_aura_start')
        idleAnimation = EffectController('volot_aura_idle')
        fullStartAnimation = EffectController('volot_full_start')
        fullIdleAnimation = EffectController('volot_full_idle')
        self.__effectControllers.append(startAnimation)
        self.__effectControllers.append(idleAnimation)
        self.__effectControllers.append(fullStartAnimation)
        self.__effectControllers.append(fullIdleAnimation)
        startAnimation.playSequence(self.__fakeModel)
        fullStartAnimation.playSequence(self.__fakeModel)
        self.delayCallback(1.0, idleAnimation.playSequence, self.__fakeModel)
        self.delayCallback(15.0, fullIdleAnimation.playSequence, self.__fakeModel)

    def __initialStart(self):
        self.__started = True
        startAnimation = EffectController('volot_start')
        idleAnimation = EffectController('volot_idle')
        self.__effectControllers.append(startAnimation)
        self.__effectControllers.append(idleAnimation)
        startAnimation.playSequence(self.__fakeModel)
        self.delayCallback(5.0, idleAnimation.playSequence, self.__fakeModel)

    def __energyRing(self, number):
        ringStart = EffectController('volot_ring_start')
        ringIdle = EffectController('volot_ring_idle')
        fakemodel = BigWorld.Model('')
        fakemodel.position = self.__collector.position + Vector3(0, 0.2 + _ENERGY_RING_Y_OFFSET_STEP * number, 0)
        BigWorld.player().addModel(fakemodel)
        self.__energyRingEffects.append(ringStart)
        self.__energyRingEffects.append(ringIdle)
        self.__ringFakeModels.append(fakemodel)
        ringStart.playSequence(fakemodel)
        self.delayCallback(1.0, ringIdle.playSequence, fakemodel)
