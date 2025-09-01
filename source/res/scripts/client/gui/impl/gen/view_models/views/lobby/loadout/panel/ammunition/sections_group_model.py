# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/panel/ammunition/sections_group_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.section_model import SectionModel

class SectionsGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SectionsGroupModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getSections(self):
        return self._getArray(1)

    def setSections(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSectionsType():
        return SectionModel

    def _initialize(self):
        super(SectionsGroupModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addArrayProperty('sections', Array())
