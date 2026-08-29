# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/user_missions_presenter.py
from __future__ import absolute_import
import typing
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_plugin_model import UserMissionsPluginModel
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_slide_model import UserMissionsSlideModel
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_widget_model import UserMissionsWidgetModel
from gui.impl.lobby.user_missions.hangar_widget.plugins import IUserMissionPlugin
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.event_banners_presenter import EventBannersPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.quests_presenter import QuestsPresenter
from gui.impl.lobby.user_missions.hangar_widget.services import IMissionsContainerService, IUserMissionWidgetService
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import Array
INVALID_GROUP_INDEX = -1

class UserMissionsPresenter(ViewComponent[UserMissionsWidgetModel]):
    _missionsContainerService = dependency.descriptor(IMissionsContainerService)
    _widgetService = dependency.descriptor(IUserMissionWidgetService)
    _WIDGET_ALIAS = R.aliases.user_missions.hangarWidget
    _CHILDREN = {_WIDGET_ALIAS.BattlePass(): BattlePassPresenter,
     _WIDGET_ALIAS.Events(): EventBannersPresenter,
     _WIDGET_ALIAS.Quests(): QuestsPresenter}
    _WIDGET_SLIDER_ID = 'missionsSlider'
    _DEFAULT_SLIDE_ID = 'missions'

    def __init__(self):
        super(UserMissionsPresenter, self).__init__(model=UserMissionsWidgetModel)

    @property
    def viewModel(self):
        return super(UserMissionsPresenter, self).getViewModel()

    @property
    def slides(self):
        return umgConfigSchema.getModel().slides

    def _onLoading(self, *args, **kwargs):
        super(UserMissionsPresenter, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            self._updateSlides(vm)
        self._addChildren()
        self._updatePlugins()

    def _getEvents(self):
        return ((self._missionsContainerService.onShowPlugin, self._onShowPlugin),
         (self._missionsContainerService.onHidePlugin, self._onHidePlugin),
         (self._widgetService.onVisibleGroupsChanged, self._onGroupVisibilityChanged),
         (self.viewModel.onSlideChanged, self._onSlideChanged),
         (g_playerEvents.onConfigModelUpdated, self.__onConfigModelUpdated))

    def _onGroupVisibilityChanged(self, groupName, isVisible):
        with self.viewModel.transaction() as vm:
            groups = vm.getVisibleGroups()
            if isVisible:
                if groupName in groups:
                    return
                groups.addString(groupName)
            else:
                if groupName not in groups:
                    return
                self.__removeGroup(groups, groupName)
            groups.invalidate()

    def _updateSlides(self, vm):
        if self.slides:
            slides = vm.getSlides()
            slides.clear()
            for slide in self.slides:
                if not slide.enabled:
                    continue
                slideModel = UserMissionsSlideModel()
                slideModel.setId(slide.name)
                slideModel.setWeight(slide.priority)
                slides.addViewModel(slideModel)

        self._updateSelectedSlide(vm)

    def _updateSelectedSlide(self, vm):
        slideId = self._missionsContainerService.getSelectedSlide(self._WIDGET_SLIDER_ID) or self._DEFAULT_SLIDE_ID
        vm.setSelectedSlide(slideId)

    def _addChildren(self):
        with self.viewModel.transaction() as vm:
            groups = vm.getVisibleGroups()
            for posId, presenterClass in self._CHILDREN.items():
                self._addChild(posId)
                child = self._getChild(posId)
                if child is not None and child.isVisible() and presenterClass.GROUP:
                    groups.addString(presenterClass.GROUP)

            groups.invalidate()
        return

    def _updatePlugins(self):
        for alias in self._getChildComponents():
            if alias not in self._childrenUidByPosition:
                continue
            plugin = self.getChildByPosId(alias)
            if isinstance(plugin, IUserMissionPlugin):
                self._addPlugin(plugin)

    def _addPlugin(self, plugin):
        with self.viewModel.transaction() as vm:
            plugins = vm.getPlugins()
            pluginModel = UserMissionsPluginModel()
            pluginModel.setUrl(plugin.getPathToResource())
            dependenciesModel = pluginModel.getDependencies()
            for path in plugin.getDependencies():
                dependenciesModel.addString(path)

            plugins.set(plugin.getViewAlias(), pluginModel)

    def _onShowPlugin(self, plugin):
        if plugin.getViewAlias() not in self._childrenUidByPosition:
            self._registerChild(plugin.getViewAlias(), plugin())
        self._addPlugin(plugin)

    def _onHidePlugin(self, pluginAlias):
        self._removeChild(pluginAlias)
        with self.viewModel.transaction() as vm:
            plugins = vm.getPlugins()
            plugins.remove(pluginAlias)

    def _onSlideChanged(self, selectedSlide):
        self._missionsContainerService.onSlideChanged(selectedSlide)
        with self.viewModel.transaction() as vm:
            self._updateSelectedSlide(vm)

    def _addChild(self, posId):
        child = self._getChild(posId)
        if child or posId not in self._CHILDREN:
            return
        child = self._CHILDREN[posId]()
        self._registerChild(posId, child)

    def _removeChild(self, posId):
        uid = self._childrenUidByPosition.get(posId, None)
        self._unregisterChild(uid, True)
        return

    def _getChildComponents(self):
        return self._missionsContainerService.getVisiblePlugins()

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            with self.viewModel.transaction() as vm:
                self._updateSlides(vm)
                vm.getSlides().invalidate()

    def __removeGroup(self, groups, groupName):
        index = INVALID_GROUP_INDEX
        for i, item in enumerate(groups):
            if str(item) == groupName:
                index = i
                break

        if index > INVALID_GROUP_INDEX:
            groups.remove(index)
