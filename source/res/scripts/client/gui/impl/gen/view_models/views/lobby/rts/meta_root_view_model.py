# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/meta_root_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.meta_tab_model import MetaTabModel

class MetaRootViewModel(ViewModel):
    __slots__ = ('onClose', 'onAbout', 'onTabClick')

    def __init__(self, properties=2, commands=3):
        super(MetaRootViewModel, self).__init__(properties=properties, commands=commands)

    def getTabs(self):
        return self._getArray(0)

    def setTabs(self, value):
        self._setArray(0, value)

    def getTabId(self):
        return self._getString(1)

    def setTabId(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MetaRootViewModel, self)._initialize()
        self._addArrayProperty('tabs', Array())
        self._addStringProperty('tabId', '')
        self.onClose = self._addCommand('onClose')
        self.onAbout = self._addCommand('onAbout')
        self.onTabClick = self._addCommand('onTabClick')
