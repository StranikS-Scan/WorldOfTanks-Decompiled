# Embedded file name: scripts/client/gui/Scaleform/windows.py
import GUI
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.Scaleform.Flash import Flash
from gui.app_loader import g_appLoader

class ModalWindow(Flash):

    def __init__(self, swf):
        Flash.__init__(self, swf)
        component = self.component
        component.size = (2, 2)
        self.component = GUI.Window('')
        self.component.addChild(component, 'flash')
        self.component.script = self
        self.component.crossFocus = True
        self.component.dragFocus = True
        self.component.dropFocus = True
        self.component.focus = True
        self.component.moveFocus = True
        self.component.mouseButtonFocus = True
        self.movie.backgroundAlpha = 0.75
        self.movie.wg_inputKeyMode = 2
        self.addFsCallbacks({'WoTLogoff': self.onLogoff})

    @property
    def movie(self):
        return self.component.flash.movie

    def close(self):
        self.component.script = None
        Flash.close(self)
        return

    def onLogoff(self, arg):
        import BigWorld

        def logOff():
            g_appLoader.goToLoginByRQ()

        BigWorld.callback(0.1, logOff)

    def handleAxisEvent(self, event):
        return True

    def handleDragEnterEvent(self, position, dragged):
        return True

    def handleDragLeaveEvent(self, position, dragged):
        return True

    def handleDragStartEvent(self, position):
        return True

    def handleDragStopEvent(self, position):
        return True

    def handleDropEvent(self, position, dropped):
        return True

    def handleKeyEvent(self, event):
        return self.movie.handleKeyEvent(event)

    def handleMouseClickEvent(self, position):
        return True

    def handleMouseEnterEvent(self, position):
        return True

    def handleMouseEvent(self, comp, event):
        return True

    def handleMouseLeaveEvent(self, position):
        return True

    def handleMouseButtonEvent(self, comp, event):
        return self.movie.handleMouseButtonEvent(event)


class BattleWindow(Flash):

    def __init__(self, swf):
        Flash.__init__(self, swf)
        self.addFsCallbacks({'WoTQuit': self.onQuit,
         'WoTLogoff': self.onLogoff})
        self.afterCreate()

    def __del__(self):
        LOG_DEBUG('Deleted: %s' % self)

    def close(self):
        Flash.close(self)

    def onQuit(self, arg):
        import BigWorld
        BigWorld.quit()

    def onLogoff(self, _):
        g_appLoader.goToLoginByRQ()


class UIInterface(object):

    def __init__(self):
        self.uiHolder = None
        return

    def __del__(self):
        LOG_DEBUG('Deleted: %s' % self)

    def populateUI(self, proxy):
        self.uiHolder = proxy

    def dispossessUI(self):
        self.uiHolder = None
        return

    def call(self, methodName, args = None):
        if self.uiHolder:
            self.uiHolder.call(methodName, args)
        else:
            LOG_WARNING('Error to %s.call("%s", ...), check for possible memory leaks' % (self.__class__, methodName))

    def callNice(self, methodName, args = None):
        if self.uiHolder:
            self.uiHolder.callNice(methodName, args)
        else:
            LOG_WARNING('Error to %s.callJson("%s", ...), check for possible memory leaks' % (self.__class__, methodName))

    def respond(self, args = None):
        if self.uiHolder:
            self.uiHolder.respond(args)
        else:
            LOG_WARNING('Error to %s.respond(), check for possible memory leaks' % self.__class__)

    def setMovieVariable(self, path, value):
        if self.uiHolder:
            self.uiHolder.setMovieVariable(path, value)
        else:
            LOG_WARNING('Error to %s.setMovieVariable("%s", ...), check for possible memory leaks' % (self.__class__, path))
