# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_popover.py
from gui.Scaleform.daapi.view.meta.CustomizationPopoverMeta import CustomizationPopoverMeta
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

class CustomizationPopover(CustomizationPopoverMeta):
    customizationService = dependency.descriptor(ICustomizationService)

    def popupClosed(self):
        """Function gets called when the customization property sheet is closed
        
        To disable the selected tank region I turn off the highlighter. After turning it off,
        I need to turn it back on otherwise the player is unable to select a new region.
        The only reason I am doing this is because there is not a "resetHighlighter" function that I am aware of.
        """
        if self.customizationService.getHightlighter():
            mode = self.customizationService.getSelectionMode()
            self.customizationService.stopHighlighter()
            self.customizationService.startHighlighter(mode)
