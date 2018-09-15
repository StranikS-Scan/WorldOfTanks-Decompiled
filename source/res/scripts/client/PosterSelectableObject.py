# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PosterSelectableObject.py
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
from gui.game_control.CalendarController import CalendarInvokeOrigin
from skeletons.gui.game_control import ICalendarController
from skeletons.new_year import ICustomizableObjectsManager

class PosterSelectableObject(ClientSelectableObject):
    calendarCtrl = dependency.descriptor(ICalendarController)
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        super(PosterSelectableObject, self).__init__()
        self.anchorName = 'PosterSelectableObject'

    def onEnterWorld(self, prereqs):
        super(PosterSelectableObject, self).onEnterWorld(prereqs)
        self.customizableObjectsMgr.addSelectableEntity(self)

    def onLeaveWorld(self):
        super(PosterSelectableObject, self).onLeaveWorld()
        self.customizableObjectsMgr.removeSelectableEntity(self)

    def onClicked(self):
        super(PosterSelectableObject, self).onClicked()
        self.calendarCtrl.showCalendar(CalendarInvokeOrigin.HANGAR)
