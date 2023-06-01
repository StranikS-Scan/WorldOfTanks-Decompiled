# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/mines_object.py
import BigWorld
import Math
import AnimationSequence
import SoundGroups
from PlayerEvents import g_playerEvents
from gui.battle_control import avatar_getter
from helpers import dependency
from Math import Matrix
from battleground.component_loading import loadComponentSystem, Loader, CompositeLoaderMixin
from battleground.components import TerrainAreaGameObject, EffectPlayerObject, SequenceObject, SmartSequenceObject
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
_CONFIG_PATH = 'scripts/dynamic_objects.xml'

def _getSequenceResourceMapping(path, spaceId):
    return {'sequence': Loader(AnimationSequence.Loader(path, spaceId))}


def _getEffectResourceMapping(name):
    return {'effectList': Loader(_CONFIG_PATH, effectsListName=name)}


@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def loadMines(ownerVehicleID, callback, dynamicObjectsCache=None, battleSession=None):
    loaders = {}
    effDescr = dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getMinesEffect()
    isAlly = False
    ownerVehicleInfo = battleSession.getArenaDP().getVehicleInfo(ownerVehicleID)
    if not avatar_getter.isObserver():
        playerTeam = avatar_getter.getPlayerTeam()
    else:
        observedVehicleID = avatar_getter.getVehicleIDAttached()
        observedVehicleInfo = battleSession.getArenaDP().getVehicleInfo(observedVehicleID)
        playerTeam = observedVehicleInfo.team
    if ownerVehicleInfo is not None:
        isAlly = playerTeam == ownerVehicleInfo.team
    idleEff = effDescr.idleEffect.ally if isAlly else effDescr.idleEffect.enemy
    hasActivationEffect = hasattr(effDescr, 'activationEffect') and effDescr.activationEffect
    gameObject = MinesObject(isAlly, hasActivationEffect)
    gameObject.prepareCompositeLoader(callback)
    spaceId = BigWorld.player().spaceID
    loadComponentSystem(gameObject.startEffectPlayer, gameObject.appendPiece, _getSequenceResourceMapping(effDescr.plantEffect.effectDescr.path, spaceId))
    loadComponentSystem(gameObject.destroyEffectPlayer, gameObject.appendPiece, _getSequenceResourceMapping(effDescr.destroyEffect.effectDescr.path, spaceId))
    loadComponentSystem(gameObject.idleEffectPlayer, gameObject.appendPiece, _getSequenceResourceMapping(idleEff.path, spaceId))
    loadComponentSystem(gameObject.blowUpEffectPlayer, gameObject.appendPiece, _getEffectResourceMapping(effDescr.blowUpEffectName))
    if hasActivationEffect:
        loadComponentSystem(gameObject.activationEffectPlayer, gameObject.appendPiece, _getEffectResourceMapping(effDescr.activationEffect))
    loadComponentSystem(gameObject.decalEffectPlayer, gameObject.appendPiece, _getEffectResourceMapping(effDescr.placeMinesEffect))
    loadComponentSystem(gameObject, gameObject.appendPiece, loaders)
    return gameObject


