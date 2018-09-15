# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/component_override.py
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from gui.Scaleform.daapi.view.component_override import ComponentOverride

class BootcampComponentOverride(ComponentOverride):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, default, override):
        check = self.bootcampController.isInBootcamp
        super(BootcampComponentOverride, self).__init__(default, override, check)
