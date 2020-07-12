# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Waiting.py
import logging
import typing
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader, IWaitingWidget
_logger = logging.getLogger(__name__)

def convertToResource(message):
    splitted = message.split('/')
    resourceID = R.invalid
    if splitted:
        resourceID = R.strings.waiting
        for item in splitted:
            resourceID = resourceID.dyn(item.replace('-', '_'))

    return resourceID


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def worker(appLoader=None):
    return appLoader.getWaitingWorker()


class Waiting(object):
    __appLoader = dependency.descriptor(IAppLoader)

    @classmethod
    def getWaitingView(cls, overlapsUI):
        return cls.__getWaiting().getWaitingView(overlapsUI)

    @classmethod
    def isVisible(cls):
        return cls.__getWaiting().isWaitingShown()

    @classmethod
    def isOpened(cls, msg):
        return cls.__getWaiting().isWaitingShown(convertToResource(msg)())

    @classmethod
    def getWaiting(cls, msg):
        return cls.__getWaiting().getWaitingTask(convertToResource(msg)())

    @classmethod
    def getSuspendedWaiting(cls, msg):
        return cls.__getWaiting().getSuspendedWaitingTask(convertToResource(msg)())

    @classmethod
    def show(cls, message, isSingle=False, interruptCallback=None, overlapsUI=True, isAlwaysOnTop=False, backgroundImage=None):
        resourceID = convertToResource(message)
        if not resourceID:
            _logger.error('Waiting can not be shown. Resource is not found: %s', message)
            return
        cls.__getWaiting().show(resourceID(), isSingle=isSingle, interruptCallback=interruptCallback, isBlocking=overlapsUI, isAlwaysOnTop=isAlwaysOnTop, backgroundImage=backgroundImage)

    @classmethod
    def hide(cls, message):
        resourceID = convertToResource(message)
        if not resourceID:
            _logger.error('Waiting can not be hidden. Resource is not found: %s', message)
            return
        cls.__getWaiting().hide(resourceID())

    @classmethod
    def suspend(cls, lockerID=None):
        cls.__getWaiting().suspend(lockerID)

    @classmethod
    def isResumeLocked(cls):
        return cls.__getWaiting().isResumeLocked()

    @classmethod
    def resume(cls, lockerID=None, hard=False):
        cls.__getWaiting().resume(lockerID, hard)

    @classmethod
    def isSuspended(cls):
        return cls.__getWaiting().isSuspended()

    @classmethod
    def close(cls):
        cls.__getWaiting().close()

    @classmethod
    def rollback(cls):
        cls.__getWaiting().rollback()

    @classmethod
    def cancelCallback(cls):
        cls.__getWaiting().cancelCallback()

    @classmethod
    def __getWaiting(cls):
        return cls.__appLoader.getWaitingWorker()
