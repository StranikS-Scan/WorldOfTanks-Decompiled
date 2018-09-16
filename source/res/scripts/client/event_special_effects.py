# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_special_effects.py
import BigWorld
import ResMgr
import Math
from debug_utils import LOG_WARNING
from items import vehicles
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from helpers.EffectsList import effectsFromSection, EffectsTimeLinePrereqs
from material_kinds import EFFECT_MATERIALS
from skeletons.gui.battle_session import IBattleSessionProvider
_FOOTBALL_EFFECTS = 'scripts/dynamic_objects.xml/footballBattle/effects/'
_BALL_EFFECTS_PATH = 'ball'
_BALL_HIT_EFFECTS_PATH = 'ball_hit'
_GUN_EFFECTS_PATH = 'gun'
_SHOT_EFFECTS_PATH = 'shot'
_CYLINDER_EFFECTS_PATH = 'cylinders/{}/'
_EFFECT_NAME_TEMPLATE = '{}_{}'

class BallEffectType(object):
    DESTRUCTION = 'destruction'
    RAM = 'ram'
    HIT_SOUND = 'hit_sound'
    RESPAWN = 'respawn'
    ALL = (DESTRUCTION,
     RAM,
     HIT_SOUND,
     RESPAWN)


class VClassType(object):
    LIGHT = 0
    MEDIUM = 1
    HEAVY = 2
    ALL = (LIGHT, MEDIUM, HEAVY)
    BY_NAME = {'lightTank': LIGHT,
     'mediumTank': MEDIUM,
     'heavyTank': HEAVY}
    BY_IDX = {v:k for k, v in BY_NAME.iteritems()}

    @staticmethod
    def getClassIndex(vehicle):
        vehicleTags = vehicle.typeDescriptor.type.tags if vehicle else set()
        for vehClass in frozenset(VClassType.BY_NAME.keys()) & vehicleTags:
            return VClassType.BY_NAME[vehClass]

        return VClassType.LIGHT


class TeamType(object):
    TEAM_BALL = 0
    TEAM_RED = 1
    TEAM_BLUE = 2
    PLAYABLE = (TEAM_BLUE, TEAM_RED)
    ALL = (TEAM_BALL,) + PLAYABLE
    BY_NAME = {'red': TEAM_RED,
     'blue': TEAM_BLUE % len(PLAYABLE)}
    BY_IDX = {v:k for k, v in BY_NAME.iteritems()}
    BY_NAME_ALL = {'ball': TEAM_BALL,
     'red': TEAM_RED,
     'blue': TEAM_BLUE}
    BY_IDX_ALL = {v:k for k, v in BY_NAME_ALL.iteritems()}

    @staticmethod
    def getTeamName(teamIdx):
        teamIdx = teamIdx % len(TeamType.ALL)
        return TeamType.BY_IDX_ALL[teamIdx]


class RenderType(object):
    FORWARD = 'forward'
    DEFFERED = 'deffered'
    ALL = (FORWARD, DEFFERED)
    _CURRENT = None

    @staticmethod
    def getRenderType():
        RenderType._CURRENT = RenderType._CURRENT or RenderType.ALL[int(isRendererPipelineDeferred())]
        return RenderType._CURRENT


_VEHICLE_SHOT_EFFECTS = ('FootballSmallHighExplosive_{}', 'FootballMainHighExplosive_{}', 'FootballHugeHighExplosive_{}')

