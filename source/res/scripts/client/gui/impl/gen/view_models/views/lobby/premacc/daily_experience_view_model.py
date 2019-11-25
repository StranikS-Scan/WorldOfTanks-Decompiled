# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/daily_experience_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.daily_experience_base_model import DailyExperienceBaseModel

class DailyExperienceViewModel(DailyExperienceBaseModel):
    __slots__ = ('onGoToContentPage', 'onBackBtnClicked')

    def __init__(self, properties=5, commands=2):
        super(DailyExperienceViewModel, self).__init__(properties=properties, commands=commands)

    def getBackBtnLabel(self):
        return self._getResource(4)

    def setBackBtnLabel(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(DailyExperienceViewModel, self)._initialize()
        self._addResourceProperty('backBtnLabel', R.invalid())
        self.onGoToContentPage = self._addCommand('onGoToContentPage')
        self.onBackBtnClicked = self._addCommand('onBackBtnClicked')
