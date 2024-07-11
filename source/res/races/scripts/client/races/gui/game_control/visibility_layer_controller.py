# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/game_control/visibility_layer_controller.py
import logging
from enum import Enum
import BigWorld
from gui.ClientHangarSpace import getSpaceNameFromPath
from helpers import dependency
from gui.prb_control.entities.listener import IGlobalListener
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IRacesBattleController, IRacesVisibilityLayerController
from extension_utils import ResMgr
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
DEFAULT_NAME = 'default'
RACES_PRB_ACTIVE = 'racesPrbActive'
_CONFIG_FILE = 'races/gui/visibility_layers.xml'

class _VisibilityLayerBits(Enum):
    LAYER1 = 1
    LAYER2 = 2
    LAYER3 = 4
    LAYER4 = 8
    LAYER5 = 16
    LAYER6 = 32
    LAYER7 = 64
    LAYER9 = 256
    LAYER10 = 512
    NA = 65536
    ASIA = 131072
    EU = 262144
    RU = 524288


class RacesVisibilityLayerController(IRacesVisibilityLayerController, IGlobalListener):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _racesController = dependency.descriptor(IRacesBattleController)
    __slots__ = ('__config',)

    def __init__(self):
        super(RacesVisibilityLayerController, self).init()
        self.__config = None
        return

    def init(self):
        super(RacesVisibilityLayerController, self).init()
        self._hangarSpace.onSpaceCreate += self.__onSpaceUpdated
        self.__config = ConfigDataReader.readConfigFile(_CONFIG_FILE)

    def fini(self):
        self._hangarSpace.onSpaceCreate -= self.__onSpaceUpdated
        super(RacesVisibilityLayerController, self).fini()

    def onLobbyInited(self, event):
        super(RacesVisibilityLayerController, self).onLobbyInited(event)
        self.startGlobalListening()

    def onAccountBecomeNonPlayer(self):
        super(RacesVisibilityLayerController, self).onAccountBecomeNonPlayer()
        self.stopGlobalListening()

    def onPrbEntitySwitched(self):
        self.__updateEnvironment()

    def __updateEnvironment(self):
        if self.prbEntity is None:
            return
        else:
            phaseIndex = self._racesController.isRacesPrbActive and RACES_PRB_ACTIVE or DEFAULT_NAME
            self.__changeVisibilityMask(phaseIndex)
            return

    def __changeVisibilityMask(self, name):
        if not self._hangarSpace.inited or self._hangarSpace.spaceLoading():
            return
        hangarConfig = self.__config.get(getSpaceNameFromPath(self._hangarSpace.spacePath))
        if not hangarConfig:
            return
        visibilityMask = hangarConfig.get(name)
        if not visibilityMask:
            _logger.warning('Wrong environment name %s', name)
            return
        BigWorld.wg_setSpaceItemsVisibilityMask(self._hangarSpace.spaceID, visibilityMask)

    def __onSpaceUpdated(self):
        self.__updateEnvironment()


class ConfigDataReader(object):

    @staticmethod
    def readConfigFile(filename):
        result = {}
        config = ResMgr.openSection(filename)
        if config is None:
            raise SoftException('Config file not found {}'.format(filename))
        for hangarName, section in config['hangarEnvironmentSettings'].items():
            result[hangarName] = ConfigDataReader._readEnvironments(section)

        return result

    @staticmethod
    def _readEnvironments(reader):
        result = {}
        for _, environment in reader.items():
            result[environment.readString('name')] = ConfigDataReader._buildVisibilityMask(environment['enabledLayers'])

        return result

    @staticmethod
    def _buildVisibilityMask(section):
        result = 0
        if section is None:
            return result
        else:
            for name, value in section.items():
                if value.asBool:
                    result |= _VisibilityLayerBits[name.upper()].value

            return result
