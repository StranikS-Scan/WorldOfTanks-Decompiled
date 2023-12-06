# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/new_year_blocks.py
from visual_script import ASPECT
from visual_script.block import Meta, Block
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
clientSelectableCameraObject, dependency, navigation, newYearController = dependencyImporter('ClientSelectableCameraObject', 'helpers.dependency', 'gui.impl.new_year.navigation', 'skeletons.new_year')

class NewYearMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class NavigateTo(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearController.INewYearController)

    def __init__(self, *args, **kwargs):
        super(NavigateTo, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._customizationName = self._makeDataInputSlot('CustomizationName', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        if self.__nyController.isEnabled():
            clientSelectableCameraObject.ClientSelectableCameraObject.deselectAll()
            name = self._customizationName.getValue()
            navigation.NewYearNavigation.switchByAnchorName(name)
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]
