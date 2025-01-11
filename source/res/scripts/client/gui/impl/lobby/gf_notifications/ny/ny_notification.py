# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_notification.py
from helpers import dependency
from constants import DEFAULT_HANGAR_SCENE
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.lobby.gf_notifications.ny.notifications_utils import createNavigationAction, createStylePreviewAction
from gui.impl.lobby.gf_notifications.base.notification_base import NotificationBase
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from skeletons.new_year import INewYearController
from skeletons.gui.game_control import IHangarSpaceSwitchController, IGFNotificationsController
from skeletons.new_year import IFriendServiceController

def _isRandomPrbActive(prbEntity):
    return False if prbEntity is None else bool(prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANDOM)


class NyNotification(NotificationBase, IPrbListener):
    _nyController = dependency.descriptor(INewYearController)
    __hangarSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __gfNotificationController = dependency.descriptor(IGFNotificationsController)
    __friendController = dependency.descriptor(IFriendServiceController)
    __slots__ = ()

    @property
    def currentHangarAcceptable(self):
        return self.__hangarSwitchController.currentSceneName == DEFAULT_HANGAR_SCENE and _isRandomPrbActive(self.prbEntity)

    def _onLoading(self, *args, **kwargs):
        super(NyNotification, self)._onLoading(*args, **kwargs)
        self._update()
        self.__gfNotificationController.onBattleQueueStateUpdated += self._update

    def _finalize(self):
        self.__gfNotificationController.onBattleQueueStateUpdated -= self._update
        super(NyNotification, self)._finalize()

    def _update(self):
        pass

    def _navigateToNy(self, objectName, viewAlias, executeBeforeSwitch=None):
        if self._canNavigate():
            action = createNavigationAction(objectName, viewAlias, executeBeforeSwitch=executeBeforeSwitch)
            if self.currentHangarAcceptable:
                action()
            else:
                self.__gfNotificationController.selectRandomBattle(action)

    def _canShowStyle(self):
        return not g_currentPreviewVehicle.isPresent()

    def _showStylePreview(self, style):
        if self._canNavigate():
            action = createStylePreviewAction(style)
            if self.currentHangarAcceptable:
                if self.__friendController.isInFriendHangar:
                    self.__friendController.leaveFriendHangar()
                action()
            else:
                self.__gfNotificationController.selectRandomBattle(action)
