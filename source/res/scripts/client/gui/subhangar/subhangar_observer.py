# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/subhangar/subhangar_observer.py
import logging
from collections import namedtuple
from functools import partial
import typing
import CGF
import Hangar
import Math
import ResMgr
from cgf_components.hangar_camera_manager import HangarCameraManager
from frameworks.state_machine import BaseStateObserver
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, CameraMover
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import TankPartIndexes
if typing.TYPE_CHECKING:
    from typing import Union, Iterable, Sized, Optional
    from frameworks.state_machine import StateEvent
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.lobby_state_machine.states import LobbyState
    from gui.shared.events import NavigationEvent
_logger = logging.getLogger(__name__)
_CONFIG_PATH = 'spaces/subhangars.xml'
_GroupConfig = namedtuple('_GroupConfig', ('name', 'defaultCamera'))
T = typing.TypeVar('T')
SubhangarActivationConfig = namedtuple('SubhangarActivationConfig', 'subHangar, state, cameraMover')

def hangarVehicleAABB():
    hangarSpace = dependency.instance(IHangarSpace)
    if not hangarSpace:
        return None
    else:
        appearance = hangarSpace.getVehicleEntityAppearance()
        if not appearance or not appearance.collisions:
            return None
        collisions = appearance.collisions
        enclosingAABB = (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0))
        for index in TankPartIndexes.ALL:
            aabb = collisions.getBoundingBox(index)
            enclosingAABB[0].x = min(enclosingAABB[0].x, aabb[0].x)
            enclosingAABB[0].y = min(enclosingAABB[0].y, aabb[0].y)
            enclosingAABB[0].z = min(enclosingAABB[0].z, aabb[0].z)
            enclosingAABB[1].x = max(enclosingAABB[1].x, aabb[1].x)
            enclosingAABB[1].y = max(enclosingAABB[1].y, aabb[1].y)
            enclosingAABB[1].z = max(enclosingAABB[1].z, aabb[1].z)

        return enclosingAABB


def selectItemByTankSize(tankSizeLowerBounds, items, default=None):
    if not tankSizeLowerBounds:
        _logger.error('tankSizeLowerBounds cannot be empty or None.')
    if not items:
        _logger.error('items cannot be empty or None.')
    aabb = hangarVehicleAABB()
    if not aabb:
        if default:
            return default
        return items[-1]
    maxDimension = max(abs(aabb[1].x - aabb[0].x), abs(aabb[1].y - aabb[0].y), abs(aabb[1].z - aabb[0].z))
    if len(tankSizeLowerBounds) != len(items):
        _logger.error('tankSizeLowerBounds (%r) and items (%r) have to be equally sized.', tankSizeLowerBounds, items)
    sizesWithItems = list(zip(tankSizeLowerBounds, items))
    sizesWithItems.sort(key=lambda sizeWithItem: sizeWithItem[0])
    largestPassingItem = sizesWithItems[0][1]
    for tankSizeLowerBound, item in sizesWithItems:
        if maxDimension < tankSizeLowerBound:
            break
        largestPassingItem = item

    return largestPassingItem


class _SubhangarConfig(object):

    def __init__(self, path):
        self.__stateGroupsToGroups = {}
        self._parseConfig(path)

    def getGroups(self, stateGroups):
        groups = set()
        for stateGroup in stateGroups:
            groups.update(self.__stateGroupsToGroups.get(stateGroup, ()))

        return groups

    def _getStates(self, rawString):
        groupStates = rawString.split()
        for state in groupStates:
            yield state.strip()

    def _parseConfig(self, path):
        xml = ResMgr.openSection(path)
        for groupXml in xml.values():
            groupName = groupXml.name
            group = _GroupConfig(groupName, groupXml.readString('defaultCamera'))
            for stateGroupRawString in groupXml.readStrings('states'):
                for state in self._getStates(stateGroupRawString):
                    if state not in self.__stateGroupsToGroups:
                        self.__stateGroupsToGroups[state] = []
                    self.__stateGroupsToGroups[state].append(group)


