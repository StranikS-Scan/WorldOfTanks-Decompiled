# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/storage_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, module
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.STORAGE_RESTORE_DEVICE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.RestoreOptDeviceBlockTooltipData(contexts.RestoreCardContext())),)
