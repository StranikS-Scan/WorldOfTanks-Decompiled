# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/recruit_banner_model.py
from frameworks.wulf import ViewModel

class RecruitBannerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RecruitBannerModel, self).__init__(properties=properties, commands=commands)

    def getAvailableForConvert(self):
        return self._getNumber(0)

    def setAvailableForConvert(self, value):
        self._setNumber(0, value)

    def getEndTimeConvert(self):
        return self._getNumber(1)

    def setEndTimeConvert(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RecruitBannerModel, self)._initialize()
        self._addNumberProperty('availableForConvert', 0)
        self._addNumberProperty('endTimeConvert', 0)
