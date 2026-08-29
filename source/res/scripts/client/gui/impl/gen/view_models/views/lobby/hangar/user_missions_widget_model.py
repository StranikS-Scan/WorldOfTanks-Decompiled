# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/user_missions_widget_model.py
from frameworks.wulf import Array, Map, ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_plugin_model import UserMissionsPluginModel
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_slide_model import UserMissionsSlideModel

class UserMissionsWidgetModel(ViewModel):
    __slots__ = ('onSlideChanged',)

    def __init__(self, properties=4, commands=1):
        super(UserMissionsWidgetModel, self).__init__(properties=properties, commands=commands)

    def getSlides(self):
        return self._getArray(0)

    def setSlides(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSlidesType():
        return UserMissionsSlideModel

    def getSelectedSlide(self):
        return self._getString(1)

    def setSelectedSlide(self, value):
        self._setString(1, value)

    def getPlugins(self):
        return self._getMap(2)

    def setPlugins(self, value):
        self._setMap(2, value)

    @staticmethod
    def getPluginsType():
        return (int, UserMissionsPluginModel)

    def getVisibleGroups(self):
        return self._getArray(3)

    def setVisibleGroups(self, value):
        self._setArray(3, value)

    @staticmethod
    def getVisibleGroupsType():
        return unicode

    def _initialize(self):
        super(UserMissionsWidgetModel, self)._initialize()
        self._addArrayProperty('slides', Array())
        self._addStringProperty('selectedSlide', '')
        self._addMapProperty('plugins', Map(int, UserMissionsPluginModel))
        self._addArrayProperty('visibleGroups', Array())
        self.onSlideChanged = self._addCommand('onSlideChanged')
