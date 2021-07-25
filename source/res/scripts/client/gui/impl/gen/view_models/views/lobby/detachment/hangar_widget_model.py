# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/hangar_widget_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_with_points_model import DetachmentWithPointsModel
from gui.impl.gen.view_models.views.lobby.detachment.common.rose_model import RoseModel

class HangarWidgetModel(ViewModel):
    __slots__ = ('onCommanderClicked', 'onRoseClicked', 'onSkillPointsClicked', 'onInstructorSlotClicked', 'onDogClicked')

    def __init__(self, properties=5, commands=5):
        super(HangarWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentInfo(self):
        return self._getViewModel(0)

    @property
    def roseModel(self):
        return self._getViewModel(1)

    def getIsLinked(self):
        return self._getBool(2)

    def setIsLinked(self, value):
        self._setBool(2, value)

    def getIsDisabled(self):
        return self._getBool(3)

    def setIsDisabled(self, value):
        self._setBool(3, value)

    def getIsLastCrewInBarracks(self):
        return self._getBool(4)

    def setIsLastCrewInBarracks(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(HangarWidgetModel, self)._initialize()
        self._addViewModelProperty('detachmentInfo', DetachmentWithPointsModel())
        self._addViewModelProperty('roseModel', RoseModel())
        self._addBoolProperty('isLinked', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isLastCrewInBarracks', False)
        self.onCommanderClicked = self._addCommand('onCommanderClicked')
        self.onRoseClicked = self._addCommand('onRoseClicked')
        self.onSkillPointsClicked = self._addCommand('onSkillPointsClicked')
        self.onInstructorSlotClicked = self._addCommand('onInstructorSlotClicked')
        self.onDogClicked = self._addCommand('onDogClicked')
