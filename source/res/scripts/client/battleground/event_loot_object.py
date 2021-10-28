# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/event_loot_object.py
import math
import random
import BigWorld
import Math
import ResMgr
import WWISE
import AnimationSequence
from battleground.iself_assembler import ISelfAssembler
from cgf_obsolete_script.py_component import Component
from cgf_obsolete_script.script_game_object import ScriptGameObject, ComponentDescriptorTyped
from battleground.component_loading import loadComponentSystem, Loader
from debug_utils import LOG_ERROR
from cgf_obsolete_script.auto_properties import AutoPropertyInitMetaclass
LOOT_EFFECTS_PATH = 'scripts/item_defs/loot/loot_effects.xml'
LOOT_CONFIG_PATH = 'scripts/dynamic_objects.xml'

class LootDatabase(object):
    _database = {}
    _lootTypes = None

    @staticmethod
    def getItemDesc(itemName, reader=None):
        itemDesc = LootDatabase._database.get(itemName, None)
        if itemDesc is None:
            if reader is None:
                reader = componentReader
            itemDesc = reader(itemName, LOOT_CONFIG_PATH)
            LootDatabase._database[itemName] = itemDesc
        return itemDesc

    @staticmethod
    def getItemDescByID(itemID, reader=None):
        itemDesc = None
        if LootDatabase._lootTypes is None:
            LootDatabase.loadTypes()
        if LootDatabase._lootTypes is not None:
            itemName = LootDatabase._lootTypes.get(itemID, None)
            if itemName is not None:
                itemDesc = LootDatabase._database.get(itemName, None)
                if itemDesc is None:
                    if reader is None:
                        reader = componentReader
                    itemDesc = reader(itemName, LOOT_CONFIG_PATH)
                    LootDatabase._database[itemName] = itemDesc
        return itemDesc

    @staticmethod
    def loadTypes():
        LootDatabase._lootTypes = {}
        path = LOOT_CONFIG_PATH + '/eventLootTypes'
        section = ResMgr.openSection(path)
        if section is None:
            LOG_ERROR('[Loot] Cannot read loot types in %s.' % path)
        for typeDesc in section.items():
            typeName = typeDesc[1]['name'].asString.strip()
            typeID = typeDesc[1]['id'].asInt
            LootDatabase._lootTypes[typeID] = typeName

        return


def componentReader(name, path):
    path += '/' + name
    section = ResMgr.openSection(path)
    itemDescs = {}
    if section is None:
        LOG_ERROR('[Loot] Cannot read item %s in %s.' % (name, path))
    for component in section.items():
        componentName = component[0]
        params = {}
        for param in component[1].items():
            dataItems = param[1].values()
            if dataItems:
                value = []
                for dataItem in dataItems:
                    value.append(dataItem.asString.strip())

            else:
                value = param[1].asString.strip()
                vector_arr = value.split()
                if len(vector_arr) == 1:
                    try:
                        value = float(value)
                    except Exception:
                        pass

                else:
                    try:
                        value = Math.Vector3(*map(float, vector_arr[:3]))
                    except Exception:
                        pass

            params[param[0]] = value

        itemDescs[componentName] = params

    return itemDescs


def loadLootById(radius, callback, typeID):
    itemDesc = LootDatabase.getItemDescByID(typeID)
    return _loadLoot(typeID, radius, callback, itemDesc) if itemDesc is not None else None


def loadLootByName(radius, callback, typeName):
    itemDesc = LootDatabase.getItemDesc(typeName)
    return _loadLoot(0, radius, callback, itemDesc) if itemDesc is not None else None


