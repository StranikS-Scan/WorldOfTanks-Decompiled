# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/edit_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.achievements.views.achievement_section_model import AchievementSectionModel

class EditViewModel(ViewModel):
    __slots__ = ('onChangeAutoSelect', 'onReplaceAchievement', 'onSave', 'onCancel', 'onExitConfirm', 'onHideFirstEntryState')

    def __init__(self, properties=5, commands=6):
        super(EditViewModel, self).__init__(properties=properties, commands=commands)

    def getIsAutoSelect(self):
        return self._getBool(0)

    def setIsAutoSelect(self, value):
        self._setBool(0, value)

    def getIsFirstEntry(self):
        return self._getBool(1)

    def setIsFirstEntry(self, value):
        self._setBool(1, value)

    def getHasChanges(self):
        return self._getBool(2)

    def setHasChanges(self, value):
        self._setBool(2, value)

    def getSelectedAchievements(self):
        return self._getArray(3)

    def setSelectedAchievements(self, value):
        self._setArray(3, value)

    @staticmethod
    def getSelectedAchievementsType():
        return AchievementModel

    def getAchievementSections(self):
        return self._getArray(4)

    def setAchievementSections(self, value):
        self._setArray(4, value)

    @staticmethod
    def getAchievementSectionsType():
        return AchievementSectionModel

    def _initialize(self):
        super(EditViewModel, self)._initialize()
        self._addBoolProperty('isAutoSelect', False)
        self._addBoolProperty('isFirstEntry', False)
        self._addBoolProperty('hasChanges', False)
        self._addArrayProperty('selectedAchievements', Array())
        self._addArrayProperty('achievementSections', Array())
        self.onChangeAutoSelect = self._addCommand('onChangeAutoSelect')
        self.onReplaceAchievement = self._addCommand('onReplaceAchievement')
        self.onSave = self._addCommand('onSave')
        self.onCancel = self._addCommand('onCancel')
        self.onExitConfirm = self._addCommand('onExitConfirm')
        self.onHideFirstEntryState = self._addCommand('onHideFirstEntryState')
