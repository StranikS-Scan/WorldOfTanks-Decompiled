# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_intro_view_model.py
from frameworks.wulf import ViewModel

class PersonalMissionsIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onContinue', 'onVideoOpen', 'onMoreInfo')

    def __init__(self, properties=0, commands=4):
        super(PersonalMissionsIntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(PersonalMissionsIntroViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onContinue = self._addCommand('onContinue')
        self.onVideoOpen = self._addCommand('onVideoOpen')
        self.onMoreInfo = self._addCommand('onMoreInfo')
