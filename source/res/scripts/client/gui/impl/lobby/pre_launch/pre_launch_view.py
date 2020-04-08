# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pre_launch/pre_launch_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pre_launch.pre_launch_view_model import PreLaunchViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.game_control import IPreLaunchController
from skeletons.gui.shared import IItemsCache

class PreLaunchView(ViewImpl):
    __slots__ = ()
    __preLaunchController = dependency.descriptor(IPreLaunchController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.pre_launch.PreLaunchView())
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.COMPONENT
        settings.model = PreLaunchViewModel()
        super(PreLaunchView, self).__init__(settings)

    def _initialize(self, *args, **kwargs):
        super(PreLaunchView, self)._initialize(*args, **kwargs)
        self.__preLaunchController.onPrelaunchCountChanged += self._onCounterChanged
        self.__preLaunchController.onPrelaunchTextChanged += self._updateText

    def _finalize(self, *args, **kwargs):
        super(PreLaunchView, self)._finalize(*args, **kwargs)
        self.__preLaunchController.onPrelaunchCountChanged -= self._onCounterChanged
        self.__preLaunchController.onPrelaunchTextChanged -= self._updateText

    def _onLoading(self):
        with self.viewModel.transaction() as model:
            self._updateText(model=model)
            model.setProgress(self.__preLaunchController.getCount())

    def _onCounterChanged(self):
        with self.viewModel.transaction() as model:
            model.setProgress(self.__preLaunchController.getCount())

    @replaceNoneKwargsModel
    def _updateText(self, model=None):
        model.setIsTeaserHidden(not self.__preLaunchController.needToShowTeaser())
        textID = R.strings.pre_launch.quest_pre_launch.num(self.__preLaunchController.getTextID())()
        teaser = backport.text(textID)
        model.setTiser(teaser)

    @property
    def viewModel(self):
        return super(PreLaunchView, self).getViewModel()
