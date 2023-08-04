# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/open_box_error_view_model.py
from frameworks.wulf import ViewModel

class OpenBoxErrorViewModel(ViewModel):
    __slots__ = ('toHangar',)

    def __init__(self, properties=0, commands=1):
        super(OpenBoxErrorViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(OpenBoxErrorViewModel, self)._initialize()
        self.toHangar = self._addCommand('toHangar')
