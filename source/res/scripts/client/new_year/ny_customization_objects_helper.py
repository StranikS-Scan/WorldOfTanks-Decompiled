# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_customization_objects_helper.py
import logging
from items.components.ny_constants import TOY_OBJECTS_IDS_BY_NAME
from helpers import dependency
from ny_common.ObjectsConfig import ObjectsConfig
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)

def getDecorationImageID(decorationToken):
    splited = decorationToken.split(':')
    return splited[-1] if len(splited) == 3 else ''


class CustomizationObjectsHelper(object):
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __nyController = dependency.descriptor(INewYearController)

    def onLobbyInited(self):
        pass

    def clear(self):
        pass

    def getLevel(self, objectName):
        objectLevels = self.__nyController.requester.getObjectsLevels()
        if not objectLevels:
            _logger.warning('Objects has not been initialized or has been cleared')
            return 0
        else:
            level = objectLevels[TOY_OBJECTS_IDS_BY_NAME[objectName]]
            if level is None:
                _logger.error('Can not find object level for object %s', objectName)
                return 0
            return level

    def getConfig(self):
        return self.__lobbyCtx.getServerSettings().getNewYearObjectsConfig()

    def isMaxLevel(self, objectID, level):
        config = self.getConfig()
        objDesriptor = config.getObjectByID(objectID)
        return objDesriptor.getNextLevel(level) is None
