# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructor_page_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_model import CommanderModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.instructor_page.instructor_page_info_model import InstructorPageInfoModel

class InstructorPageViewModel(NavigationViewModel):
    __slots__ = ('onAssignClick', 'onDemountClick', 'onRecoverClick', 'onVoiceListenClick', 'onVoiceToggleClick')

    def __init__(self, properties=18, commands=8):
        super(InstructorPageViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def information(self):
        return self._getViewModel(2)

    @property
    def commander(self):
        return self._getViewModel(3)

    @property
    def vehicle(self):
        return self._getViewModel(4)

    @property
    def price(self):
        return self._getViewModel(5)

    def getId(self):
        return self._getNumber(6)

    def setId(self, value):
        self._setNumber(6, value)

    def getBackground(self):
        return self._getResource(7)

    def setBackground(self, value):
        self._setResource(7, value)

    def getIcon(self):
        return self._getString(8)

    def setIcon(self, value):
        self._setString(8, value)

    def getGrade(self):
        return self._getNumber(9)

    def setGrade(self, value):
        self._setNumber(9, value)

    def getGender(self):
        return self._getString(10)

    def setGender(self, value):
        self._setString(10, value)

    def getIsUnremovable(self):
        return self._getBool(11)

    def setIsUnremovable(self, value):
        self._setBool(11, value)

    def getIsAssignDisabled(self):
        return self._getBool(12)

    def setIsAssignDisabled(self, value):
        self._setBool(12, value)

    def getSlotLevelNeeded(self):
        return self._getNumber(13)

    def setSlotLevelNeeded(self, value):
        self._setNumber(13, value)

    def getIsAssigned(self):
        return self._getBool(14)

    def setIsAssigned(self, value):
        self._setBool(14, value)

    def getIsRemoved(self):
        return self._getBool(15)

    def setIsRemoved(self, value):
        self._setBool(15, value)

    def getIsInOtherDetachment(self):
        return self._getBool(16)

    def setIsInOtherDetachment(self, value):
        self._setBool(16, value)

    def getRemoveTime(self):
        return self._getNumber(17)

    def setRemoveTime(self, value):
        self._setNumber(17, value)

    def _initialize(self):
        super(InstructorPageViewModel, self)._initialize()
        self._addViewModelProperty('information', InstructorPageInfoModel())
        self._addViewModelProperty('commander', CommanderModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addViewModelProperty('price', PriceModel())
        self._addNumberProperty('id', 0)
        self._addResourceProperty('background', R.invalid())
        self._addStringProperty('icon', '')
        self._addNumberProperty('grade', 0)
        self._addStringProperty('gender', '')
        self._addBoolProperty('isUnremovable', False)
        self._addBoolProperty('isAssignDisabled', False)
        self._addNumberProperty('slotLevelNeeded', 0)
        self._addBoolProperty('isAssigned', False)
        self._addBoolProperty('isRemoved', False)
        self._addBoolProperty('isInOtherDetachment', False)
        self._addNumberProperty('removeTime', 0)
        self.onAssignClick = self._addCommand('onAssignClick')
        self.onDemountClick = self._addCommand('onDemountClick')
        self.onRecoverClick = self._addCommand('onRecoverClick')
        self.onVoiceListenClick = self._addCommand('onVoiceListenClick')
        self.onVoiceToggleClick = self._addCommand('onVoiceToggleClick')
