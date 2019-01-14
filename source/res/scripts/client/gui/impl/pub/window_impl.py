# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/window_impl.py
import logging
from frameworks.wulf import PositionAnchor, Window
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.window_model import WindowModel
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)

class WindowImpl(Window):
    __slots__ = ('__areaID',)
    gui = dependency.descriptor(IGuiLoader)

    def __init__(self, wndFlags, *args, **kwargs):
        self.__areaID = kwargs.pop('areaID', R.areas.default())
        super(WindowImpl, self).__init__(wndFlags, *args, **kwargs)

    @property
    def windowModel(self):
        return super(WindowImpl, self)._getDecoratorViewModel()

    @property
    def area(self):
        return self.gui.windowsManager.getWindowsArea(self.__areaID) if self.__areaID else None

    def move(self, x, y, xAnchor=PositionAnchor.LEFT, yAnchor=PositionAnchor.TOP):
        area = self.area
        if area is not None:
            return area.move(self, x, y, xAnchor=xAnchor, yAnchor=yAnchor)
        else:
            _logger.error('Window %r can not moved due to it is not added to area.', self)
            return False

    def center(self):
        area = self.area
        if area is not None:
            return area.center(self)
        else:
            _logger.error('Window %r can not be centered due to it is not added to area.', self)
            return False

    def cascade(self):
        area = self.area
        if area is not None:
            return area.cascade(self)
        else:
            _logger.error('Window %r can not be cascaded due to it is not added to area.', self)
            return False

    def _initialize(self):
        super(WindowImpl, self)._initialize()
        area = self.area
        if area is not None:
            area.addWindow(self)
        if self.windowModel is not None:
            self.windowModel.onClosed += self._onClosed
            self.windowModel.onMinimized += self._onMinimize
        return

    def _finalize(self):
        area = self.area
        if area is not None:
            self.area.removeWindow(self)
        if self.windowModel is not None:
            self.windowModel.onClosed -= self._onClosed
            self.windowModel.onMinimized -= self._onMinimize
        super(WindowImpl, self)._finalize()
        return

    def _onClosed(self, _=None):
        self.destroy()

    def _onMinimize(self, _=None):
        self.hide()
