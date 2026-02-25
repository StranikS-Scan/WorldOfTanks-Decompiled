# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/models/custom_shells.py
from __future__ import absolute_import
import typing
from items import vehicles
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_modules import Shell
    from fun_random.gui.feature.configs.sub_modes.custom_shells import FunSubModeCustomShellConfigModel, FunSubModeCustomShellSlotConfigModel, FunSubModeCustomShellLayoutConfigModel, FunSubModeCustomShellsConfigModel

class FunCustomShell(object):

    def __init__(self, intCD, count, imageName):
        self.intCD = intCD
        self.count = count
        self.imageName = imageName

    @classmethod
    def fromShellItem(cls, shell):
        return cls(shell.intCD, shell.count, shell.descriptor.iconName)

    @classmethod
    def fromCustomShellConfig(cls, shellConfig, count):
        return cls(shellConfig.intCD, count, vehicles.getItemByCompactDescr(shellConfig.intCD).iconName)


class FunCustomShellSlot(object):

    def __init__(self, slotConfig, customShell, originalIndex):
        self.__slotConfig = slotConfig
        self.__customShell = customShell
        self.__originalIndex = originalIndex

    @classmethod
    def fromShellItem(cls, customShellsConfig, layoutConfig, shell):
        return cls(customShellsConfig.slots[layoutConfig.slotIndex], FunCustomShell.fromShellItem(shell), layoutConfig.shellIndex)

    @classmethod
    def fromCustomLayoutConfig(cls, customShellsConfig, layoutConfig):
        return cls(customShellsConfig.slots[layoutConfig.slotIndex], FunCustomShell.fromCustomShellConfig(customShellsConfig.shells[layoutConfig.slotIndex], layoutConfig.shellCount), layoutConfig.shellIndex)

    @property
    def originalIndex(self):
        return self.__originalIndex

    @property
    def command(self):
        return self.__slotConfig.command

    @property
    def shell(self):
        return self.__customShell

    @property
    def imageNameOverride(self):
        return self.__slotConfig.imageOverride

    @property
    def tooltipOverride(self):
        return self.__slotConfig.tooltipOverride