def _loadLoot(typeID, radius, callback, desc):
    loot = LootObject(radius, typeID)
    loaders = {}
    for name, params in desc.items():
        if name == 'model':
            modelName = params.get('name', None)
            modelAssembler = None
            if modelName is None:
                modelName = params.get('names', ('',))
                modelName = random.choice(modelName).strip()
            offset = params.get('offset', (0, params.get('overTerrainHeight', 0), 0))
            borderName = params.get('border', None)
            animation = params.get('animation', None)
            if animation is not None:
                if borderName is not None:
                    modelAssembler = BigWorld.CompoundAssembler('model', BigWorld.player().spaceID, borderName)
                loaders['animatedModel'] = Loader(modelName, offset=offset, animation=animation)
                offset = (0, 0, 0)
            else:
                modelAssembler = BigWorld.CompoundAssembler('model', BigWorld.player().spaceID)
                modelAssembler.addRootPart(modelName, 'root')
                borderName = params.get('border', None)
                if borderName is not None:
                    borderMatrix = Math.Matrix()
                    modelAssembler.addPart(borderName, 'root', 'border', borderMatrix)
            if modelAssembler is not None:
                loaders['model'] = Loader(modelAssembler, offset=offset, randomYaw=params.get('randomYaw', False), animation=params.get('animation', None), sound=params.get('sound', None))
        if name == 'area':
            loaders['terrainArea'] = Loader(BigWorld.TerrainAreaAssembler(params['model'], params['overTerrainHeight'], Math.Vector2(radius, radius), 4294967295L, True))
        if name == 'particle':
            loaders['markingSmoke'] = Loader(params['name'], offset=params.get('offset', None))
        if name == 'startEffect':
            loaders['startEffectPlayer'] = Loader(LOOT_EFFECTS_PATH, effectsListName=params['name'])
        if name == 'pickupEffect':
            loaders['pickupEffectPlayer'] = Loader(LOOT_EFFECTS_PATH, effectsListName=params['name'])
        if name == 'destroyEffect':
            loaders['destroyEffectPlayer'] = Loader(LOOT_EFFECTS_PATH, effectsListName=params['name'])
        if name == 'idleEffect':
            loaders['idleEffectPlayer'] = Loader(LOOT_EFFECTS_PATH, effectsListName=params['name'])
        if name == 'minimapPoint':
            setattr(loot, 'minimapSymbol', params['name'])
        if name == 'sequence':
            loaders['sequence'] = Loader(AnimationSequence.Loader(params['name'], BigWorld.player().spaceID))

    loadComponentSystem(loot, callback, loaders)
    return loot


class SequenceComponent(Component):

    def __init__(self, sequence, *args, **kwargs):
        self._active = False
        self._model = None
        self._spaceID = None
        self._sequence = sequence
        self._position = Math.Vector3(0.0, 0.0, 0.0)
        return

    def setPosition(self, position):
        self._position = position

    def activate(self):
        self._active = True
        self._spaceID = BigWorld.player().spaceID
        self._attachModel()

    def deactivate(self):
        self._detachModel()
        self._active = False

    def _attachModel(self):
        self._model = BigWorld.Model('')
        self._model.position = self._position
        BigWorld.player().addModel(self._model)
        if self._sequence is not None:
            self._sequence.bindTo(AnimationSequence.ModelWrapperContainer(self._model, self._spaceID))
            self._sequence.start()
        return

    def _detachModel(self):
        if self._model is not None and self._active:
            self._sequence.stop()
            self._sequence = None
            BigWorld.player().delModel(self._model)
            self._model = None
        self._spaceID = None
        return

    def destroy(self):
        self._detachModel()
        self._active = False


class ModelComponent(Component):

    @property
    def position(self):
        return self.__baseModel.position

    def __init__(self, compoundModel, **kwargs):
        setattr(self, 'compoundModel', compoundModel)
        self.__animation = kwargs.get('animation', None)
        self.__offset = Math.Vector3(kwargs.get('offset', (0, 0, 0)))
        if kwargs.get('randomYaw', False):
            yaw = random.uniform(0, math.pi)
            radius = self.__offset.flatDistTo((0, 0, 0))
            self.__offset.x = radius * math.cos(yaw)
            self.__offset.z = radius * math.sin(yaw)
        self.__baseModel = compoundModel
        sound = kwargs.get('sound', None)
        self.__sound = None
        if sound is not None:
            self.__sound = WWISE.WW_getSound(sound, sound, self.__baseModel.root, Math.Vector3(0.0, 0.0, 0.0))
        self._active = False
        return

    def activate(self):
        if self.compoundModel is not None:
            BigWorld.player().addModel(self.compoundModel)
            if self.__animation is not None:
                self.compoundModel.action(self.__animation)()
        if self.__sound is not None:
            self.__sound.play()
        self._active = True
        return

    def deactivate(self):
        if not self._active:
            return
        else:
            if self.__sound is not None:
                self.__sound.stop()
                self.__sound = None
            if self.compoundModel is not None:
                BigWorld.player().delModel(self.compoundModel)
            return

    def setPosition(self, position):
        if self.compoundModel is not None:
            self.compoundModel.position = position + self.__offset
        return

    def attach(self, attachment, offset=None):
        if offset is not None:
            offsetMatrix = Math.Matrix()
            offsetMatrix.setTranslate(offset)
            self.__baseModel.root.attach(attachment, offsetMatrix)
        else:
            self.__baseModel.root.attach(attachment)
        return

    def detach(self, attachment):
        self.__baseModel.root.detach(attachment)

    def setMotor(self, matrix):
        if self.compoundModel is not None:
            if getattr(self.compoundModel, 'addMotor') is not None:
                self.compoundModel.addMotor(BigWorld.Servo(matrix))
            else:
                self.compoundModel.matrix = matrix
        return

    def getModel(self):
        return self.compoundModel


