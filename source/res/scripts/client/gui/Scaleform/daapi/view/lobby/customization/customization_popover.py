# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_popover.py
from gui.Scaleform.daapi.view.meta.CustomizationPopoverMeta import CustomizationPopoverMeta
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

class CustomizationPopover(CustomizationPopoverMeta):
    customizationService = dependency.descriptor(ICustomizationService)

    def popupClosed(self):
        if self.customizationService.getHightlighter():
            mode = self.customizationService.getSelectionMode()
            self.customizationService.stopHighlighter()
            self.customizationService.startHighlighter(mode)
