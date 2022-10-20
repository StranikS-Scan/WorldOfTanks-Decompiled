# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/crew_list_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.crew_item_model import CrewItemModel

class CrewListModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(CrewListModel, self).__init__(properties=properties, commands=commands)

    def getCrewList(self):
        return self._getArray(0)

    def setCrewList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCrewListType():
        return CrewItemModel

    def _initialize(self):
        super(CrewListModel, self)._initialize()
        self._addArrayProperty('crewList', Array())