class ParticleComponent(Component):

    def __init__(self, particle, offset):
        self.particle = particle
        self.offset = offset


class EffectPlayer(Component):

    def __init__(self, effectsListSectionRoot, effectsListName):
        arena = BigWorld.player().arena
        timeline = arena.componentSystem.effectsListCache.loadFromRootDataSection(effectsListName, effectsListSectionRoot)
        self.effectsListTimeLine = timeline
        self.__effectID = None
        return

    def play(self, pickupPosition):
        if self.__effectID:
            BigWorld.player().terrainEffects.stop(self.__effectID)
        velocityDir = Math.Vector3(0, 1, 0)
        self.__effectID = BigWorld.player().terrainEffects.addNew(pickupPosition, self.effectsListTimeLine.effectsList, self.effectsListTimeLine.keyPoints, None, start=pickupPosition + velocityDir, end=pickupPosition - velocityDir)
        return

    def stop(self):
        if self.__effectID:
            BigWorld.player().terrainEffects.stop(self.__effectID)
            self.__effectID = None
        return


class TerrainAreaComponent(Component):

    def __init__(self, area):
        self.area = area


class ILootObject(ScriptGameObject):
    model = None

    def processPickup(self, entityID):
        pass


class LootObject(ILootObject, ISelfAssembler):
    __metaclass__ = AutoPropertyInitMetaclass
    model = ComponentDescriptorTyped(ModelComponent)
    animatedModel = ComponentDescriptorTyped(ModelComponent)
    markingSmoke = ComponentDescriptorTyped(ParticleComponent)
    startEffectPlayer = ComponentDescriptorTyped(EffectPlayer)
    idleEffectPlayer = ComponentDescriptorTyped(EffectPlayer)
    pickupEffectPlayer = ComponentDescriptorTyped(EffectPlayer)
    destroyEffectPlayer = ComponentDescriptorTyped(EffectPlayer)
    terrainArea = ComponentDescriptorTyped(TerrainAreaComponent)
    sequence = ComponentDescriptorTyped(SequenceComponent)

    def __init__(self, radius, lootTypeID):
        super(LootObject, self).__init__(BigWorld.player().spaceID)
        self.radius = radius
        self.lootTypeID = lootTypeID
        self.__rootModel = None
        self.model = None
        self.animatedModel = None
        self.markingSmoke = None
        self.startEffectPlayer = None
        self.idleEffectPlayer = None
        self.pickupEffectPlayer = None
        self.destroyEffectPlayer = None
        self.terrainArea = None
        self.minimapSymbol = None
        self.sequence = None
        self.__position = Math.Vector3()
        return

    def activate(self):
        super(LootObject, self).activate()
        if self.startEffectPlayer is not None:
            self.startEffectPlayer.play(self.__position)
        if self.idleEffectPlayer is not None:
            self.idleEffectPlayer.play(self.__position)
        return

    def deactivate(self):
        super(LootObject, self).deactivate()
        if self.destroyEffectPlayer is not None:
            self.destroyEffectPlayer.play(self.__position)
        if self.idleEffectPlayer is not None:
            self.idleEffectPlayer.stop()
        return

    def assembleOnLoad(self):
        if not self.model:
            return
        else:
            if self.markingSmoke is not None:
                pixie = self.markingSmoke.particle
                if pixie is not None:
                    self.model.attach(pixie, self.markingSmoke.offset)
            if self.terrainArea is not None:
                self.model.attach(self.terrainArea.area)
            return

    def processPickup(self, entityID):
        if self.pickupEffectPlayer is not None:
            self.pickupEffectPlayer.play(self.__position)
        self.stopSmoke()
        return

    def startSmoke(self):
        if self.markingSmoke and self.markingSmoke.particle is not None and not self.markingSmoke.particle.attached:
            self.model.attach(self.markingSmoke.particle)
        return

    def stopSmoke(self):
        if self.markingSmoke and self.markingSmoke.particle is not None and self.markingSmoke.particle.attached:
            self.model.detach(self.markingSmoke.particle)
        return

    def setPosition(self, position):
        self.__position = position
        if self.model is not None:
            self.model.setPosition(position)
        if self.sequence is not None:
            self.sequence.setPosition(position)
        if self.animatedModel is not None:
            self.animatedModel.setPosition(position)
        return
