# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_views_helpers.py
import logging
from gui import GUI_SETTINGS
from new_year.gui.constants import VIEW_ALIAS
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import time_utils, dependency
from new_year.skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)

def getTimerGameDayLeft():
    return time_utils.getDayTimeLeft() + 1


def showInfoVideo():
    url = GUI_SETTINGS.newYearInfo.get('baseURL')
    if url is None:
        _logger.error('newYearInfo.baseURL is missed')
    showBrowserOverlayView(url, alias=VIEW_ALIAS.NY_BROWSER_VIEW)
    return


class HoverObject(object):
    __slots__ = ('objectName', 'spaceHover', 'guiHover')

    def __init__(self, objectName):
        self.objectName = objectName
        self.spaceHover = False
        self.guiHover = False

    @property
    def isHovered(self):
        return self.objectName is not None and self.spaceHover

    def setSpaceObjectHover(self, objectName, isHovered):
        self.objectName = objectName
        self.spaceHover = isHovered

    def setGUIObjectHover(self, objectName, isHovered):
        self.objectName = objectName
        self.guiHover = isHovered

    def clear(self):
        self.objectName = None
        self.spaceHover = False
        self.guiHover = False
        return


@dependency.replace_none_kwargs(newYearController=INewYearController)
def destroyGUIHoveredObject(hoverObject, newYearController=None):
    if hoverObject.guiHover and hoverObject.objectName is not None:
        newYearController.setGuiObjectHover(hoverObject.objectName, False)
    hoverObject.clear()
    return
