# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/widget/qt_crew_widget_cm_handlers.py
from crew_widget_cm_handlers import CrewContextMenuHandler
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class QuickTrainingCrewWidgetContextMenuHandler(CrewContextMenuHandler):
    uiLoader = dependency.instance(IGuiLoader)

    def __init__(self, cmProxy, ctx=None):
        super(QuickTrainingCrewWidgetContextMenuHandler, self).__init__(cmProxy, ctx)
        self._view = self.uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.crew.QuickTrainingView())

    def showPersonalFile(self):
        super(QuickTrainingCrewWidgetContextMenuHandler, self).showPersonalFile()
        self._view.destroyWindow()

    def changeCrewMember(self):
        super(QuickTrainingCrewWidgetContextMenuHandler, self).changeCrewMember()
        self._view.destroyWindow()

    def changeSpecialization(self):
        super(QuickTrainingCrewWidgetContextMenuHandler, self).changeSpecialization()
        self._view.destroyWindow()
