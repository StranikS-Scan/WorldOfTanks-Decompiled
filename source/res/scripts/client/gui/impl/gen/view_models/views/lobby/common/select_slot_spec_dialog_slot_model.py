# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/select_slot_spec_dialog_slot_model.py
from frameworks.wulf import ViewModel

class SelectSlotSpecDialogSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SelectSlotSpecDialogSlotModel, self).__init__(properties=properties, commands=commands)

    def getSpecialization(self):
        return self._getString(0)

    def setSpecialization(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(SelectSlotSpecDialogSlotModel, self)._initialize()
        self._addStringProperty('specialization', '')
