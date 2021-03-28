# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bootcamp/bootcamp_exit_model.py
from gui.impl.gen.view_models.views.bootcamp.bootcamp_progress_model import BootcampProgressModel

class BootcampExitModel(BootcampProgressModel):
    __slots__ = ('onLeaveBootcamp',)

    def __init__(self, properties=6, commands=1):
        super(BootcampExitModel, self).__init__(properties=properties, commands=commands)

    def getIsInBattle(self):
        return self._getBool(3)

    def setIsInBattle(self, value):
        self._setBool(3, value)

    def getIsNeedAwarding(self):
        return self._getBool(4)

    def setIsNeedAwarding(self, value):
        self._setBool(4, value)

    def getIsReferral(self):
        return self._getBool(5)

    def setIsReferral(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BootcampExitModel, self)._initialize()
        self._addBoolProperty('isInBattle', False)
        self._addBoolProperty('isNeedAwarding', False)
        self._addBoolProperty('isReferral', False)
        self.onLeaveBootcamp = self._addCommand('onLeaveBootcamp')
