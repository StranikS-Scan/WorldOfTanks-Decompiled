# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/awards/seniority_awards_category_info_model.py
from frameworks.wulf import ViewModel

class SeniorityAwardsCategoryInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SeniorityAwardsCategoryInfoModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(SeniorityAwardsCategoryInfoModel, self)._initialize()
        self._addStringProperty('category', '')
