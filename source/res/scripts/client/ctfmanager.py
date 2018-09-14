# Embedded file name: scripts/client/CTFManager.py
import BigWorld
import Math
import operator
import Event
import ResMgr
from functools import partial
from debug_utils import *
from shared_utils import findFirst
from constants import FLAG_STATE, RESOURCE_POINT_STATE
from Math import Vector2, Vector3
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
_DYNAMIC_OBJECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_FLAG_MODEL_NAME = 'ctf_flag'
_FLAG_CIRCLE_MODEL_NAME = 'ctf_flag_circle'

class Flag(object):
    flagEntities = []

    def __init__(self, position, isVisible, flagID):
        position = Vector3(0.0, 0.0, 0.0) if position is None else position
        self.__flagEntity = None
        self.__position = position
        self.__isVisible = isVisible
        self.__flagID = flagID
        spaceId = BigWorld.player().spaceID
        if spaceId != 0:
            self.create()
        else:
            g_ctfManager.addDelayedFlag(self)
        return

    def flagEnterWorld(self, entity):
        if self.__flagEntity is not None:
            LOG_ERROR('Flags: Wrong usage of offline flags')
            return
        else:
            self.__flagEntity = entity
            self.__flagEntity.show(not g_ctfManager.isNeedHideAll and self.__isVisible)
            return

    def destroy(self):
        if self.__flagEntity is not None:
            self.__flagEntity.show(False)
        return

    def flagLeaveWorld(self):
        self.__flagEntity = None
        return

    def setPosition(self, position):
        self.__position = Vector3(0.0, 0.0, 0.0) if position is None else position
        if self.__flagEntity is not None:
            self.__flagEntity.setPosition(position)
        return

    def show(self, isVisible):
        self.__isVisible = isVisible
        if self.__flagEntity:
            self.__flagEntity.show(isVisible)

    def create(self):
        if self.__flagEntity is not None:
            LOG_ERROR('Flags: Wrong usage of offline flags')
            return
        else:
            self.__entityID = BigWorld.createEntity('OfflineFlag', BigWorld.player().spaceID, 0, self.__position, Vector3(0.0, 0.0, 0.0), dict({'flagID': self.__flagID}))
            return


class _CTFConfigReader():
    name = property(lambda self: ('empty' if self.__configSection is None else self.__configSection.name))

    def __init__(self):
        self.__configSection = ResMgr.openSection(_DYNAMIC_OBJECTS_CONFIG_FILE)
        raise self.__configSection is not None or AssertionError
        return

    def readModelParams(self, name):
        if self.__configSection is None:
            return
        else:
            models = self.__configSection['models']
            if models is None:
                return
            for model in models.values():
                if model.name == 'model':
                    modelName = model.readString('name', '')
                    if modelName == name:
                        modelParams = {}
                        for k, v in model.items():
                            modelParams[k] = v.asString

                        return modelParams

            return

    def readRadiusModelName(self, name):
        if self.__configSection is None:
            return
        else:
            radiusModel = self.__configSection.readString(name, '')
            if len(radiusModel) > 0:
                return radiusModel
            return

    def readFirstLvlSection(self, name):
        if self.__configSection is None:
            return
        else:
            return self.__configSection[name]


_g_ctfConfig = _CTFConfigReader()

