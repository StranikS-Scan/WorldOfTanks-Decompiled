# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/detachment_controller.py
import logging
from Event import EventManager, Event
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from async import async, AsyncEvent, await
from constants import IS_CREW_SANDBOX
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.dialogs.dialogs import showIntroVideoDialogView
from gui.shared.event_dispatcher import showPresentationView, showBrowserOverlayView
from helpers import dependency
from items.components.detachment_constants import DetachmentSlotType
from notification import NotificationMVC
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.game_control import IDetachmentController, IBootcampController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class DetachmentInfo(object):
    __slots__ = ('__instructorSlots', '__vehicleSlots', '__progress')

    def __init__(self, instructorSlots, vehicleSlots, progress):
        self.__instructorSlots = instructorSlots
        self.__vehicleSlots = vehicleSlots
        self.__progress = progress

    def getShownSlots(self, slotType):
        return self.__instructorSlots if slotType == DetachmentSlotType.INSTRUCTORS else self.__vehicleSlots

    @property
    def shownProgress(self):
        return self.__progress

    @shownProgress.setter
    def shownProgress(self, progress):
        self.__progress = progress

    def __repr__(self):
        return 'instructorSlots={}, vehicleSlots={}, progress={}'.format(self.__instructorSlots, self.__vehicleSlots, self.__progress)


class DetachmentController(IDetachmentController):
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __bootcampController = dependency.descriptor(IBootcampController)
    __appLoader = dependency.descriptor(IAppLoader)
    __settingsCore = dependency.instance(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)
    _VERSION_UPDATER_COMPLETION_MARK = 'token:crew_conversion:success'

    def __init__(self):
        self.__isConnected = False
        self.__eventsManager = EventManager()
        self.onShowIntroVideoSwitched = Event(self.__eventsManager)
        self.onSlotsAnimationRenew = Event(self.__eventsManager)
        self._showIntroVideo = True
        self.__detachmentInfo = {}

    @property
    def isAccConverted(self):
        return self.__itemsCache.items.tokens.getTokenCount(self._VERSION_UPDATER_COMPLETION_MARK)

    @property
    def storageData(self):
        return self.__settingsCore.serverSettings.getUIStorage()

    @property
    def isIntroVideoShow(self):
        return bool(self.storageData.get(UI_STORAGE_KEYS.DETACHMENT_INTRO_VIDEO_IS_SHOWN, False))

    @property
    def isPromoScreenShow(self):
        return bool(self.storageData.get(UI_STORAGE_KEYS.PROMO_SCREEN_IS_SHOWN, False))

    @property
    def isIntroVideoOn(self):
        return self._showIntroVideo

    def tryLockPopups(self):
        if not self.isDetachmentIntroCompleted():
            NotificationMVC.g_instance.lockPopups()

    def isDetachmentIntroCompleted(self):
        return not self.isAccConverted or (not self.isIntroVideoOn or self.isIntroVideoShow) and self.isPromoScreenShow

    def onLobbyInited(self, _):
        if not self.__bootcampController.isInBootcamp():
            showVideo = self.isAccConverted and self.isIntroVideoOn and not self.isIntroVideoShow
            showPresentation = self.isAccConverted and not self.isPromoScreenShow
            self.processIntro(showVideo, showPresentation)
        if not self.__detachmentInfo:
            for invId, detItem in self.__detachmentCache.getDetachments().iteritems():
                descr = detItem.getDescriptor()
                self.__detachmentInfo[invId] = DetachmentInfo([ idx for idx in xrange(descr.getSlotsCount(DetachmentSlotType.INSTRUCTORS)) ], [ idx for idx in xrange(descr.getSlotsCount(DetachmentSlotType.VEHICLES)) ], self.__getCurrentProgress(invId))

    def onConnected(self):
        self.__isConnected = True

    def onDisconnected(self):
        self.__isConnected = False
        self.__detachmentInfo.clear()

    def fini(self):
        self.__eventsManager.clear()

    def showIntroVideo(self):
        self.__showVideo(False)

    @property
    def isConnected(self):
        return self.__isConnected

    @async
    def processIntro(self, showVideo, showPresentation):
        if showVideo:
            yield await(self.__showVideo(True))
            if not self.__isConnected:
                return
            self.__settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.DETACHMENT_INTRO_VIDEO_IS_SHOWN: True})
        if showPresentation:
            showPresentationView()

    def getShownProgress(self, detInvID):
        detInfo = self.__getDetachmentInfo(detInvID)
        prevProgress = detInfo.shownProgress
        detInfo.shownProgress = self.__getCurrentProgress(detInvID)
        return prevProgress

    def isSlotAnimationActive(self, detInvID, slotType, slotIndex, checkSlotEmpty=True):
        detItem = self.__detachmentCache.getDetachment(detInvID)
        detInfo = self.__getDetachmentInfo(detInvID)
        storage = detInfo.getShownSlots(slotType)
        needAnimationShown = slotIndex not in storage
        if checkSlotEmpty:
            isSlotEmpty = not detItem.getDescriptor().getSlotValue(slotType, slotIndex)
            return needAnimationShown and isSlotEmpty
        return needAnimationShown

    def saveAnimationAsShown(self, detInvID, slotType, slotIndex):
        detInfo = self.__getDetachmentInfo(detInvID)
        storage = detInfo.getShownSlots(slotType)
        if slotIndex not in storage:
            storage.append(slotIndex)

    def renewSlotsAnimation(self, detInvID, slotType, slots):
        detInfo = self.__getDetachmentInfo(detInvID)
        storage = detInfo.getShownSlots(slotType)
        for slotIndex in slots:
            if slotIndex in storage:
                storage.remove(slotIndex)

        self.onSlotsAnimationRenew(detInvID)

    def setPromoScreenIsShown(self):
        self.__settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.PROMO_SCREEN_IS_SHOWN: True})
        NotificationMVC.g_instance.unlockPopups()

    def __getDetachmentInfo(self, detInvID):
        if detInvID not in self.__detachmentInfo:
            info = DetachmentInfo([], [], self.__getCurrentProgress(detInvID))
            self.__detachmentInfo[detInvID] = info
            _, _, levelIconID, _, _ = info.shownProgress
            return DetachmentInfo([], [], (0.0,
             1,
             levelIconID,
             R.strings.detachment.progressionLevel.commander(),
             -1))
        return self.__detachmentInfo[detInvID]

    def __getCurrentProgress(self, detInvID):
        detItem = self.__detachmentCache.getDetachment(detInvID)
        return (detItem.currentXPProgress,
         detItem.level,
         detItem.levelIconID,
         detItem.masteryName,
         detItem.experience)

    @async
    def __showVideo(self, withClosingDialog):
        if IS_CREW_SANDBOX:
            yield await(self.__showSandboxIntroWindow())
        else:
            yield await(showIntroVideoDialogView(withClosingDialog))

    @async
    def __showSandboxIntroWindow(self):
        url = GUI_SETTINGS.detachment.get('webIntroVideo')
        event = AsyncEvent()
        showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY, onDone=event.set)
        yield await(event.wait())
