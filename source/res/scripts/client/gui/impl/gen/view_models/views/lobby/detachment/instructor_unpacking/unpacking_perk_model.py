# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructor_unpacking/unpacking_perk_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_base_model import PerkBaseModel

class UnpackingPerkModel(PerkBaseModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(UnpackingPerkModel, self).__init__(properties=properties, commands=commands)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(UnpackingPerkModel, self)._initialize()
        self._addBoolProperty('isSelected', False)