class _CTFManager():
    isNeedHideAll = property(lambda self: self.__needHideAll)

    @property
    def flagModelName(self):
        return self.__flagModelFile

    @property
    def flagCircleModelName(self):
        return self.__flagCircleModelFile

    @property
    def flagAnimAction(self):
        return self.__flagAnimAction

    def __init__(self):
        self.__flagModelFile = None
        self.__flagCircleModelFile = None
        self.__flagAnimAction = None
        self.__flags = {}
        self.__flagTeams = []
        self.__resourcePoints = {}
        self.__rpGuids = {}
        self.__resourcePointsLock = None
        self.__delayedFlags = []
        self.__evtManager = Event.EventManager()
        self.onFlagSpawning = Event.Event(self.__evtManager)
        self.onFlagSpawnedAtBase = Event.Event(self.__evtManager)
        self.onFlagCapturedByVehicle = Event.Event(self.__evtManager)
        self.onFlagDroppedToGround = Event.Event(self.__evtManager)
        self.onFlagAbsorbed = Event.Event(self.__evtManager)
        self.onFlagRemoved = Event.Event(self.__evtManager)
        self.onCarriedFlagsPositionUpdated = Event.Event(self.__evtManager)
        self.onFlagTeamsUpdated = Event.Event(self.__evtManager)
        self.onResPointIsFree = Event.Event(self.__evtManager)
        self.onResPointCooldown = Event.Event(self.__evtManager)
        self.onResPointCaptured = Event.Event(self.__evtManager)
        self.onResPointCapturedLocked = Event.Event(self.__evtManager)
        self.onResPointBlocked = Event.Event(self.__evtManager)
        self.onOwnVehicleInsideResPoint = Event.Event(self.__evtManager)
        self.onOwnVehicleLockedForResPoint = Event.Event(self.__evtManager)
        self.onResPointAmountChanged = Event.Event(self.__evtManager)
        self.onHideAll = Event.Event(self.__evtManager)
        self.__needHideAll = False
        flagModelParams = _g_ctfConfig.readModelParams(_FLAG_MODEL_NAME)
        if flagModelParams is not None:
            self.__flagModelFile = flagModelParams.get('file')
            self.__flagAnimAction = flagModelParams.get('action')
        flagCircleModelParams = _g_ctfConfig.readModelParams(_FLAG_CIRCLE_MODEL_NAME)
        if flagCircleModelParams is not None:
            self.__flagCircleModelFile = flagCircleModelParams.get('file')
        return

    def addDelayedFlag(self, flag):
        self.__delayedFlags.append(flag)

    def onEnterArena(self):
        for flag in self.__delayedFlags:
            flag.create()

        self.__delayedFlags = []

    def onLeaveArena(self):
        self.__needHideAll = False
        self.__clear()

    def onFlagStateChanged(self, data):
        flagID = data[0]
        prevState = data[1]
        newState = data[2]
        stateParams = data[3:]
        self.__switchFlagToState(flagID, prevState, newState, stateParams)

    def onFlagTeamsReceived(self, data):
        self.__flagTeams = data

    def updateCarriedFlagPositions(self, flagIDs, positions):
        for i, flagID in enumerate(flagIDs):
            if flagID in self.__flags:
                self.__flags[flagID]['minimapPos'] = Vector3(float(positions[i * 2]), 0.0, float(positions[i * 2 + 1]))

        self.onCarriedFlagsPositionUpdated(flagIDs)

    def getFlags(self):
        return sorted(self.__flags.iteritems(), key=operator.itemgetter(0))

    def getFlagInfo(self, flagID):
        return self.__flags[flagID]

    def isFlagBearer(self, vehicleID):
        for flag in self.__flags.itervalues():
            if flag['vehicle'] == vehicleID:
                return True

        return False

    def getFlagMinimapPos(self, flagID):
        if flagID not in self.__flags:
            return
        else:
            flag = self.__flags[flagID]
            vehicleID = flag['vehicle']
            if vehicleID is not None:
                vehicle = self.__getVehicle(vehicleID)
                if vehicle is not None:
                    return vehicle.position
            return flag['minimapPos']

    def hideAll(self):
        self.__needHideAll = True
        for flag in self.__flags.itervalues():
            flag['flag'].show(False)

        self.onHideAll()

    def __switchFlagToState(self, flagID, prevState, newState, stateParams):
        if flagID not in self.__flags:
            self.__flags[flagID] = {'state': None,
             'prevState': None,
             'minimapPos': None,
             'vehicle': None,
             'respawnTime': 0.0,
             'flag': None,
             'team': self.__flagTeams[flagID]}
        flag = self.__flags[flagID]
        flag['state'] = newState
        flag['prevState'] = prevState
        flagTeam = flag['team']
        if newState == FLAG_STATE.WAITING_FIRST_SPAWN:
            respawnTime = stateParams[0]
            flag['respawnTime'] = respawnTime
            self.onFlagSpawning(flagID, respawnTime)
        elif newState == FLAG_STATE.ON_SPAWN:
            flagPos = Vector3(*stateParams[0])
            flag['vehicle'] = None
            flag['minimapPos'] = flagPos
            flag['respawnTime'] = 0.0
            self.__flagModelSet(flagID, flagPos, True)
            self.onFlagSpawnedAtBase(flagID, flagTeam, flagPos)
        elif newState == FLAG_STATE.ON_VEHICLE:
            vehicleID = stateParams[0]
            flag['vehicle'] = vehicleID
            flag['respawnTime'] = 0.0
            self.__flagModelSet(flagID, None, False)
            vehicle = self.__getVehicle(vehicleID)
            if vehicle is not None:
                flag['minimapPos'] = vehicle.position
            self.onFlagCapturedByVehicle(flagID, flagTeam, vehicleID)
        elif newState == FLAG_STATE.ON_GROUND:
            loserVehicleID = stateParams[0]
            flagPos = Vector3(*stateParams[1])
            respawnTime = stateParams[2]
            flag['vehicle'] = None
            flag['respawnTime'] = respawnTime
            flag['minimapPos'] = flagPos
            self.__flagModelSet(flagID, flagPos, True)
            self.onFlagDroppedToGround(flagID, flagTeam, loserVehicleID, flagPos, respawnTime)
        elif newState == FLAG_STATE.ABSORBED:
            vehicleID = stateParams[0]
            respawnTime = stateParams[1]
            flag['vehicle'] = None
            flag['respawnTime'] = respawnTime
            self.__flagModelSet(flagID, None, False)
            self.onFlagAbsorbed(flagID, flagTeam, vehicleID, respawnTime)
        elif newState == FLAG_STATE.UNKNOWN:
            vehicleID = flag['vehicle']
            self.__flagModelSet(flagID, None, False)
            flag['vehicle'] = None
            flag['respawnTime'] = 0.0
            flag['minimapPos'] = None
            self.onFlagRemoved(flagID, flagTeam, vehicleID)
        return

    def __flagModelSet(self, flagID, flagPos, isVisible):
        if flagID not in self.__flags:
            return
        else:
            flagEntity = self.__flags[flagID]['flag']
            if flagEntity is None:
                self.__flags[flagID]['flag'] = Flag(flagPos, isVisible, flagID)
            else:
                flagEntity.setPosition(flagPos)
                flagEntity.show(isVisible)
            return

    def __clear(self):
        for flag in self.__flags.itervalues():
            if flag is not None:
                flag['flag'].destroy()

        self.__delayedFlags = []
        self.__flags.clear()
        self.__flagTeams = ()
        self.__evtManager.clear()
        self.__resourcePoints.clear()
        self.__rpGuids.clear()
        return

    def __getVehicle(self, vehicleID):
        return BigWorld.entities.get(vehicleID)

    def onResourcePointStateChanged(self, data):
        pointID = data[0]
        prevState = data[1]
        newState = data[2]
        stateParams = data[3:]
        self.__switchResourcePointToState(pointID, prevState, newState, stateParams)

    def onOwnVehicleInsideRP(self, pointInfo):
        pointID, pointState = pointInfo if pointInfo else (None, None)
        if pointID is not None:
            point = self.__resourcePoints[pointID]
            point['isPlayerCapture'] = True
            prevState = point['state']
            if prevState != pointState:
                point['state'] = pointState
                point['prevState'] = prevState
        else:
            _, point = findFirst(lambda (pID, p): p['isPlayerCapture'], self.__resourcePoints.iteritems(), (None, None))
            if point is None:
                LOG_ERROR('Vehicle left unknown point!')
                return
            point['isPlayerCapture'] = False
        self.onOwnVehicleInsideResPoint(pointID)
        return

    def onOwnVehicleLockedForRP(self, unlockTime):
        self.__resourcePointsLock = unlockTime
        self.onOwnVehicleLockedForResPoint(unlockTime)

    def onResourcePointAmountChanged(self, pointID, amount):
        point = self.__resourcePoints.get(pointID, None)
        if point is not None:
            point['amount'] = amount
            self.onResPointAmountChanged(pointID, amount, point['totalAmount'])
        return

    def getResourcePoints(self):
        return sorted(self.__resourcePoints.iteritems(), key=operator.itemgetter(0))

    def getResourcePointLock(self):
        return self.__resourcePointsLock

    def registerResourcePointModel(self, rpModel):
        if not hasattr(rpModel, 'guid'):
            raise AssertionError
            pointID = self.__rpGuids.get(rpModel.guid)
            raise pointID is not None or AssertionError
            rp = pointID in self.__resourcePoints and self.__resourcePoints[pointID]
            rp['model'] = rpModel
        return

    def unregisterResourcePointModel(self, rpModel):
        if not hasattr(rpModel, 'guid'):
            raise AssertionError
            pointID = self.__rpGuids.get(rpModel.guid)
            rp = pointID in self.__resourcePoints and self.__resourcePoints[pointID]
            rp['model'] = None
        return

    def updateRegisteredResourcePointModel(self, rpModel):
        if not hasattr(rpModel, 'guid'):
            raise AssertionError
            pointID = self.__rpGuids.get(rpModel.guid)
            if pointID in self.__resourcePoints:
                rp = self.__resourcePoints[pointID]
                rp['state'] == RESOURCE_POINT_STATE.FREE and rpModel.playEffect()

    def __getResourcePointFromArena(self, pointID):
        arena = BigWorld.player().arena
        if arena is None:
            return
        else:
            arenaType = arena.arenaType
            if hasattr(arenaType, 'resourcePoints'):
                resourcePoints = arenaType.resourcePoints
                if pointID < len(resourcePoints):
                    return resourcePoints[pointID]
            return

    def __switchResourcePointToState(self, pointID, prevState, newState, stateParams):
        if pointID not in self.__resourcePoints:
            pointCfg = self.__getResourcePointFromArena(pointID)
            if pointCfg is not None:
                if 'guid' in pointCfg:
                    self.__rpGuids[pointCfg['guid']] = pointID
            totalAmount = pointCfg['amount'] if pointCfg is not None else 0
            position = pointCfg['position'] if pointCfg is not None else None
            self.__resourcePoints[pointID] = {'state': None,
             'prevState': None,
             'team': 0,
             'model': None,
             'minimapPos': position,
             'cooldownTime': None,
             'amount': 0,
             'totalAmount': totalAmount,
             'isPlayerCapture': False}
        resourcePoint = self.__resourcePoints[pointID]
        resourcePoint['state'] = newState
        resourcePoint['prevState'] = prevState
        resourcePoint['cooldownTime'] = None
        resourcePoint['team'] = 0
        if newState == RESOURCE_POINT_STATE.FREE:
            self.__playResourcePointEffect(resourcePoint)
            self.onResPointIsFree(pointID)
        elif newState == RESOURCE_POINT_STATE.COOLDOWN:
            self.__stopResourcePointEffect(resourcePoint)
            serverTime = stateParams[0]
            resourcePoint['cooldownTime'] = serverTime
            self.onResPointCooldown(pointID, serverTime)
        elif newState == RESOURCE_POINT_STATE.CAPTURED:
            self.__stopResourcePointEffect(resourcePoint)
            team = stateParams[0]
            resourcePoint['team'] = team
            self.onResPointCaptured(pointID, team)
        elif newState == RESOURCE_POINT_STATE.CAPTURED_LOCKED:
            self.__stopResourcePointEffect(resourcePoint)
            team = stateParams[0]
            resourcePoint['team'] = team
            self.onResPointCapturedLocked(pointID, team)
        elif newState == RESOURCE_POINT_STATE.BLOCKED:
            self.__stopResourcePointEffect(resourcePoint)
            self.onResPointBlocked(pointID)
        return

    @staticmethod
    def __playResourcePointEffect(resourcePoint):
        if resourcePoint['model'] is None:
            return
        else:
            resourcePoint['model'].playEffect()
            return

    @staticmethod
    def __stopResourcePointEffect(resourcePoint):
        if resourcePoint['model'] is None:
            return
        else:
            resourcePoint['model'].stopEffect()
            return


