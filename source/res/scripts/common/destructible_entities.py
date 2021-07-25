# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/destructible_entities.py
import ResMgr
from items import _xml
from constants import IS_CLIENT, IS_BASEAPP, IS_BOT, IS_CELLAPP, IS_WEB
from debug_utils import LOG_DEBUG_DEV
from collections import namedtuple, OrderedDict
if IS_CELLAPP or IS_CLIENT or IS_WEB:
    import material_kinds
    from material_kinds import EFFECT_MATERIAL_INDEXES_BY_NAMES
g_destructibleEntitiesCache = None

class DESTRUCTIBLE_ENTITY_TYPES:
    EPIC_HEADQUARTER = 2


class DestructibleEntitiesCache(object):

    def __init__(self):
        self.destructibleEntityTypes = {}
        self.mapActivityLists = {}
        self.destroyEffectLists = {}
        self.materials = {}

    def getDestructibleEntityType(self, typeID):
        return self.destructibleEntityTypes.get(typeID, None)

    def getMapActivityList(self, name):
        return self.mapActivityLists.get(name, None)

    def getDestroyEffectList(self, name):
        return self.destroyEffectLists.get(name, None)

    def addDestructibleEntityType(self, destructibleEntityType):
        self.destructibleEntityTypes[destructibleEntityType.id] = destructibleEntityType


class DestructibleEntityType(object):
    maxNumStateComponents = property(lambda self: max((len(state.components) for state in self.states.values())))

    def __init__(self, id, displayName, health, destroyedNotificationRadius, materials, observationPoints=(), observedPoints=(), directVisionRadius=None, normalRadioDistance=None):
        self.id = id
        self.displayName = displayName
        self.health = health
        self.destroyedNotificationRadius = destroyedNotificationRadius
        self.materials = materials
        self.states = OrderedDict()
        self.observationPoints = observationPoints
        self.observedPoints = observedPoints
        self.directVisionRadius = directVisionRadius
        self.normalRadioDistance = normalRadioDistance

    def addState(self, name, state):
        self.states[name] = state


class DestructibleEntityState(object):

    def __init__(self):
        self.components = OrderedDict()
        if IS_CLIENT:
            self.effect = None
        return

    def addComponent(self, id, stateComponent):
        self.components[id] = stateComponent

    if IS_CLIENT:

        def setClientProperties(self, effect):
            self.effect = effect


class DestructibleEntityStateComponent(object):

    def __init__(self, destructible, physicsModel):
        self.destructible = destructible
        self.physicsModel = physicsModel
        if IS_CLIENT:
            self.guiNode = None
            self.visualModel = None
        return

    if IS_CLIENT:

        def setClientProperties(self, guiNode, visualModel):
            self.guiNode = guiNode
            self.visualModel = visualModel


def init():
    global g_destructibleEntitiesCache
    g_destructibleEntitiesCache = DestructibleEntitiesCache()
    xmlPath = 'scripts/item_defs/destructible_entities.xml'
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    for _, (typeXmlCtx, typeSection) in _xml.getItemsWithContext(xmlCtx, section, 'type'):
        destructibleEntityType = _readType(typeXmlCtx, typeSection)
        if g_destructibleEntitiesCache.getDestructibleEntityType(destructibleEntityType.id) is not None:
            _xml.raiseWrongXml(typeXmlCtx, 'id', 'duplicate id' % destructibleEntityType.id)
        g_destructibleEntitiesCache.addDestructibleEntityType(destructibleEntityType)

    if IS_CLIENT:
        _readDestructibleEntitiesEffects('scripts/destructible_entity_effects.xml')
    return


def determineDestructibleEntityTypeID(validVehicleLevels, defaultTypeID):
    validVehicleLevelsType3 = {8, 9}
    if set(validVehicleLevels) == validVehicleLevelsType3:
        return 3
    else:
        return defaultTypeID


def _readType(xmlCtx, section):
    id = section.readInt('id', -1)
    displayName = section.readString('display_name')
    health = section.readFloat('health', 100)
    destroyedNotificationRadius = section.readFloat('destroyedNotificationRadius', 0)
    materials = _readMaterials(*_xml.getSubSectionWithContext(xmlCtx, section, 'materials'))
    observationPoints = _readPointList(*_xml.getSubSectionWithContext(xmlCtx, section, 'observationPoints'))
    observedPoints = _readPointList(*_xml.getSubSectionWithContext(xmlCtx, section, 'observedPoints'))
    directVisionRadius = section.readFloat('directVisionRadius', 0)
    normalRadioDistance = section.readFloat('normalRadioDistance', 0)
    destructibleEntityType = DestructibleEntityType(id, displayName, health, destroyedNotificationRadius, materials, observationPoints=observationPoints, observedPoints=observedPoints, directVisionRadius=directVisionRadius, normalRadioDistance=normalRadioDistance)
    for _, (stateXmlCtx, stateSection) in _xml.getChildrenWithContext(xmlCtx, section, 'states'):
        destructibleEntityType.addState(*_readState(stateXmlCtx, stateSection))

    return destructibleEntityType


