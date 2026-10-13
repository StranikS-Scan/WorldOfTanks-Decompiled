# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/portal_battle_queue_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui.prb_control import prbEntityProperty
from helpers import dependency
from gui.impl.pub import ViewImpl
from portal.gui.impl.gen.view_models.views.lobby.portal_battle_queue_view_model import PortalBattleQueueViewModel, Complexity
from portal.skeletons.portal_event_controller import IPortalEventController
from skeletons.gui.game_control import IHangarFeatureStateController
from gui.shared.view_helpers.blur_manager import CachedBlur
from portal.sounds.sound_constants import PORTAL_BATTLE_QUEUE_SOUND_SPACE

class PortalBattleQueueView(ViewImpl):
    __slots__ = ('__blur',)
    __portalEventController = dependency.descriptor(IPortalEventController)
    __hangarFeatureStateController = dependency.descriptor(IHangarFeatureStateController)
    _COMMON_SOUND_SPACE = PORTAL_BATTLE_QUEUE_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PortalBattleQueueViewModel()
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.SUB_VIEW)
        super(PortalBattleQueueView, self).__init__(settings)

    def _onLoaded(self, *args, **kwargs):
        self.__hangarFeatureStateController.enter(self.layoutID, doHideHeader=True)

    @property
    def viewModel(self):
        return super(PortalBattleQueueView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def _finalize(self):
        self.__blur.fini()
        self._removeListeners()
        self.__hangarFeatureStateController.exit(self.layoutID)
        super(PortalBattleQueueView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(PortalBattleQueueView, self)._onLoading(*args, **kwargs)
        self._addListeners()
        self._loadModel()

    def _addListeners(self):
        self.viewModel.onLeave += self.__onLeave

    def _removeListeners(self):
        self.viewModel.onLeave -= self.__onLeave

    def _loadModel(self):
        complexity = Complexity(self.__portalEventController.battleLevel)
        with self.viewModel.transaction() as model:
            model.setComplexity(complexity)

    def __onLeave(self):
        self.prbEntity.exitFromQueue()
