# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/hangar_space_reloader.py
import logging
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpaceReloader
from skeletons.gui.shared.utils import IHangarSpace
from gui.impl.lobby.offers import getGfImagePath
from gui.Scaleform.Waiting import Waiting

class ErrorFlags(object):
    NONE = 0
    INVALID_NAME = 1
    ALREADY_PROCESSING_RELOAD = 2
    WAITING_FOR_SPACE = 4
    SPACE_PATH_NOT_INITED = 8
    DUPLICATE_REQUEST = 16
    HANGAR_NOT_READY = 32


_logger = logging.getLogger(__name__)

class HangarSpaceReloader(IHangarSpaceReloader):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HangarSpaceReloader, self).__init__()
        self.__loadingSpacePath = None
        self.__waitingMessage = None
        return

    def init(self):
        self.hangarSpace.onSpaceCreate += self.__onHangarSpaceLoaded
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self.__onHangarSpaceLoaded
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.__hideWaiting()
        self.__loadingSpacePath = None
        return

    def changeHangarSpace(self, spaceName, visibilityMask, waitingMessage=None, backgroundImage=None, actionChange=False):
        errCode = ErrorFlags.NONE
        if not spaceName:
            _logger.error('Invalid space name: the name cannot be empty.')
            return (False, ErrorFlags.INVALID_NAME)
        else:
            reloadValid = True
            if self.__loadingSpacePath is not None:
                _logger.error('Failed to load space "%s", because another space is loading: %s', spaceName, self.__loadingSpacePath)
                reloadValid = False
                errCode |= ErrorFlags.ALREADY_PROCESSING_RELOAD
            if not self.hangarSpace.spaceInited:
                _logger.error('Failed to load space "%s", because hangar is not inited.', spaceName)
                reloadValid = False
                errCode |= ErrorFlags.HANGAR_NOT_READY
            if self.hangarSpace.spaceLoading():
                _logger.error('Failed to load space "%s", because another space is loading.', spaceName)
                reloadValid = False
                errCode |= ErrorFlags.WAITING_FOR_SPACE
            hangarSpacePath = self.hangarSpace.spacePath
            if self.hangarSpace.spaceInited and hangarSpacePath is None:
                _logger.error('Abnormal behaviour: hangarSpace.spacePath is not initialized')
                reloadValid = False
                errCode |= ErrorFlags.SPACE_PATH_NOT_INITED
            spacePath = spaceName if spaceName.startswith('space') else 'spaces/{}'.format(spaceName)
            if spacePath == hangarSpacePath:
                _logger.warning('No need to load space "%s", because it is already loaded', spaceName)
                reloadValid = False
                errCode |= ErrorFlags.DUPLICATE_REQUEST
            if not reloadValid:
                return (reloadValid, errCode)
            self.__loadingSpacePath = spacePath
            self.__waitingMessage = waitingMessage
            if waitingMessage:
                Waiting.show(waitingMessage, isAlwaysOnTop=True, backgroundImage=getGfImagePath(backgroundImage))
            from gui.ClientHangarSpace import g_clientHangarSpaceOverride
            g_clientHangarSpaceOverride.setPath(spacePath, visibilityMask=visibilityMask, isReload=True, event=self.hangarSpace.onSpaceChangedByAction if actionChange else None)
            return (reloadValid, errCode)

    @property
    def hangarSpacePath(self):
        return self.__loadingSpacePath or self.hangarSpace.spacePath

    def __onHangarSpaceLoaded(self):
        self.__hideWaiting()
        self.__loadingSpacePath = None
        return

    def __onSpaceDestroy(self, inited):
        if self.__loadingSpacePath is None:
            return
        else:
            if self.hangarSpace.spacePath == self.__loadingSpacePath:
                self.__hideWaiting()
                self.__loadingSpacePath = None
            return

    def __hideWaiting(self):
        if self.__waitingMessage is not None:
            Waiting.hide(self.__waitingMessage)
            self.__waitingMessage = None
        return
