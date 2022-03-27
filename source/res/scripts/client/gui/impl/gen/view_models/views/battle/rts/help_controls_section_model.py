# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/rts/help_controls_section_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.rts.help_controls_article_model import HelpControlsArticleModel

class HelpControlsSectionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HelpControlsSectionModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getHeader(self):
        return self._getResource(1)

    def setHeader(self, value):
        self._setResource(1, value)

    def getArticles(self):
        return self._getArray(2)

    def setArticles(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(HelpControlsSectionModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('header', R.invalid())
        self._addArrayProperty('articles', Array())