class SubhangarObserver(BaseStateObserver):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, lsm, path=_CONFIG_PATH):
        super(SubhangarObserver, self).__init__()
        self.__activatedSubHangars = []
        self.__subHangarsToActivate = set()
        self.__subHangarsToDeactivate = set()
        self.__config = _SubhangarConfig(path)
        self.__callbackDelayer = CallbackDelayer()
        self.__lsm = lsm
        lsm.onVisibleRouteChanged += self.__navigationsFinished
        self.__hangarSpace.onSpaceCreate += self.__navigationsFinished

    def isObservingState(self, state):
        return isinstance(state, SubhangarStateGroupConfigProvider)

    def clear(self):
        self.__lsm.onVisibleRouteChanged -= self.__navigationsFinished
        self.__lsm = None
        self.__callbackDelayer.destroy()
        self.__activatedSubHangars = []
        self.__subHangarsToActivate = set()
        self.__subHangarsToDeactivate = set()
        return

    def onEnterState(self, state, event):
        config = state.getSubhangarStateGroupConfig()
        subhangarStateGroups = (room.value for room in config.stateGroups)
        subHangars = self.__config.getGroups(subhangarStateGroups)
        for subHangar in subHangars:
            _logger.debug('Queued %s for activation due to entering %r state', subHangar, state)
            subhangarConfig = SubhangarActivationConfig(subHangar, state, config.cameraMover)
            self.__subHangarsToActivate.add(subhangarConfig)
            if subhangarConfig in self.__subHangarsToDeactivate:
                self.__subHangarsToDeactivate.remove(subhangarConfig)

    def onExitState(self, state, event):
        for config in self.__activatedSubHangars:
            if state is config.state:
                _logger.debug('Queued %s for deactivation due to exiting %r state', config.subHangar, state)
                self.__subHangarsToDeactivate.add(config)

        self.__subHangarsToActivate = set((config for config in self.__subHangarsToActivate if config.state is not state))

    def __navigationsFinished(self, *_):
        if self.__hangarSpace.spaceInited:
            self.__configureSubHangars()
            self.__subHangarsToActivate.clear()
            self.__subHangarsToDeactivate.clear()
            self.__hangarSpace.onSpaceCreate -= self.__navigationsFinished

    def __configureSubHangars(self):
        hangarSpaceId = self.__hangarSpace.spaceID
        if not hangarSpaceId:
            _logger.debug('hangarSpaceID is None')
            return
        for config in self.__subHangarsToDeactivate:
            if config in self.__activatedSubHangars:
                _logger.info('Deactivating %s', config.subHangar)
                Hangar.deactivateGroup(hangarSpaceId, config.subHangar.name)

        self.__activatedSubHangars = [ subhangarActivationConfig for subhangarActivationConfig in self.__activatedSubHangars if subhangarActivationConfig not in self.__subHangarsToDeactivate ]
        for config in self.__subHangarsToActivate:
            if config not in self.__activatedSubHangars:
                _logger.info('Activating %s.', config.subHangar)
                Hangar.activateGroup(hangarSpaceId, config.subHangar.name)
                self.__activatedSubHangars.append(config)

        cameraManager = CGF.getManager(hangarSpaceId, HangarCameraManager)
        if cameraManager and (self.__subHangarsToDeactivate or self.__subHangarsToActivate):
            configWithCameras = [ config for config in self.__activatedSubHangars if config.subHangar.defaultCamera ]
            if configWithCameras:
                subHangar, _, cameraMover = configWithCameras[-1]
                _logger.debug('Switching to %s camera (group: %s).', subHangar.defaultCamera, subHangar)
                cameraManager.clearCurrentCameraComponents()
                self.__callbackDelayer.clearCallbacks()
                self.__callbackDelayer.delayCallback(0, partial(self.__switchToCameraWhenLoaded, subHangar.defaultCamera, cameraMover))
            else:
                self.__callbackDelayer.clearCallbacks()
                _logger.debug('No camera specified for current set of rooms. Returning camera to tank.')
                cameraManager.switchToTank()

    def __switchToCameraWhenLoaded(self, cameraName, cameraMover):
        hangarSpaceId = self.__hangarSpace.spaceID
        cameraManager = CGF.getManager(hangarSpaceId, HangarCameraManager)
        if not cameraManager or not cameraManager.cameraExists(cameraName):
            return 0
        else:
            cameraMover.moveCamera(cameraManager, cameraName)
            return None
