# Embedded file name: scripts/client/CTFManager.py
import BigWorld
import Event
import ResMgr
from functools import partial
from debug_utils import *
from constants import FLAG_STATE
from Math import Vector2, Vector3
_DYNAMIC_OBJECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_FLAG_MODEL_NAME = 'ctf_flag'

class _CTFConfigReader:
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


_g_ctfConfig = _CTFConfigReader()

class _CTFManager:

    def __init__(self):
        self.__flagModelFile = None
        self.__flagAnimAction = None
        self.__flags = {}
        self.__vehicles = None
        self.__evtManager = Event.EventManager()
        self.onFlagSpawnedAtBase = Event.Event(self.__evtManager)
        self.onFlagCapturedByVehicle = Event.Event(self.__evtManager)
        self.onFlagDroppedToGround = Event.Event(self.__evtManager)
        self.onFlagAbsorbed = Event.Event(self.__evtManager)
        self.onCarriedFlagsPositionUpdated = Event.Event(self.__evtManager)
        flagModelParams = _g_ctfConfig.readModelParams(_FLAG_MODEL_NAME)
        if flagModelParams is not None:
            self.__flagModelFile = flagModelParams.get('file')
            self.__flagAnimAction = flagModelParams.get('action')
        return

    def onEnterArena(self):
        self.__vehicles = BigWorld.player().arena.vehicles

    def onLeaveArena(self):
        self.__clear()

    def onFlagStateChanged(self, data):
        flagID = data[0]
        prevState = data[1]
        newState = data[2]
        stateParams = data[3:]
        self.__switchFlagToState(flagID, prevState, newState, stateParams)

    def updateCarriedFlagPositions(self, flagIDs, positions):
        for i, flagID in enumerate(flagIDs):
            if flagID in self.__flags:
                self.__flags[flagID]['minimapPos'] = Vector3(float(positions[i * 2]), 0.0, float(positions[i * 2 + 1]))

        self.onCarriedFlagsPositionUpdated(flagIDs)

    def getFlags(self):
        return self.__flags.keys()

    def getFlagInfo(self, flagID):
        return self.__flags.get(flagID, None)

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

    def __switchFlagToState(self, flagID, prevState, newState, stateParams):
        if flagID not in self.__flags:
            self.__flags[flagID] = {'state': None,
             'prevState': None,
             'minimapPos': None,
             'vehicle': None,
             'respawnTime': 0.0,
             'model': None}
        flag = self.__flags[flagID]
        flag['state'] = newState
        flag['prevState'] = prevState
        if newState == FLAG_STATE.ON_SPAWN:
            flagPos = Vector3(*stateParams[0])
            flag['vehicle'] = None
            flag['minimapPos'] = flagPos
            flag['respawnTime'] = 0.0
            self.__flagModelSet(flagID, flagPos, True)
            self.onFlagSpawnedAtBase(flagID, flagPos)
        elif newState == FLAG_STATE.ON_VEHICLE:
            vehicleID = stateParams[0]
            flag['vehicle'] = vehicleID
            flag['respawnTime'] = 0.0
            self.__flagModelSet(flagID, None, False)
            vehicle = self.__getVehicle(vehicleID)
            if vehicle is not None:
                flag['minimapPos'] = vehicle.position
            self.onFlagCapturedByVehicle(flagID, vehicleID)
        elif newState == FLAG_STATE.ON_GROUND:
            loserVehicleID = stateParams[0]
            flagPos = Vector3(*stateParams[1])
            respawnTime = stateParams[2]
            flag['vehicle'] = None
            flag['respawnTime'] = respawnTime
            flag['minimapPos'] = flagPos
            self.__flagModelSet(flagID, flagPos, True)
            self.onFlagDroppedToGround(flagID, loserVehicleID, flagPos, respawnTime)
        elif newState == FLAG_STATE.ABSORBED:
            vehicleID = stateParams[0]
            respawnTime = stateParams[1]
            flag['vehicle'] = None
            flag['respawnTime'] = respawnTime
            self.__flagModelSet(flagID, None, False)
            self.onFlagAbsorbed(flagID, vehicleID, respawnTime)
        return

    def __createFlagAt(self, flagID, position, isVisible):
        if self.__flagModelFile is None:
            LOG_ERROR('CTFManager: flag model is not specified')
            return
        else:
            BigWorld.loadResourceListBG((self.__flagModelFile,), partial(self.__onFlagModelLoaded, flagID, position, isVisible))
            return

    def __onFlagModelLoaded(self, flagID, position, isVisible, resourceRefs):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load flag model %s' % (resourceRefs.failedIDs,))
        else:
            model = resourceRefs[self.__flagModelFile]
            if position is not None:
                model.position = position
            BigWorld.addModel(model, BigWorld.player().spaceID)
            BigWorld.wgAddEdgeDetectModel(model, 3, 2)
            BigWorld.wgEdgeDetectModelSetVisible(model, isVisible)
            if self.__flagAnimAction is not None:
                try:
                    animAction = model.action(self.__flagAnimAction)
                    animAction()
                except:
                    pass

            self.__flags[flagID]['model'] = model
        return

    def __removeFlag(self, flagID):
        if flagID not in self.__flags:
            return
        else:
            flagModel = self.__flags[flagID]['model']
            if flagModel is not None:
                BigWorld.wgDelEdgeDetectModel(flagModel)
                BigWorld.delModel(self.__flags[flagID]['model'])
            del self.__flags[flagID]
            return

    def __clear(self):
        for flag in self.__flags.itervalues():
            flagModel = flag['model']
            if flagModel is not None:
                BigWorld.wgDelEdgeDetectModel(flagModel)
                BigWorld.delModel(flagModel)
                flag['model'] = None

        self.__flags.clear()
        self.__vehicles = None
        self.__evtManager.clear()
        return

    def __getVehicle(self, vehicleID):
        if self.__vehicles is None:
            return
        elif vehicleID not in self.__vehicles:
            return
        else:
            return BigWorld.entities.get(vehicleID)

    def __flagModelSet(self, flagID, flagPos, isVisible):
        if flagID not in self.__flags:
            return
        else:
            flagModel = self.__flags[flagID]['model']
            if flagModel is None:
                self.__createFlagAt(flagID, flagPos, isVisible)
            else:
                BigWorld.wgEdgeDetectModelSetVisible(flagModel, isVisible)
                if flagPos is not None:
                    flagModel.position = flagPos
            return