g_ctfManager = _CTFManager()

class _GlobalHideListener():

    def __init__(self, hideMethod):
        self.__hideMethod = hideMethod
        g_ctfManager.onHideAll += self.__hide

    def __del__(self):
        g_ctfManager.onHideAll -= self.__hide
        self.__hideMethod = None
        return

    def __hide(self):
        self.__hideMethod()


class _CTFCheckPoint():

    def __init__(self, radiusModelName):
        self.__terrainSelectedArea = None
        self.__fakeModel = None
        self.__hideListener = None
        self.__radiusModelName = _g_ctfConfig.readRadiusModelName(radiusModelName)
        if self.__radiusModelName is None:
            LOG_ERROR('%s: unable to load value from "%s" section' % (_g_ctfConfig.name, radiusModelName))
        return

    def __del__(self):
        self.__hideListener = None
        if self.__fakeModel is not None:
            BigWorld.delModel(self.__fakeModel)
            self.__fakeModel = None
        self.__terrainSelectedArea = None
        self.__radiusModelName = None
        return

    def _createTerrainSelectedArea(self, position, size, overTerrainHeight, color):
        if self.__radiusModelName is None:
            return
        elif g_ctfManager.isNeedHideAll:
            return
        else:
            self.__fakeModel = BigWorld.Model('objects/fake_model.model')
            self.__fakeModel.position = position
            BigWorld.addModel(self.__fakeModel, BigWorld.player().spaceID)
            self.__fakeModel.addMotor(BigWorld.Servo(Math.Matrix(self.__fakeModel.matrix)))
            rootNode = self.__fakeModel.node('')
            self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
            self.__terrainSelectedArea.setup(self.__radiusModelName, Vector2(size, size), overTerrainHeight, color)
            rootNode.attach(self.__terrainSelectedArea)
            self.__hideListener = _GlobalHideListener(self.__hideCheckPoint)
            return

    def __hideCheckPoint(self):
        if self.__fakeModel is not None:
            self.__fakeModel.visible = False
        return