class MinesObject(TerrainAreaGameObject, CompositeLoaderMixin):

    def __init__(self, isAllyMine, hasActivationDelay):
        super(MinesObject, self).__init__(BigWorld.player().spaceID)
        self.__position = Math.Vector3()
        self.__isAllyMine = isAllyMine
        self.__isEnemyMarkerEnabled = False
        self.__isActivated = False
        self.activationTimeDelay = 0
        self.mineNumber = 0
        self.__pendingEffects = []
        if not self.__isAvatarReady:
            g_playerEvents.onAvatarReady += self.__onAvatarReady
        self.startEffectPlayer = SmartSequenceObject()
        self.idleEffectPlayer = SequenceObject()
        self.destroyEffectPlayer = SmartSequenceObject()
        self.blowUpEffectPlayer = EffectPlayerObject()
        self.activationEffectPlayer = EffectPlayerObject()
        self.decalEffectPlayer = EffectPlayerObject()
        self.__soundTimerEventStart = 'eb_ability_minefield_zone_timer_start'
        self.__soundTimerEventEnd = 'eb_ability_minefield_zone_timer_end'
        self.__soundTimerObjStart = None
        self.__soundTimerObjEnd = None
        self.__children = (self.startEffectPlayer,
         self.idleEffectPlayer,
         self.destroyEffectPlayer,
         self.blowUpEffectPlayer,
         self.decalEffectPlayer)
        if hasActivationDelay:
            self.__children += (self.activationEffectPlayer,)
        return

    def destroy(self):
        self.__pendingEffects = []
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        super(MinesObject, self).destroy()

    def setPosition(self, position):
        super(MinesObject, self).setPosition(position)
        self.__position = position

    def setIsEnemyMarkerEnabled(self, value):
        self.__isEnemyMarkerEnabled = value

    def setIsActivated(self, value):
        self.__isActivated = value

    def setActivationTimeDelay(self, value):
        self.activationTimeDelay = value

    def setMineNumber(self, value):
        self.mineNumber = value

    def hasActivationEffect(self):
        return self.activationTimeDelay > 0

    def activate(self):
        super(MinesObject, self).activate()
        for child in self.__children:
            child.activate()

        if self.__isFirstMine():
            self.__soundTimerObjStart = self.__getSoundObject(self.__soundTimerEventStart)
            self.__soundTimerObjEnd = self.__getSoundObject(self.__soundTimerEventEnd)
        self.__playEffectOnAvatarReady(self.__playStartEffects)

    def activateMine(self):
        self.__playEffectOnAvatarReady(self.__playActivateMineEffects)

    def deactivate(self):
        super(MinesObject, self).deactivate()
        for child in self.__children:
            child.deactivate()

        self.__playEffectOnAvatarReady(self.__playStopEffects)
        if self.hasActivationEffect():
            self.activationEffectPlayer.stop()
        self.idleEffectPlayer.stop()
        self.decalEffectPlayer.stop()

    def detonate(self):
        self.__playEffectOnAvatarReady(self.__playDetonateEffects)

    def enableEnemyIdleEffect(self, isEnabled):
        if self.__isAllyMine:
            return
        if isEnabled == self.__isEnemyMarkerEnabled:
            return
        if isEnabled:
            self.__playEffectOnAvatarReady(self.__playIdleEffects)
        else:
            self.idleEffectPlayer.stop()

    def _piecesNum(self):
        return len(self.__children) + 1

    def __getSoundObject(self, name):
        mPos = Matrix()
        mPos.translation = self.__position
        return SoundGroups.g_instance.WWgetSoundObject(self.__getSoundObjName(name), mPos)

    def __getSoundObjName(self, eventName):
        return '{}_{}'.format(eventName, self.id)

    def __isFirstMine(self):
        return self.mineNumber == 0

    @property
    def __isAvatarReady(self):
        player = BigWorld.player()
        return player is not None and player.userSeesWorld()

    def __playStartEffects(self):
        self.startEffectPlayer.bindAndStart(self.__position, self._nativeSystem.spaceID)
        if not self.hasActivationEffect() or self.__isActivated:
            if self.__isAllyMine or self.__isEnemyMarkerEnabled:
                self.__playIdleEffects()
        elif self.__isFirstMine() and self.__soundTimerObjStart:
            self.__soundTimerObjStart.play(self.__soundTimerEventStart)
        self.decalEffectPlayer.start(self.__position)

    def __playActivateMineEffects(self):
        self.decalEffectPlayer.stop()
        if self.__isFirstMine() and self.hasActivationEffect():
            if self.__soundTimerObjStart:
                self.__soundTimerObjStart.stopAll()
            if self.__soundTimerObjEnd:
                self.__soundTimerObjEnd.play(self.__soundTimerEventEnd)
        if self.__isAllyMine or self.__isEnemyMarkerEnabled:
            self.__playIdleEffects()
        self.activationEffectPlayer.start(self.__position)

    def __playStopEffects(self):
        self.destroyEffectPlayer.bindAndStart(self.__position, self._nativeSystem.spaceID)

    def __playIdleEffects(self):
        self.idleEffectPlayer.bindAndStart(self.__position)

    def __playDetonateEffects(self):
        self.blowUpEffectPlayer.start(self.__position)

    def __playEffectOnAvatarReady(self, effect):
        if self.__isAvatarReady:
            effect()
        else:
            self.__pendingEffects.append(effect)

    def __onAvatarReady(self):
        for effect in self.__pendingEffects:
            effect()

        self.__pendingEffects = []
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
