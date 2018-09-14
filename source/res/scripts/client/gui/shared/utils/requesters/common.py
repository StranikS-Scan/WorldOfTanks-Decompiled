# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/common.py
import BigWorld

class RequestProcessor(object):
    """
    Incapsulates delayed server request
    """

    def __init__(self, delay, callback):
        """
        :param delay: delay before calling the callback(in seconds)
        :param callback: callback to be called
        """
        self.__callback = callback
        self.__fired = False
        self.__bwCallbackID = BigWorld.callback(delay, self.__cooldownCallback)

    @property
    def isFired(self):
        """
        Returns to be called flag
        :return: boolean value
        """
        return self.__fired

    def cancel(self):
        """
        Cancel delayed callback
        """
        if self.__bwCallbackID is not None:
            BigWorld.cancelCallback(self.__bwCallbackID)
            self.__bwCallbackID = None
        return

    def __cooldownCallback(self):
        """
        Proxy-function for delayed callback. Cancel callback and return result
        """
        self.__bwCallbackID = None
        self.__fired = True
        self.__callback()
        return