class _FlagResourceLoader():

    class __LoadTask:
        pass

    def __init__(self):
        self.__tasks = {}

    def startLoadTask(self, resourceList, callbackFn):
        task = self.__LoadTask()
        self.__tasks[task] = callbackFn
        BigWorld.loadResourceListBG(resourceList, partial(self.__onResourcesLoaded, task))
        return task

    def stopLoadTask(self, task):
        if task in self.__tasks:
            del self.__tasks[task]

    def __onResourcesLoaded(self, task, resourceRefs):
        if task not in self.__tasks:
            return
        callbackFn = self.__tasks[task]
        del self.__tasks[task]
        callbackFn(resourceRefs)


_g_resLoader = _FlagResourceLoader()

class _CTFPointFlag():

    def __init__(self, flagModelName, flagPos):
        self.__flagModelFile = None
        self.__flagModel = None
        self.__flagAnimAction = None
        self.__flagPos = flagPos
        self.__loadTask = None
        self.__hideListener = None
        flagModelParams = _g_ctfConfig.readModelParams(flagModelName)
        if flagModelParams is not None:
            self.__flagModelFile = flagModelParams.get('file')
            self.__flagAnimAction = flagModelParams.get('action')
        if self.__flagModelFile is None:
            LOG_ERROR('%s: can\'t find the "%s" model.' % (_g_ctfConfig.name, flagModelName))
        return

    def __del__(self):
        self.__hideListener = None
        if self.__loadTask is not None:
            _g_resLoader.stopLoadTask(self.__loadTask)
            self.__loadTask = None
        if self.__flagModel is not None:
            BigWorld.delModel(self.__flagModel)
            self.__flagModel = None
        self.__flagModelFile = None
        self.__flagAnimAction = None
        self.__flagPos = None
        return

    def _createFlag(self, applyOverlay = False):
        if g_ctfManager.isNeedHideAll:
            return
        else:
            raise self.__flagModelFile is not None or AssertionError
            self.__loadTask = _g_resLoader.startLoadTask((self.__flagModelFile,), partial(self.__onModelLoaded, applyOverlay))
            return

    def __onModelLoaded(self, applyOverlay, resourceRefs):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load flag model %s' % (resourceRefs.failedIDs,))
        else:
            model = resourceRefs[self.__flagModelFile]
            if not model is not None:
                raise AssertionError
                model.position = self.__flagPos
                BigWorld.addModel(model, BigWorld.player().spaceID)
                BigWorld.wg_applyOverlayToModel(model, applyOverlay)
                self.__flagModel = model
                if self.__flagAnimAction is not None:
                    try:
                        animAction = model.action(self.__flagAnimAction)
                        animAction()
                    except:
                        LOG_WARNING('Unable to start "%s" animation action for model "%s"' % (self.__flagAnimAction, self.__flagModelFile))

                g_ctfManager.isNeedHideAll and self.__hidePointFlag()
            else:
                self.__hideListener = _GlobalHideListener(self.__hidePointFlag)
        return

    def __hidePointFlag(self):
        if self.__flagModel is not None:
            self.__flagModel.visible = False
        return


