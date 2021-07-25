# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/navigation_view_model.py
from frameworks.wulf import ViewModel

class NavigationViewModel(ViewModel):
    __slots__ = ('onClose', 'onLoadPage', 'onBack')
    VEHICLE_LIST = 'vehicle_list'
    BARRACK_DETACHMENT = 'barrack_detachment'
    BARRACK_INSTRUCTOR = 'barrack_instructor'
    BARRACK_RECRUIT = 'barrack_recruit'
    PERSONAL_CASE_BASE = 'personal_case'
    PERSONAL_CASE_PERKS_MATRIX = 'personal_case_perks_matrix'
    PERSONAL_CASE_PROFILE = 'personal_case_profile'
    PERSONAL_CASE_PROGRESSION = 'personal_case_progression'
    INSTRUCTORS_LIST = 'instructors_list'
    INSTRUCTOR_PAGE = 'instructor_page'
    INSTRUCTOR_UNPACKING = 'instructor_unpacking'
    INSTRUCTORS_OFFICE = 'instructors_office'
    LEARNED_SKILLS = 'learned_skills'
    MOBILIZATION = 'mobilization'
    ASSIGN_TO_VEHICLE = 'assignToVehicle'
    NO_DETACHMENT = 'noDetachment'
    NEW_LEVEL = 'newLevel'

    def __init__(self, properties=2, commands=3):
        super(NavigationViewModel, self).__init__(properties=properties, commands=commands)

    def getPreviousViewId(self):
        return self._getString(0)

    def setPreviousViewId(self, value):
        self._setString(0, value)

    def getCurrentViewId(self):
        return self._getString(1)

    def setCurrentViewId(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NavigationViewModel, self)._initialize()
        self._addStringProperty('previousViewId', '')
        self._addStringProperty('currentViewId', '')
        self.onClose = self._addCommand('onClose')
        self.onLoadPage = self._addCommand('onLoadPage')
        self.onBack = self._addCommand('onBack')
