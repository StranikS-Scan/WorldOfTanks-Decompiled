# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/tutorial/tutorial_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.tutorial.component_model import ComponentModel
from gui.impl.gen.view_models.common.tutorial.criterion_model import CriterionModel
from gui.impl.gen.view_models.common.tutorial.descriptions_model import DescriptionsModel
from gui.impl.gen.view_models.common.tutorial.effect_model import EffectModel
from gui.impl.gen.view_models.common.tutorial.triggers_model import TriggersModel
from gui.impl.gen.view_models.common.tutorial.view_criterion_model import ViewCriterionModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class TutorialModel(ViewModel):
    __slots__ = ('onComponentFound', 'onComponentDisposed', 'onEffectCompleted', 'onComponentUpdate', 'onTriggerActivated')

    def __init__(self, properties=7, commands=5):
        super(TutorialModel, self).__init__(properties=properties, commands=commands)

    @property
    def effects(self):
        return self._getViewModel(0)

    @property
    def triggers(self):
        return self._getViewModel(1)

    @property
    def foundComponents(self):
        return self._getViewModel(2)

    @property
    def descriptions(self):
        return self._getViewModel(3)

    @property
    def criteria(self):
        return self._getViewModel(4)

    @property
    def viewCriteria(self):
        return self._getViewModel(5)

    def getEnabled(self):
        return self._getBool(6)

    def setEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(TutorialModel, self)._initialize()
        self._addViewModelProperty('effects', ListModel())
        self._addViewModelProperty('triggers', ListModel())
        self._addViewModelProperty('foundComponents', ListModel())
        self._addViewModelProperty('descriptions', DescriptionsModel())
        self._addViewModelProperty('criteria', ListModel())
        self._addViewModelProperty('viewCriteria', ListModel())
        self._addBoolProperty('enabled', False)
        self.onComponentFound = self._addCommand('onComponentFound')
        self.onComponentDisposed = self._addCommand('onComponentDisposed')
        self.onEffectCompleted = self._addCommand('onEffectCompleted')
        self.onComponentUpdate = self._addCommand('onComponentUpdate')
        self.onTriggerActivated = self._addCommand('onTriggerActivated')
