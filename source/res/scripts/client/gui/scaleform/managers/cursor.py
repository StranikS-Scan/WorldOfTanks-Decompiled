# Embedded file name: scripts/client/gui/Scaleform/managers/Cursor.py
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.meta.CursorMeta import CursorMeta
from gui.Scaleform.framework.entities.View import View
import GUI
import BigWorld
__author__ = 'd_trofimov'

class Cursor(CursorMeta, View):
    ARROW = 'arrow'
    AUTO = 'auto'
    BUTTON = 'button'
    HAND = 'hand'
    IBEAM = 'ibeam'
    ROTATE = 'rotate'
    RESIZE = 'resize'
    MOVE = 'move'
    DRAG_OPEN = 'dragopen'
    DRAG_CLOSE = 'dragclose'
    __DAAPI_ERROR = 'flashObject is Python Cursor class can`t be None!'
    __isAutoShow = False

    def __init__(self):
        super(Cursor, self).__init__()
        self.__isActivated = False

    @classmethod
    def setAutoShow(cls, flag):
        cls.__isAutoShow = flag

    @classmethod
    def getAutoShow(cls):
        return cls.__isAutoShow

    def _populate(self):
        super(Cursor, self)._populate()
        self.attachCursor(self.__isAutoShow)
        self.setAutoShow(False)

    def _dispose(self):
        super(Cursor, self)._dispose()

    def attachCursor(self, automaticallyShow):
        if automaticallyShow:
            self.show()
        if not self.__isActivated:
            mcursor = GUI.mcursor()
            mcursor.visible = False
            LOG_DEBUG('Cursor attach')
            BigWorld.setCursor(mcursor)
            self.__isActivated = True

    def detachCursor(self, automaticallyHide):
        if self.__isActivated:
            LOG_DEBUG('Cursor detach')
            BigWorld.setCursor(None)
            self.__isActivated = False
        if automaticallyHide:
            self.hide()
        return

    def show(self):
        if self.flashObject is not None:
            self.flashObject.visible = True
        else:
            LOG_ERROR(self.__DAAPI_ERROR)
        return

    def hide(self):
        if self.flashObject is not None:
            self.flashObject.visible = False
        else:
            LOG_ERROR(self.__DAAPI_ERROR)
        return

    def setCursorForced(self, cursor):
        self.as_setCursorS(cursor)
