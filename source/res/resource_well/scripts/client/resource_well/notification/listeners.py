# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/notification/listeners.py
import logging
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from notification.listeners import _NotificationListener
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.gui.feature.resource_well_helpers import isStartNotificationShown, isFinishNotificationShown, setStartNotificationShown, setFinishNotificationShown
from resource_well.notification.decorators import ResourceWellStartDecorator
from shared_utils import first
from skeletons.gui.resource_well import IResourceWellController
_logger = logging.getLogger(__name__)

class ResourceWellListener(_NotificationListener):
    __RESOURCE_WELL_MESSAGES = R.strings.messenger.serviceChannelMessages.resourceWell
    __START_ENTITY_ID = 0
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        self.__prevIsEnabled = None
        super(ResourceWellListener, self).__init__()
        return

    def start(self, model):
        result = super(ResourceWellListener, self).start(model)
        if result:
            self.__resourceWell.onEventUpdated += self.__onEventStateUpdated
            self.__resourceWell.onSettingsChanged += self.__onEventStateUpdated
            self.__tryNotify()
        return result

    def stop(self):
        self.__resourceWell.onEventUpdated -= self.__onEventStateUpdated
        self.__resourceWell.onSettingsChanged -= self.__onEventStateUpdated
        super(ResourceWellListener, self).stop()

    def __onEventStateUpdated(self):
        self.__tryNotify()

    def __tryNotify(self):
        self.__checkPause()
        if self.__resourceWell.isActive() and not isStartNotificationShown():
            self.__pushStarted()
        elif self.__resourceWell.isFinished() and isStartNotificationShown() and not isFinishNotificationShown():
            self.__pushFinished()

    def __checkPause(self):
        if not self.__resourceWell.isStarted() or self.__resourceWell.isFinished():
            self.__prevIsEnabled = None
            return
        elif self.__prevIsEnabled is None and self.__resourceWell.isStarted() and not self.__resourceWell.isFinished():
            self.__prevIsEnabled = self.__resourceWell.isEnabled()
            return
        else:
            isEnabled = self.__resourceWell.isEnabled()
            if self.__prevIsEnabled is not isEnabled:
                self.__prevIsEnabled = isEnabled
                if isEnabled:
                    self.__pushEnabled()
                else:
                    self.__pushPaused()
            return

    def __pushPaused(self):
        text = backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.pause.text())
        SystemMessages.pushMessage(text=text, type=SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)

    def __pushEnabled(self):
        text = backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.enabled.text())
        SystemMessages.pushMessage(text=text, type=SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)

    def __pushStarted(self):
        model = self._model()
        if model is not None:
            if self.__resourceWell.getPurchaseMode() in (PurchaseMode.SEQUENTIAL_PRODUCT, PurchaseMode.ONE_SERIAL_PRODUCT):
                text = self.__getSingleVehicleText()
            else:
                text = self.__getTwoVehiclesText()
            title = backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.start.title())
            messageData = {'title': title,
             'text': text}
            model.addNotification(ResourceWellStartDecorator(message=messageData, entityID=self.__START_ENTITY_ID, model=model))
            setStartNotificationShown()
        return

    def __getSingleVehicleText(self):
        rewardID = first(self.__resourceWell.config.rewards.keys())
        vehicle = self.__resourceWell.getRewardVehicle(rewardID)
        vehicleName = text_styles.crystal(vehicle.shortUserName if vehicle is not None else '')
        return backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.oneVehicleStart.text(), vehicle=vehicleName)

    def __getTwoVehiclesText(self):
        rewardIDs = self.__resourceWell.config.rewards.keys()
        if not len(rewardIDs) == 2:
            _logger.error('At parallel launch must be two vehicles, got %s', rewardIDs)
            return
        else:
            vehicles = [ self.__resourceWell.getRewardVehicle(rewardID) for rewardID in rewardIDs ]
            vehicleNames = [ text_styles.crystal(vehicle.shortUserName if vehicle is not None else '') for vehicle in vehicles ]
            return backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.twoVehiclesStart.text(), firstVehicle=vehicleNames[0], secondVehicle=vehicleNames[1])

    def __pushFinished(self):
        SystemMessages.pushMessage(text=backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.end.text()), type=SM_TYPE.ResourceWellEnd, messageData={'title': backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.end.title())})
        setFinishNotificationShown()
