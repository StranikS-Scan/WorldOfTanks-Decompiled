# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/visibility_layer_controller.py
import logging
from enum import Enum
import BigWorld
from halloween.gui.impl.auxiliary.close_event_confirmator import CloseEventConfirmator
from helpers import dependency
from Event import EventManager
from gui.prb_control.entities.listener import IGlobalListener
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.lobby_context import ILobbyContext
from halloween.skeletons.gui.visibility_layer_controller import IHalloweenVisibilityLayerController
from skeletons.gui.game_control import IHalloweenController
from halloween.gui.halloween_gui_constants import FUNCTIONAL_FLAG
from halloween.hw_constants import INVALID_PHASE_INDEX
from debug_utils import LOG_WARNING
from extension_utils import ResMgr
_logger = logging.getLogger(__name__)
_CONFIG_FILE = 'halloween/gui/visibility_layers.xml'

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


class VisibilityLayerController(IHalloweenVisibilityLayerController, IGlobalListener):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _hwController = dependency.descriptor(IHalloweenController)

    def __init__(self):
        super(VisibilityLayerController, self).init()
        self.__hangarConfig = None
        self._em = EventManager()
        self.__closeEventConfirmator = CloseEventConfirmator()
        return

    def init(self):
        super(VisibilityLayerController, self).init()
        self._hwController.onQuestsUpdated += self.__onEventsCacheSyncCompleted
        self._hwController.onChangeActivePhase += self.__onChangeActivePhase
        self._hangarSpace.onSpaceCreate += self.__onSpaceUpdated
        reader = ConfigDataReader()
        reader.readConfigFile()
        self.__hangarConfig = reader.hangarConfig

    def fini(self):
        self._hwController.onQuestsUpdated -= self.__onEventsCacheSyncCompleted
        self._hwController.onChangeActivePhase -= self.__onChangeActivePhase
        self._hangarSpace.onSpaceCreate -= self.__onSpaceUpdated
        self._em.clear()
        super(VisibilityLayerController, self).fini()

    def onLobbyInited(self, event):
        super(VisibilityLayerController, self).onLobbyInited(event)
        self.startGlobalListening()
        self.__updateCloseEventConfirmator(shouldStart=True)

    def onAccountBecomeNonPlayer(self):
        super(VisibilityLayerController, self).onAccountBecomeNonPlayer()
        self.stopGlobalListening()
        self.__updateCloseEventConfirmator(shouldStart=False)

    def onPrbEntitySwitched(self):
        self.__updateEnvironment()
        self.__updateCloseEventConfirmator(shouldStart=True)

    def __updateEnvironment(self):
        if self.prbEntity is None:
            return
        else:
            phaseIndex = INVALID_PHASE_INDEX
            isEventMode = self._hwController.isEventPrbActive()
            if isEventMode:
                activePhase = self._hwController.phases.getActivePhase()
                if activePhase is None:
                    return
                phaseIndex = activePhase.phaseIndex
            self.changeVisibilityMask(phaseIndex)
            return

    def changeVisibilityMask(self, phaseIndex):
        if not self._hangarSpace.inited or self._hangarSpace.spaceLoading():
            return
        phaseConfig = self.__hangarConfig.get(phaseIndex)
        if not phaseConfig:
            LOG_WARNING('Wrong phase index %s' % phaseIndex)
            return
        visibilityMask = phaseConfig['visibilityMask']
        BigWorld.wg_setSpaceItemsVisibilityMask(self._hangarSpace.spaceID, visibilityMask)

    def __onEventsCacheSyncCompleted(self):
        self.__updateEnvironment()

    def __onChangeActivePhase(self, _):
        self.__updateEnvironment()

    def __onSpaceUpdated(self):
        self.__updateEnvironment()

    def __onServerSettingChanged(self, diff):
        if 'hallowen_config' in diff and 'hangarEnvironmentSettings' in diff['hallowen_config']:
            self.__updateEnvironment()

    def __updateCloseEventConfirmator(self, shouldStart):
        if self.prbEntity is None:
            return
        else:
            isEventMode = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.HALLOWEEN_BATTLE)
            shouldStart &= isEventMode
            if shouldStart:
                if not self.__closeEventConfirmator.isStarted:
                    self.__closeEventConfirmator.start()
            elif self.__closeEventConfirmator.isStarted:
                self.__closeEventConfirmator.stop()
            return


class ConfigDataReader(object):

    def __init__(self):
        super(ConfigDataReader, self).__init__()
        self.__hangarConfig = {}

    @property
    def hangarConfig(self):
        return self.__hangarConfig

    def readConfigFile(self):
        self.__hangarConfig = {}
        configSection = ResMgr.openSection(_CONFIG_FILE)
        if configSection is None:
            return
        else:
            for _, envSection in configSection['hangarEnvironmentSettings'].items():
                phaseID = envSection['phaseID'].asInt
                self.__hangarConfig[phaseID] = {'visibilityMask': self._buildVisibilityMask(envSection['enabledLayers'])}

            return

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
