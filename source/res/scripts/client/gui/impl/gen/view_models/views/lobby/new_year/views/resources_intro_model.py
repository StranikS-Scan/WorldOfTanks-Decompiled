# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/resources_intro_model.py
from frameworks.wulf import ViewModel

class ResourcesIntroModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(ResourcesIntroModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ResourcesIntroModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
