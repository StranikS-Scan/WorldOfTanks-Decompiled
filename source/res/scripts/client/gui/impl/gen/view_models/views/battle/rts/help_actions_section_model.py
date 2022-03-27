# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/rts/help_actions_section_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.rts.help_actions_item_model import HelpActionsItemModel

class HelpActionsSectionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(HelpActionsSectionModel, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getResource(0)

    def setHeader(self, value):
        self._setResource(0, value)

    def getArticles(self):
        return self._getArray(1)

    def setArticles(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(HelpActionsSectionModel, self)._initialize()
        self._addResourceProperty('header', R.invalid())
        self._addArrayProperty('articles', Array())
