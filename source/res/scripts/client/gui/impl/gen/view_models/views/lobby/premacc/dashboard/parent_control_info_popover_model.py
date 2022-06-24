# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/parent_control_info_popover_model.py
from frameworks.wulf import ViewModel

class ParentControlInfoPopoverModel(ViewModel):
    __slots__ = ('onLinkClicked',)

    def __init__(self, properties=0, commands=1):
        super(ParentControlInfoPopoverModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ParentControlInfoPopoverModel, self)._initialize()
        self.onLinkClicked = self._addCommand('onLinkClicked')
