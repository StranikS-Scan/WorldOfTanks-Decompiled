# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/crew_controller.py
from gui.shared.gui_items.Tankman import NO_SLOT, NO_TANKMAN
from helpers import dependency
from skeletons.gui.game_control import ICrewController
from skeletons.gui.impl import IGuiLoader

class CrewController(ICrewController):

    def __init__(self):
        super(CrewController, self).__init__()
        self.__widgetSlotIdx = NO_SLOT
        self.__widgetTankmanID = NO_TANKMAN

    def setWidgetData(self, viewKey):
        uiLoader = dependency.instance(IGuiLoader)
        view = uiLoader.windowsManager.getViewByLayoutID(viewKey)
        if view:
            currentSlotIdx, _, currentTankman = view.crewWidget.getWidgetData()
            self.__widgetSlotIdx = currentSlotIdx
            self.__widgetTankmanID = currentTankman.invID if currentTankman else NO_TANKMAN

    def getWidgetData(self):
        return (self.__widgetSlotIdx, self.__widgetTankmanID)
