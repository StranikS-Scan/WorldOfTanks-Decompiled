# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/snow_maidens/snow_maidens_intro_view_model.py
from frameworks.wulf import ViewModel

class SnowMaidensIntroViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick',)

    def __init__(self, properties=0, commands=1):
        super(SnowMaidensIntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(SnowMaidensIntroViewModel, self)._initialize()
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
