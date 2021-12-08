# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearJukeboxSelectableObject.py
import logging
from functools import partial
from ClientSelectableObject import ClientSelectableObject
from entity_constants import HighlightColors
from helpers import dependency
from new_year.ny_jukebox_controller import JukeboxSides
from skeletons.new_year import INewYearController, IJukeboxController
from uilogging.deprecated.decorators import loggerEntry
from new_year.cgf_components.highlight_manager import HighlightComponent
_logger = logging.getLogger(__name__)

class NewYearJukeboxSelectableObject(ClientSelectableObject):
    __nyController = dependency.descriptor(INewYearController)
    __jukeboxController = dependency.descriptor(IJukeboxController)

    @loggerEntry
    def onEnterWorld(self, prereqs):
        self._HIGHLIGHT_COLOR = HighlightColors.RED if self.sideName == JukeboxSides.A else HighlightColors.BLUE
        super(NewYearJukeboxSelectableObject, self).onEnterWorld(prereqs)
        self.__nyController.onStateChanged += self.__onStateChanged
        self.__jukeboxController.onHighlightEnable += self.__onHighlightEnable
        self.__onStateChanged()

    def onLeaveWorld(self):
        self.__nyController.onStateChanged -= self.__onStateChanged
        self.__jukeboxController.onHighlightEnable -= self.__onHighlightEnable
        super(NewYearJukeboxSelectableObject, self).onLeaveWorld()

    def onMouseClick(self):
        super(NewYearJukeboxSelectableObject, self).onMouseClick()
        self.__jukeboxController.handleJukeboxClick(self.sideName)

    def _addHighlightComponent(self):
        self.entityGameObject.createComponent(HighlightComponent, self, self._HIGHLIGHT_COLOR, self.edgeMode, False, True, True, partial(self.__jukeboxController.handleJukeboxHighlight, self.sideName, True), partial(self.__jukeboxController.handleJukeboxHighlight, self.sideName, False))

    def __onStateChanged(self):
        self.setEnable(self.__nyController.isEnabled())

    def __onHighlightEnable(self, enabled):
        self.setEnable(enabled)