class EventEffectsStorage(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__ballEffects = {effectType:None for effectType in BallEffectType.ALL}
        self.__knownVehicleIdx = {}
        size = len(TeamType.PLAYABLE) * len(VClassType.ALL)
        self.__hitEffects = [None] * (size + 1)
        self.__gunEffects = [None] * size
        self.__cylinderModels = [''] * len(TeamType.ALL)
        return

    def getBallHitEffectForVehicle(self, vehicle, ownShot=False):
        idx = self._getOwnVehicleIndex() if ownShot else self._getVehicleIndex(vehicle)
        return self.__hitEffects[idx]

    def getGunEffectForVehicle(self, vehicle):
        idx = self._getVehicleIndex(vehicle)
        return self.__gunEffects[idx]

    def getHighlightCylinderForEntity(self, entity):
        team = self._getTeamIdx(entity)
        modelName = self.__cylinderModels[team]
        return HighlightCylinder(modelName)

    def getBallEffect(self, effectType):
        return self.__ballEffects[effectType] if effectType in self.__ballEffects else None

    def readCfg(self):
        effectsSec = ResMgr.openSection(_FOOTBALL_EFFECTS)
        if effectsSec is None:
            return
        else:
            ballEffectSec = effectsSec[_BALL_EFFECTS_PATH]
            if ballEffectSec is not None:
                self._readBallEffects(ballEffectSec)
            hitEffectsSec = effectsSec[_BALL_HIT_EFFECTS_PATH]
            if hitEffectsSec is not None:
                self._readHitEffects(hitEffectsSec)
            gunEffectsSec = effectsSec[_GUN_EFFECTS_PATH]
            if gunEffectsSec is not None:
                self._readGunEffects(gunEffectsSec)
            renderType = RenderType.getRenderType()
            cylinderEffectsSec = effectsSec[_CYLINDER_EFFECTS_PATH.format(renderType)]
            if cylinderEffectsSec is not None:
                self._readCylinderEffects(cylinderEffectsSec, self.__cylinderModels)
            return

    def prerequisites(self):
        prereqs = set()
        for effectTimeline in self.__ballEffects.itervalues():
            _, effects, readyPrereqs = effectTimeline
            if not readyPrereqs:
                prereqs.update(effects.prerequisites())

        for effectTimeline in self.__hitEffects:
            _, effects, readyPrereqs = effectTimeline
            if not readyPrereqs:
                prereqs.update(effects.prerequisites())

        for effectTimeline in self.__gunEffects:
            _, effects, readyPrereqs = effectTimeline
            if not readyPrereqs:
                prereqs.update(effects.prerequisites())

        for teamName in TeamType.BY_NAME.iterkeys():
            for effectName in _VEHICLE_SHOT_EFFECTS:
                effectName = effectName.format(teamName)
                effectIdx = vehicles.g_cache.shotEffectsIndexes[effectName]
                effectsDescr = vehicles.g_cache.shotEffects[effectIdx]
                if not effectsDescr['prereqs']:
                    projectileModel, projectileOwnShotModel, effects = effectsDescr['projectile']
                    prereqs.add(projectileModel)
                    prereqs.add(projectileOwnShotModel)
                    prereqs.update(effects.prerequisites())
                    for materialName in EFFECT_MATERIALS:
                        prereqs.update(effectsDescr[materialName + 'Hit'][1].prerequisites())

                    prereqs.update(effectsDescr['shallowWaterHit'][1].prerequisites())
                    prereqs.update(effectsDescr['deepWaterHit'][1].prerequisites())
                    prereqs.update(effectsDescr['armorResisted'][1].prerequisites())
                    prereqs.update(effectsDescr['armorBasicRicochet'][1].prerequisites())
                    prereqs.update(effectsDescr['armorRicochet'][1].prerequisites())
                    prereqs.update(effectsDescr['armorHit'][1].prerequisites())
                    prereqs.update(effectsDescr['armorCriticalHit'][1].prerequisites())

        return list(prereqs)

    def keepPrereqs(self, prereqs):
        for effectTimeline in self.__ballEffects.itervalues():
            _, effects, readyPrereqs = effectTimeline
            if not readyPrereqs:
                readyPrereqs.update(self._extract(prereqs, effects.prerequisites()))

        for effectTimeline in self.__hitEffects:
            _, effects, readyPrereqs = effectTimeline
            if not readyPrereqs:
                readyPrereqs.update(self._extract(prereqs, effects.prerequisites()))

        for effectTimeline in self.__gunEffects:
            _, effects, readyPrereqs = effectTimeline
            if not readyPrereqs:
                readyPrereqs.update(self._extract(prereqs, effects.prerequisites()))

        for teamName in TeamType.BY_NAME.iterkeys():
            for effectName in _VEHICLE_SHOT_EFFECTS:
                effectName = effectName.format(teamName)
                effectIdx = vehicles.g_cache.shotEffectsIndexes[effectName]
                effectsDescr = vehicles.g_cache.shotEffects[effectIdx]
                readyPrereqs = effectsDescr['prereqs']
                if not readyPrereqs:
                    projectileModel, projectileOwnShotModel, effects = effectsDescr['projectile']
                    readyPrereqs.update(self._extract(prereqs, (projectileModel, projectileOwnShotModel)))
                    readyPrereqs.update(self._extract(prereqs, effects.prerequisites()))
                    for materialName in EFFECT_MATERIALS:
                        readyPrereqs.update(self._extract(prereqs, effectsDescr[materialName + 'Hit'][1].prerequisites()))

                    readyPrereqs.update(self._extract(prereqs, effectsDescr['shallowWaterHit'][1].prerequisites()))
                    readyPrereqs.update(self._extract(prereqs, effectsDescr['deepWaterHit'][1].prerequisites()))
                    readyPrereqs.update(self._extract(prereqs, effectsDescr['armorResisted'][1].prerequisites()))
                    readyPrereqs.update(self._extract(prereqs, effectsDescr['armorBasicRicochet'][1].prerequisites()))
                    readyPrereqs.update(self._extract(prereqs, effectsDescr['armorRicochet'][1].prerequisites()))
                    readyPrereqs.update(self._extract(prereqs, effectsDescr['armorHit'][1].prerequisites()))
                    readyPrereqs.update(self._extract(prereqs, effectsDescr['armorCriticalHit'][1].prerequisites()))

    def _readBallEffects(self, effectsSec):
        for effectType in BallEffectType.ALL:
            section = effectsSec[effectType]
            if section is not None:
                effectsTimeline = effectsFromSection(section)
                self.__ballEffects[effectType] = self._wrapEffectsTimeline(effectsTimeline)

        return

    def _readHitEffects(self, effectsSec):
        self._readVehicleEffects(effectsSec, self.__hitEffects)
        self._readOwnVehicleEffects(effectsSec, self.__hitEffects)

    def _readGunEffects(self, effectsSec):
        self._readVehicleEffects(effectsSec, self.__gunEffects)

    def _getVehicleIndex(self, vehicle):
        if vehicle.id not in self.__knownVehicleIdx:
            index = self.__knownVehicleIdx[vehicle.id] = self._generateVehicleIndex(vehicle)
        else:
            index = self.__knownVehicleIdx[vehicle.id]
        return index

    def _getTeamIdx(self, entity):
        arenaDataProvider = self._sessionProvider.getArenaDP()
        vehicleInfo = arenaDataProvider.getVehicleInfo(entity.id)
        return vehicleInfo.team

    def _generateVehicleIndex(self, vehicle):
        teamIdx = self._getTeamIdx(vehicle) % len(TeamType.PLAYABLE)
        classIdx = self._getVehicleClassIdx(vehicle)
        return self._generateIndex(teamIdx, classIdx)

    @staticmethod
    def _extract(prereqs, resourceNames):
        res = []
        resourceNames = frozenset(resourceNames)
        for name in resourceNames:
            try:
                if name not in prereqs.failedIDs:
                    res.append(prereqs[name])
                else:
                    LOG_WARNING('Resource is not found: {}'.format(name))
                    res.append(None)
            except ValueError:
                LOG_WARNING('Resource is not found: {}'.format(name))
                res.append(None)

        return res

    @staticmethod
    def _wrapEffectsTimeline(effectsTimeline):
        return EffectsTimeLinePrereqs(effectsTimeline.keyPoints, effectsTimeline.effectsList, set()) if effectsTimeline is not None else EffectsTimeLinePrereqs(None, None, set())

    @staticmethod
    def _readSingleEffect(effectsSec, effectName, effectIdx, effectsList):
        section = effectsSec[effectName]
        effectsTimeline = effectsFromSection(section) if section is not None else None
        effectsList[effectIdx] = EventEffectsStorage._wrapEffectsTimeline(effectsTimeline)
        return

    @staticmethod
    def _readVehicleEffects(effectsSec, effectsList):
        for teamIdx, teamName in TeamType.BY_IDX.iteritems():
            for classIdx, className in VClassType.BY_IDX.iteritems():
                effectName = EventEffectsStorage._generateEffectName(teamName, className)
                effectIdx = EventEffectsStorage._generateIndex(teamIdx, classIdx)
                EventEffectsStorage._readSingleEffect(effectsSec, effectName, effectIdx, effectsList)

    @staticmethod
    def _readOwnVehicleEffects(effectsSec, effectsList):
        effectName = EventEffectsStorage._generateEffectName('players', 'own')
        effectIdx = EventEffectsStorage._getOwnVehicleIndex()
        EventEffectsStorage._readSingleEffect(effectsSec, effectName, effectIdx, effectsList)

    @staticmethod
    def _readCylinderEffects(effectsSec, cylindersList):
        for teamIdx, teamName in TeamType.BY_IDX_ALL.iteritems():
            cylindersList[teamIdx] = effectsSec.readString(teamName, '')

    @staticmethod
    def _generateEffectName(teamName, className):
        return _EFFECT_NAME_TEMPLATE.format(teamName, className)

    @staticmethod
    def _getVehicleClassIdx(vehicle):
        sizeIdx = VClassType.getClassIndex(vehicle)
        return sizeIdx

    @staticmethod
    def _generateIndex(teamIdx, classIdx):
        offset = len(TeamType.PLAYABLE) + 1
        return teamIdx * offset + classIdx

    @staticmethod
    def _getOwnVehicleIndex():
        idx = len(TeamType.PLAYABLE) * len(VClassType.ALL)
        return idx


class HighlightCylinder(object):
    _ROOT_NODE_NAME = 'root'

    @property
    def visible(self):
        return self.__model is not None and self.__model.visible

    @visible.setter
    def visible(self, visible):
        if self.__model is not None:
            self.__model.visible = visible
        return

    def __init__(self, modelName):
        self.__model = None
        self.__modelName = modelName
        return

    def destroy(self):
        self.detach()
        self.__model = None
        return

    def prerequisites(self):
        spaceID = BigWorld.player().spaceID
        assembler = BigWorld.CompoundAssembler(self.__modelName, spaceID)
        assembler.addRootPart(self.__modelName, HighlightCylinder._ROOT_NODE_NAME)
        return [assembler]

    def keepPrereqs(self, prereqs):
        if self.__modelName not in prereqs.failedIDs:
            self.__model = prereqs[self.__modelName]

    def attachTo(self, provider):
        self.detach()
        if self.__model:
            self.__model.matrix = provider
            BigWorld.player().addModel(self.__model)

    def detach(self):
        if self.__model in BigWorld.player().models:
            BigWorld.player().delModel(self.__model)
            self.__model.matrix = Math.Matrix()
