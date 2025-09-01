# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/hub_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tab_model import TabModel

class HubViewModel(ViewModel):
    __slots__ = ('onTabChange', 'onContentLayoutChanged')

    def __init__(self, properties=2, commands=2):
        super(HubViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentTabId(self):
        return self._getString(0)

    def setCurrentTabId(self, value):
        self._setString(0, value)

    def getTabsList(self):
        return self._getArray(1)

    def setTabsList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getTabsListType():
        return TabModel

    def _initialize(self):
        super(HubViewModel, self)._initialize()
        self._addStringProperty('currentTabId', '')
        self._addArrayProperty('tabsList', Array())
        self.onTabChange = self._addCommand('onTabChange')
        self.onContentLayoutChanged = self._addCommand('onContentLayoutChanged')
