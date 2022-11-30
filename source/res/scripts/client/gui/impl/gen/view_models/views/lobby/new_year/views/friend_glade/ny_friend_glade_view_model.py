# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/friend_glade/ny_friend_glade_view_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_hangar_name_model import NyHangarNameModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_toy_slots_bar_model import NyToySlotsBarModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_widget_resource_box_model import NyWidgetResourceBoxModel
from gui.impl.gen.view_models.views.lobby.new_year.views.base.ny_scene_rotatable_view import NySceneRotatableView
from gui.impl.gen.view_models.views.lobby.new_year.views.friend_glade.ny_resources_view_model import NyResourcesViewModel

class NyFriendGladeViewModel(NySceneRotatableView):
    __slots__ = ('collect', 'setFavoriteFriend', 'goToFriends')

    def __init__(self, properties=8, commands=5):
        super(NyFriendGladeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def resourceBoxModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getResourceBoxModelType():
        return NyWidgetResourceBoxModel

    @property
    def resourcesViewModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getResourcesViewModelType():
        return NyResourcesViewModel

    @property
    def toySlotsBar(self):
        return self._getViewModel(3)

    @staticmethod
    def getToySlotsBarType():
        return NyToySlotsBarModel

    @property
    def hangarName(self):
        return self._getViewModel(4)

    @staticmethod
    def getHangarNameType():
        return NyHangarNameModel

    def getTabName(self):
        return self._getString(5)

    def setTabName(self, value):
        self._setString(5, value)

    def getIsFirstVisit(self):
        return self._getBool(6)

    def setIsFirstVisit(self, value):
        self._setBool(6, value)

    def getFriendName(self):
        return self._getString(7)

    def setFriendName(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(NyFriendGladeViewModel, self)._initialize()
        self._addViewModelProperty('resourceBoxModel', NyWidgetResourceBoxModel())
        self._addViewModelProperty('resourcesViewModel', NyResourcesViewModel())
        self._addViewModelProperty('toySlotsBar', NyToySlotsBarModel())
        self._addViewModelProperty('hangarName', NyHangarNameModel())
        self._addStringProperty('tabName', '')
        self._addBoolProperty('isFirstVisit', False)
        self._addStringProperty('friendName', '')
        self.collect = self._addCommand('collect')
        self.setFavoriteFriend = self._addCommand('setFavoriteFriend')
        self.goToFriends = self._addCommand('goToFriends')