g_ctfManager = _CTFManager()

class _CTFCheckPoint:

    def __init__(self, radiusModelName):
        self.__terrainSelectedArea = None
        self.__fakeModel = None
        self.__radiusModelName = _g_ctfConfig.readRadiusModelName(radiusModelName)
        if self.__radiusModelName is None:
            LOG_ERROR('%s: unable to load value from "%s" section' % (_g_ctfConfig.name, radiusModelName))
        return

    def __del__(self):
        if self.__fakeModel is not None:
            BigWorld.delModel(self.__fakeModel)
            self.__fakeModel = None
        self.__terrainSelectedArea = None
        self.__radiusModelName = None
        return

    def _createTerrainSelectedArea(self, position, size, overTerrainHeight, color):
        if self.__radiusModelName is None:
            return
        else:
            self.__fakeModel = BigWorld.Model('objects/fake_model.model')
            self.__fakeModel.position = position
            BigWorld.addModel(self.__fakeModel, BigWorld.player().spaceID)
            rootNode = self.__fakeModel.node('')
            self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
            self.__terrainSelectedArea.setup(self.__radiusModelName, Vector2(size, size), overTerrainHeight, color)
            rootNode.attach(self.__terrainSelectedArea)
            return


class _CTFPointFlag:

    def __init__(self, flagModelName, flagPos):
        self.__flagModelFile = None
        self.__flagModel = None
        self.__flagAnimAction = None
        self.__flagPos = flagPos
        flagModelParams = _g_ctfConfig.readModelParams(flagModelName)
        if flagModelParams is not None:
            self.__flagModelFile = flagModelParams.get('file')
            self.__flagAnimAction = flagModelParams.get('action')
        if self.__flagModelFile is None:
            LOG_ERROR('%s: can\'t find the "%s" model.' % (_g_ctfConfig.name, flagModelName))
        return

    def __del__(self):
        if self.__flagModel is not None:
            BigWorld.delModel(self.__flagModel)
            self.__flagModel = None
        self.__flagModelFile = None
        self.__flagAnimAction = None
        self.__flagPos = None
        return

    def _createFlag(self):
        raise self.__flagModelFile is not None or AssertionError
        BigWorld.loadResourceListBG((self.__flagModelFile,), self.__onModelLoaded)
        return

    def __onModelLoaded(self, resourceRefs):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load flag model %s' % (resourceRefs.failedIDs,))
        else:
            model = resourceRefs[self.__flagModelFile]
            raise model is not None or AssertionError
            model.position = self.__flagPos
            BigWorld.addModel(model, BigWorld.player().spaceID)
            self.__flagModel = model
            if self.__flagAnimAction is not None:
                try:
                    animAction = model.action(self.__flagAnimAction)
                    animAction()
                except:
                    LOG_WARNING('Unable to start "%s" animation action for model "%s"' % (self.__flagAnimAction, self.__flagModelFile))

        return
