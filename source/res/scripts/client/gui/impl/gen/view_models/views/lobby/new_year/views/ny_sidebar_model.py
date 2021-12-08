# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_sidebar_model.py
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_common_model import NySidebarCommonModel

class NySidebarModel(NySidebarCommonModel):
    __slots__ = ('onSideBarBtnClick',)
    VIEW_NAME_GLADE = 'glade'
    VIEW_NAME_REWARDS = 'rewards'
    VIEW_NAME_COLLECTIONS = 'collections'

    def __init__(self, properties=3, commands=1):
        super(NySidebarModel, self).__init__(properties=properties, commands=commands)

    def getViewName(self):
        return self._getString(2)

    def setViewName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NySidebarModel, self)._initialize()
        self._addStringProperty('viewName', '')
        self.onSideBarBtnClick = self._addCommand('onSideBarBtnClick')
