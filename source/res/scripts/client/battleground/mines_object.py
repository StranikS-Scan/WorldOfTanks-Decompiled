# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/mines_object.py
import BigWorld
import Math
import AnimationSequence
from helpers import dependency
from battleground.component_loading import loadComponentSystem, Loader
from battleground.components import TerrainAreaGameObject, SequenceComponent, EffectPlayer
from svarog_script.auto_properties import AutoPropertyInitMetaclass
from svarog_script.script_game_object import ComponentDescriptorTyped
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
_CONFIG_PATH = 'scripts/dynamic_objects.xml'

@dependency.replace_none_kwargs(dynamicObjectsCache=IBattleDynamicObjectsCache, battleSession=IBattleSessionProvider)
def loadMines(ownerVehicleID, callback, dynamicObjectsCache=None, battleSession=None):
    gameObject = MinesObject()
    loaders = {}
    effDescr = dynamicObjectsCache.getConfig(battleSession.arenaVisitor.getArenaGuiType()).getMinesEffect()
    isAlly = False
    ownerVehicleInfo = battleSession.getArenaDP().getVehicleInfo(ownerVehicleID)
    if ownerVehicleInfo is not None:
        isAlly = ownerVehicleInfo.team == BigWorld.player().followTeamID
    idleEff = effDescr.idleEffect.ally if isAlly else effDescr.idleEffect.enemy
    spaceId = BigWorld.player().spaceID
    loaders['startEffectPlayer'] = Loader(AnimationSequence.Loader(effDescr.plantEffect.effectDescr.path, spaceId))
    loaders['destroyEffectPlayer'] = Loader(AnimationSequence.Loader(effDescr.destroyEffect.effectDescr.path, spaceId))
    loaders['idleEffectPlayer'] = Loader(AnimationSequence.Loader(idleEff.path, spaceId))
    loaders['blowUpEffectPlayer'] = Loader(_CONFIG_PATH, effectsListName='minesBlowUpEffect')
    loaders['decalEffectPlayer'] = Loader(_CONFIG_PATH, effectsListName='minesDecalEffect')
    loadComponentSystem(gameObject, callback, loaders)
    return gameObject


class MinesObject(TerrainAreaGameObject):
    __metaclass__ = AutoPropertyInitMetaclass
    startEffectPlayer = ComponentDescriptorTyped(SequenceComponent)
    idleEffectPlayer = ComponentDescriptorTyped(SequenceComponent)
    destroyEffectPlayer = ComponentDescriptorTyped(SequenceComponent)
    blowUpEffectPlayer = ComponentDescriptorTyped(EffectPlayer)
    decalEffectPlayer = ComponentDescriptorTyped(EffectPlayer)

    def __init__(self):
        super(MinesObject, self).__init__(BigWorld.player().spaceID)
        self.__position = Math.Vector3()

    def setPosition(self, position):
        super(MinesObject, self).setPosition(position)
        self.__position = position

    def activate(self):
        super(MinesObject, self).activate()
        if self.startEffectPlayer is not None:
            self.startEffectPlayer.bindAsTerrainEffect(self.__position, self._nativeSystem.worldID)
            self.startEffectPlayer.start()
        if self.idleEffectPlayer is not None:
            self.idleEffectPlayer.createTerrainEffect(self.__position, None, -1)
            self.idleEffectPlayer.start()
        if self.decalEffectPlayer is not None:
            self.decalEffectPlayer.play(self.__position)
        return

    def deactivate(self):
        super(MinesObject, self).deactivate()
        if self.destroyEffectPlayer is not None:
            self.destroyEffectPlayer.bindAsTerrainEffect(self.__position, self._nativeSystem.worldID)
            self.destroyEffectPlayer.start()
        if self.idleEffectPlayer is not None:
            self.idleEffectPlayer.stop()
        if self.decalEffectPlayer is not None:
            self.decalEffectPlayer.stop()
        return

    def detonate(self):
        if self.blowUpEffectPlayer is not None:
            self.blowUpEffectPlayer.play(self.__position)
        return
