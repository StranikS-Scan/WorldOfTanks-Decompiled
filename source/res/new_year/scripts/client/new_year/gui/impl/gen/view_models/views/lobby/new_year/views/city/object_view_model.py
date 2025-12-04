# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/city/object_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.group_slots_model import GroupSlotsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.customization_zone.customization_zone_model import CustomizationZoneModel

class ObjectViewModel(ViewModel):
    __slots__ = ('onGoToCustomizationObject', 'onClose', 'onEscape')

    def __init__(self, properties=5, commands=3):
        super(ObjectViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def groupSlots(self):
        return self._getViewModel(0)

    @staticmethod
    def getGroupSlotsType():
        return GroupSlotsModel

    @property
    def customizationZoneObject(self):
        return self._getViewModel(1)

    @staticmethod
    def getCustomizationZoneObjectType():
        return CustomizationZoneModel

    def getCurrentObject(self):
        return self._getString(2)

    def setCurrentObject(self, value):
        self._setString(2, value)

    def getNextObject(self):
        return self._getString(3)

    def setNextObject(self, value):
        self._setString(3, value)

    def getPrevObject(self):
        return self._getString(4)

    def setPrevObject(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(ObjectViewModel, self)._initialize()
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addViewModelProperty('customizationZoneObject', CustomizationZoneModel())
        self._addStringProperty('currentObject', '')
        self._addStringProperty('nextObject', '')
        self._addStringProperty('prevObject', '')
        self.onGoToCustomizationObject = self._addCommand('onGoToCustomizationObject')
        self.onClose = self._addCommand('onClose')
        self.onEscape = self._addCommand('onEscape')
