# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/subhangar/subhangar_observer.py
import logging
from collections import namedtuple
import CGF
import Hangar
import Math
import ResMgr
import typing
from shared_utils import first
from cgf_components.hangar_camera_manager import HangarCameraSystem
from frameworks_common.state_machine import BaseStateObserver
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import getVehicleAABB, selectItemByTankSize as selectItemByTankSizeBase
if typing.TYPE_CHECKING:
    from typing import Union, Iterable, Sized, Optional
    from frameworks_common.state_machine import StateEvent
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.lobby_state_machine.states import LobbyState
    from gui.shared.events import NavigationEvent
_logger = logging.getLogger(__name__)
_CONFIG_PATH = 'spaces/subhangars.xml'
_GroupConfig = namedtuple('_GroupConfig', ('name', 'defaultCamera'))
T = typing.TypeVar('T')
SubhangarActivationConfig = namedtuple('SubhangarActivationConfig', 'subHangar, state, cameraMover, environmentName')

def hangarVehicleAABB():
    if not dependency.isConfigured():
        return None
    else:
        hangarSpace = dependency.instance(IHangarSpace)
        if not hangarSpace:
            return None
        appearance = hangarSpace.getVehicleEntityAppearance()
        return None if not appearance or not appearance.collisions else getVehicleAABB(appearance.collisions)


def selectItemByTankSize(tankSizeLowerBounds, items, default=None):
    return selectItemByTankSizeBase(tankSizeLowerBounds, items, default, hangarVehicleAABB())


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
        self.__lsm = lsm
        lsm.onVisibleRouteChanged += self.__navigationsFinished
        self.__hangarSpace.onSpaceCreate += self.__navigationsFinished

    def isObservingState(self, state):
        return isinstance(state, SubhangarStateGroupConfigProvider)

    def clear(self):
        self.__lsm.onVisibleRouteChanged -= self.__navigationsFinished
        self.__lsm = None
        self.__hangarSpace.onSpaceCreate -= self.__navigationsFinished
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
            subhangarConfig = SubhangarActivationConfig(subHangar, state, config.cameraMover, config.environmentName)
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
        else:
            self.__hangarSpace.onSpaceCreate += self.__navigationsFinished

    def __configureSubHangars(self):
        hangarSpaceId = self.__hangarSpace.spaceID
        if not hangarSpaceId:
            _logger.debug('hangarSpaceID is None')
            return
        else:
            if self.__hangarSpace.space is not None:
                space = self.__hangarSpace.space.getSpace()
                activatedEnvironments = [ config.environmentName for config in self.__activatedSubHangars if config.environmentName and config not in self.__subHangarsToDeactivate ]
                environmentsToActivate = [ config.environmentName for config in self.__subHangarsToActivate if config.environmentName and config not in self.__activatedSubHangars ]
                environmentsToDeactivate = [ config.environmentName for config in self.__subHangarsToDeactivate if config.environmentName and config in self.__activatedSubHangars ]
                if environmentsToActivate:
                    space.setEnvironment(first(environmentsToActivate))
                if not activatedEnvironments and not environmentsToActivate and environmentsToDeactivate:
                    space.resetEnvironment()
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

            cameraManager = CGF.getSystem(hangarSpaceId, HangarCameraSystem)
            if cameraManager and (self.__subHangarsToDeactivate or self.__subHangarsToActivate):
                configWithCameras = [ config for config in self.__activatedSubHangars if config.subHangar.defaultCamera ]
                if configWithCameras:
                    subHangar, _, cameraMover, _ = configWithCameras[-1]
                    _logger.debug('Switching to %s camera (group: %s).', subHangar.defaultCamera, subHangar)
                    if not cameraManager.cameraExists(subHangar.defaultCamera):
                        cameraMover.moveCameraFailed()
                    else:
                        cameraMover.moveCamera(cameraManager, subHangar.defaultCamera)
                else:
                    _logger.debug('No camera specified for current set of rooms. Returning camera to tank.')
                    if self.__hangarSpace.spaceInited:
                        cameraManager.switchToTank()
            return
