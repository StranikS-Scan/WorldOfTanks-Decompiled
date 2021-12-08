# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearBaseEntryObject.py
from ClientSelectableObject import ClientSelectableObject
from entity_constants import HighlightColors
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
from new_year.cgf_components.highlight_manager import HighlightGroupComponent

class NewYearBaseEntryObject(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _nyController = dependency.descriptor(INewYearController)
    _HIGHLIGHT_COLOR = HighlightColors.BLUE

    def onEnterWorld(self, prereqs):
        super(NewYearBaseEntryObject, self).onEnterWorld(prereqs)
        self._nyController.onStateChanged += self.__onStateChanged
        self.__onStateChanged()
        if self.selectionGroupIdx:
            self.entityGameObject.createComponent(HighlightGroupComponent, self.selectionGroupIdx)

    def onLeaveWorld(self):
        self._nyController.onStateChanged -= self.__onStateChanged
        self.entityGameObject.removeComponentByType(HighlightGroupComponent)
        super(NewYearBaseEntryObject, self).onLeaveWorld()

    def __onStateChanged(self):
        self.setEnable(self._nyController.isEnabled())
