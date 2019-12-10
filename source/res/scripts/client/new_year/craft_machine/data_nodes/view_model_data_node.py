# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/data_nodes/view_model_data_node.py
from helpers import dependency
from skeletons.new_year import ICraftMachineSettingsStorage
from .abstract_data_node import IAbstractDataNode

class ViewModelDataNode(IAbstractDataNode):
    __settings = dependency.descriptor(ICraftMachineSettingsStorage)

    def __init__(self, viewModel):
        super(ViewModelDataNode, self).__init__()
        self._viewModel = viewModel

    def destroy(self):
        super(ViewModelDataNode, self).destroy()
        self._viewModel = None
        return

    def _onInit(self):
        self._loadFrom(self.__settings)
        self.updateData()

    def _onDestroy(self):
        self._saveTo(self.__settings)

    def _loadFrom(self, settings):
        pass

    def _saveTo(self, settings):
        pass
