# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/vehicle_menu_model.py
from frameworks.wulf import Array, Map, ViewModel

class VehicleMenuModel(ViewModel):
    __slots__ = ('onNavigate',)
    DISABLED = 'disabled'
    ENABLED = 'enabled'
    WARNING = 'warning'
    CRITICAL = 'critical'
    UNAVAILABLE = 'unavailable'
    BATTLE_NEEDED = 'battleNeeded'
    CREW_MEMBERS_RETIRED = 'crewMembersRetired'
    CUSTOMIZATION = 'customization'
    CREW_AUTO_RETURN = 'crewAutoReturn'
    CREW_RETRAIN = 'crewRetrain'
    QUICK_TRAINING = 'quickTraining'
    CREW_OUT = 'crewOut'
    CREW_BACK = 'crewBack'
    EASY_EQUIP = 'easyEquip'
    ARMOR_INSPECTOR = 'armorInspector'
    FIELD_MODIFICATION = 'fieldModification'
    NATION_CHANGE = 'nationChange'
    RESEARCH = 'research'
    ABOUT_VEHICLE = 'aboutVehicle'
    COMPARE = 'compare'
    REPAIRS = 'repairs'
    VEH_SKILL_TREE = 'vehSkillTree'

    def __init__(self, properties=2, commands=1):
        super(VehicleMenuModel, self).__init__(properties=properties, commands=commands)

    def getMenuItems(self):
        return self._getMap(0)

    def setMenuItems(self, value):
        self._setMap(0, value)

    @staticmethod
    def getMenuItemsType():
        return (unicode, unicode)

    def getResearchItems(self):
        return self._getArray(1)

    def setResearchItems(self, value):
        self._setArray(1, value)

    @staticmethod
    def getResearchItemsType():
        return unicode

    def _initialize(self):
        super(VehicleMenuModel, self)._initialize()
        self._addMapProperty('menuItems', Map(unicode, unicode))
        self._addArrayProperty('researchItems', Array())
        self.onNavigate = self._addCommand('onNavigate')