def _readPointList(xmlCtx, section):
    result = []
    for _, ((stateCompXmlCtx, _), point) in _xml.getItemsWithContext(xmlCtx, section, 'point'):
        result.append(point.asVector3)

    return result


def _readState(xmlCtx, section):
    state = DestructibleEntityState()
    for _, (stateCompXmlCtx, stateCompSection) in _xml.getChildrenWithContext(xmlCtx, section, 'components'):
        state.addComponent(*_readStateComponent(stateCompXmlCtx, stateCompSection))

    if IS_CLIENT:
        effect = section.readString('effect', '')
        if effect == '':
            effect = None
        state.setClientProperties(effect)
    return (_xml.readString(xmlCtx, section, 'name'), state)


def _readStateComponent(xmlCtx, section):
    destructible = _xml.readBool(xmlCtx, section, 'destructible')
    physicsModel = _xml.readString(xmlCtx, section, 'physics_model')
    component = DestructibleEntityStateComponent(destructible, physicsModel)
    if IS_CLIENT:
        visualModel = _xml.readString(xmlCtx, section, 'visual_model')
        guiNodeName = section.readString('gui_node', '')
        if guiNodeName == '':
            guiNodeName = None
        component.setClientProperties(guiNodeName, visualModel)
    return (_xml.readString(xmlCtx, section, 'id'), component)


def _readDestructibleEntitiesEffects(filename):
    section = ResMgr.openSection(filename)
    if section is None:
        _xml.raiseWrongXml(None, filename, 'can not open or read')
    mapActivitySection = section['map_activities']
    for s in mapActivitySection.values():
        name = s.readString('name')
        LOG_DEBUG_DEV('name ', name)
        activitySec = s['activities']
        activities = activitySec.readStrings('activity')
        LOG_DEBUG_DEV('activities ', activities)
        g_destructibleEntitiesCache.mapActivityLists[name] = activities

    destructionEffectsSection = section['destruction_effects']
    for s in destructionEffectsSection.values():
        name = s.readString('name')
        g_destructibleEntitiesCache.destroyEffectLists[name] = s

    return


DestructibleMaterialInfo = namedtuple('DestructibleMaterialInfo', ('kind', 'armor', 'effectMaterialIdx', 'extra', 'vehicleDamageFactor', 'useHitAngle', 'mayRicochet', 'collideOnceOnly', 'checkCaliberForRichet', 'checkCaliberForHitAngleNorm'))

def _readMaterials(parentXmlCtx, section):
    materials = {}
    if IS_BASEAPP or IS_BOT:
        return materials
    else:
        for matName, (xmlCtx, matSection) in _xml.getItemsWithContext(parentXmlCtx, section):
            matKind = material_kinds.IDS_BY_NAMES.get(matName)
            if matKind is None:
                _xml.raiseWrongXml(xmlCtx, matName, 'material kind name is unknown')
            if matKind in materials:
                _xml.raiseWrongXml(xmlCtx, matName, 'duplicate material kind')
            effectMaterialName = _xml.readString(xmlCtx, matSection, 'effectMaterial')
            effectMaterialIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES.get(effectMaterialName)
            if effectMaterialIdx is None:
                _xml.raiseWrongXml(xmlCtx, matName, 'Unknown effect material %s' % effectMaterialName)
            materials[matKind] = DestructibleMaterialInfo(kind=matKind, armor=_xml.readInt(xmlCtx, matSection, 'armor'), extra=None, vehicleDamageFactor=_xml.readFraction(xmlCtx, matSection, 'vehicleDamageFactor'), useHitAngle=_xml.readBool(xmlCtx, matSection, 'useHitAngle'), mayRicochet=_xml.readBool(xmlCtx, matSection, 'mayRicochet'), collideOnceOnly=True, checkCaliberForRichet=_xml.readBool(xmlCtx, matSection, 'checkCaliberForRichet'), checkCaliberForHitAngleNorm=_xml.readBool(xmlCtx, matSection, 'checkCaliberForHitAngleNorm'), effectMaterialIdx=effectMaterialIdx)

        return materials
