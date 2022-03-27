# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/rts/help_controls_article_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.rts.help_controls_article_item_model import HelpControlsArticleItemModel

class HelpControlsArticleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(HelpControlsArticleModel, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getResource(0)

    def setHeader(self, value):
        self._setResource(0, value)

    def getHelpItems(self):
        return self._getArray(1)

    def setHelpItems(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(HelpControlsArticleModel, self)._initialize()
        self._addResourceProperty('header', R.invalid())
        self._addArrayProperty('helpItems', Array())