class _CTFResourcePointModel():

    def __init__(self, pointModelName, effectsSectionName):
        self.__modelFile = None
        self.__model = None
        self.__effectsTimeLine = None
        self.__effectsPlayer = None
        self.__loadTask = None
        self.__hideListener = None
        g_ctfManager.registerResourcePointModel(self)
        modelParams = _g_ctfConfig.readModelParams(pointModelName)
        if modelParams is not None:
            self.__modelFile = modelParams.get('file')
        if self.__modelFile is None:
            LOG_ERROR('%s: can\'t find the "%s" model.' % (_g_ctfConfig.name, pointModelName))
        effectsSection = _g_ctfConfig.readFirstLvlSection(effectsSectionName)
        if effectsSection is not None:
            self.__effectsTimeLine = effectsFromSection(effectsSection)
        return

    def __del__(self):
        self.__hideListener = None
        if self.__loadTask is not None:
            _g_resLoader.stopLoadTask(self.__loadTask)
            self.__loadTask = None
        g_ctfManager.unregisterResourcePointModel(self)
        if self.__effectsPlayer is not None:
            self.stopEffect()
            self.__effectsPlayer = None
        self.__effectsTimeLine = None
        if self.__model is not None:
            BigWorld.delModel(self.__model)
            self.__model = None
        self.__modelFile = None
        return

    def _createPoint(self):
        if g_ctfManager.isNeedHideAll:
            return
        else:
            raise self.__modelFile is not None or AssertionError
            self.__loadTask = _g_resLoader.startLoadTask((self.__modelFile,), self.__onModelLoaded)
            return

    def __onModelLoaded(self, resourceRefs):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load model %s' % (resourceRefs.failedIDs,))
        else:
            model = resourceRefs[self.__modelFile]
            if not model is not None:
                raise AssertionError
                model.position = self.position
                roll, pitch, yaw = self.direction
                model.rotate(roll, (0.0, 0.0, 1.0))
                model.rotate(pitch, (1.0, 0.0, 0.0))
                model.rotate(yaw, (0.0, 1.0, 0.0))
                BigWorld.addModel(model, BigWorld.player().spaceID)
                BigWorld.wg_applyOverlayToModel(model, False)
                self.__model = model
                g_ctfManager.updateRegisteredResourcePointModel(self)
                g_ctfManager.isNeedHideAll and self.__hideResPointFlag()
            else:
                self.__hideListener = _GlobalHideListener(self.__hideResPointFlag)
        return

    def __hideResPointFlag(self):
        if self.__model is not None:
            self.__model.visible = False
        self.stopEffect()
        return

    def playEffect(self):
        if self.__effectsPlayer is not None:
            return
        elif self.__model is None:
            return
        else:
            if self.__effectsTimeLine is not None:
                self.__effectsPlayer = EffectsListPlayer(self.__effectsTimeLine.effectsList, self.__effectsTimeLine.keyPoints)
                self.__effectsPlayer.play(self.__model)
            return

    def stopEffect(self):
        if self.__effectsPlayer is None:
            return
        else:
            self.__effectsPlayer.stop()
            self.__effectsPlayer = None
            return


class _UDOAttributeChecker():
    isAttrCheckFailed = property(lambda self: self.__isCheckFailed)

    def __init__(self):
        self.__isCheckFailed = False

    def checkAttribute(self, attributeName):
        self.__isCheckFailed = True
        attribute = getattr(self, attributeName, None)
        raise attribute is not None and len(attribute) > 0 or AssertionError
        self.__isCheckFailed = False
        return
