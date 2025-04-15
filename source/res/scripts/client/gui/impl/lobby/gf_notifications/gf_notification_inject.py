# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/gf_notification_inject.py
import logging
from gui.shared.system_factory import collectGamefaceNotifications
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
_logger = logging.getLogger(__name__)

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
    def get(gfTemplate):
        resId, clazz = collectGamefaceNotifications().get(gfTemplate, None)
        if clazz is not None:
            return (resId, clazz)
        else:
            _logger.error("can't fined presenter for %s", gfTemplate)
            return
