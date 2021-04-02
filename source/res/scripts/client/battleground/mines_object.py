# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/mines_object.py
import BigWorld
import Math
import AnimationSequence
from helpers import dependency
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
    gameObject = MinesObject()
    loaders = {}
    effDescr = dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getMinesEffect()
    isAlly = False
    ownerVehicleInfo = battleSession.getArenaDP().getVehicleInfo(ownerVehicleID)
    if ownerVehicleInfo is not None:
        isAlly = battleSession.getArenaDP().isAllyTeam(ownerVehicleInfo.team)
    idleEff = effDescr.idleEffect.ally if isAlly else effDescr.idleEffect.enemy
    gameObject.prepareCompositeLoader(callback)
    spaceId = BigWorld.player().spaceID
    loadComponentSystem(gameObject.startEffectPlayer, gameObject.appendPiece, _getSequenceResourceMapping(effDescr.plantEffect.effectDescr.path, spaceId))
    loadComponentSystem(gameObject.destroyEffectPlayer, gameObject.appendPiece, _getSequenceResourceMapping(effDescr.destroyEffect.effectDescr.path, spaceId))
    loadComponentSystem(gameObject.idleEffectPlayer, gameObject.appendPiece, _getSequenceResourceMapping(idleEff.path, spaceId))
    loadComponentSystem(gameObject.blowUpEffectPlayer, gameObject.appendPiece, _getEffectResourceMapping('minesBlowUpEffect'))
    loadComponentSystem(gameObject.decalEffectPlayer, gameObject.appendPiece, _getEffectResourceMapping('minesDecalEffect'))
    loadComponentSystem(gameObject, gameObject.appendPiece, loaders)
    return gameObject


class MinesObject(TerrainAreaGameObject, CompositeLoaderMixin):

    def __init__(self):
        super(MinesObject, self).__init__(BigWorld.player().spaceID)
        self.__position = Math.Vector3()
        self.startEffectPlayer = SmartSequenceObject()
        self.idleEffectPlayer = SequenceObject()
        self.destroyEffectPlayer = SmartSequenceObject()
        self.blowUpEffectPlayer = EffectPlayerObject()
        self.decalEffectPlayer = EffectPlayerObject()
        self.__children = (self.startEffectPlayer,
         self.idleEffectPlayer,
         self.destroyEffectPlayer,
         self.blowUpEffectPlayer,
         self.decalEffectPlayer)

    def setPosition(self, position):
        super(MinesObject, self).setPosition(position)
        self.__position = position

    def activate(self):
        super(MinesObject, self).activate()
        for child in self.__children:
            child.activate()

        self.startEffectPlayer.bindAndStart(self.__position, self._nativeSystem.spaceID)
        self.idleEffectPlayer.bindAndStart(self.__position)
        self.decalEffectPlayer.start(self.__position)

    def deactivate(self):
        super(MinesObject, self).deactivate()
        for child in self.__children:
            child.deactivate()

        self.destroyEffectPlayer.bindAndStart(self.__position, self._nativeSystem.spaceID)
        self.idleEffectPlayer.stop()
        self.decalEffectPlayer.stop()

    def detonate(self):
        self.blowUpEffectPlayer.start(self.__position)

    def _piecesNum(self):
        return len(self.__children) + 1
