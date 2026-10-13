# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/tooltip_positioner.py


class TooltipPositionerMixin(object):

    def __onWindowPositionChanged(self, uniqueID, *_):
        window = self.gui.windowsManager.getWindow(uniqueID)
        if window:
            window.onPositionChanged -= self.__onWindowPositionChanged
            if self.__positionX and self.__positionY:
                width, __ = window.size
                window.move(int(self.__positionX) - int(width), int(self.__positionY))

    def createToolTip(self, event):
        window = super(TooltipPositionerMixin, self).createToolTip(event)
        if window:
            self.__positionX = event.getArgument('positionX')
            self.__positionY = event.getArgument('positionY')
            window.onPositionChanged += self.__onWindowPositionChanged
        return window
