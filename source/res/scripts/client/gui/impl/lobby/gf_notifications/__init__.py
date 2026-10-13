# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/__init__.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.paragons.notifications.paragons_coins_notification_view import ParagonsCoinsNotification
from messenger.m_constants import GFNotificationTemplates
from simple_notification import SimpleNotification
from session_progress_rewards_notification import SessionProgressRewardsNotification
from debug_utils import LOG_ERROR
from gui.impl.gen import R
NOTIFICATION_PRESENTERS = {GFNotificationTemplates.CUSTOM_PARAGONS_COINS_NOTIFICATION: (R.views.lobby.paragons.notifications.ParagonsCoinsNotificationView(), ParagonsCoinsNotification)}

class GFNotificationInject(InjectComponentAdaptor):

    def __init__(self, gfViewName, isPopUp, linkageData, *args, **kwargs):
        self.__gfViewName = gfViewName
        self.__isPopUp = isPopUp
        self.__linkageData = linkageData
        super(GFNotificationInject, self).__init__()

    def _makeInjectView(self):
        resId, presenter = PresentersFactory.get(self.__gfViewName)
        return presenter(resId, self.__isPopUp, self.__linkageData)


class PresentersFactory(object):

    @staticmethod
    def get(viewName):
        resId, clazz = NOTIFICATION_PRESENTERS.get(viewName, None)
        if clazz is not None:
            return (resId, clazz)
        else:
            LOG_ERROR("Cant fined presenter for '%s'" % viewName)
            return

    @staticmethod
    def add(viewName, resId, clazz):
        NOTIFICATION_PRESENTERS[viewName] = (resId, clazz)


PresentersFactory.add('SessionProgressRewardsNotification', R.views.lobby.daily.SessionProgressRewardsNotificationView(), SessionProgressRewardsNotification)
