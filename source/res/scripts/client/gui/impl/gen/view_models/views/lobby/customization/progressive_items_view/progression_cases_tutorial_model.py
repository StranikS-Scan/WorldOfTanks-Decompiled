# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progressive_items_view/progression_cases_tutorial_model.py
from frameworks.wulf import ViewModel

class ProgressionCasesTutorialModel(ViewModel):
    __slots__ = ('onClose', 'showVideo')

    def __init__(self, properties=0, commands=2):
        super(ProgressionCasesTutorialModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ProgressionCasesTutorialModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.showVideo = self._addCommand('showVideo')
