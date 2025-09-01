# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/event_banners_list_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.event_banner_model import EventBannerModel

class EventBannersListModel(ViewModel):
    __slots__ = ('onEventClick', 'onAppearAnimationPlayed')

    def __init__(self, properties=1, commands=2):
        super(EventBannersListModel, self).__init__(properties=properties, commands=commands)

    def getBanners(self):
        return self._getArray(0)

    def setBanners(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBannersType():
        return EventBannerModel

    def _initialize(self):
        super(EventBannersListModel, self)._initialize()
        self._addArrayProperty('banners', Array())
        self.onEventClick = self._addCommand('onEventClick')
        self.onAppearAnimationPlayed = self._addCommand('onAppearAnimationPlayed')
