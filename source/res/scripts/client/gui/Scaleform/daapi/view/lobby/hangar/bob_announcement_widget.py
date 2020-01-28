# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/bob_announcement_widget.py
from gui.Scaleform.daapi.view.meta.BobAnnouncementWidgetMeta import BobAnnouncementWidgetMeta
from gui.game_control.bob_announcement_helpers import getAnnouncementWidgetData
from gui.impl.backport import text
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IBobController, IBobAnnouncementController

class BobAnnouncementWidget(BobAnnouncementWidgetMeta):
    __bobController = dependency.descriptor(IBobController)
    __bobAnnouncement = dependency.descriptor(IBobAnnouncementController)

    def onClick(self):
        self.__bobAnnouncement.clickAnnouncement()

    def _populate(self):
        if self.__bobController.isRuEuRealm():
            self.as_setEventTitleS(text(R.strings.bob.announcement.title()))
        else:
            self.as_setEventTitleS(text(R.strings.bob.announcement.title.na_asia()))
        self.as_setCurrentRealmS(self.__bobController.getCurrentRealm())
        self.__onAnnouncementUpdated(self.__bobAnnouncement.currentAnnouncement)
        self.__bobAnnouncement.onAnnouncementUpdated += self.__onAnnouncementUpdated
        super(BobAnnouncementWidget, self)._populate()

    def _dispose(self):
        self.__bobAnnouncement.onAnnouncementUpdated -= self.__onAnnouncementUpdated
        super(BobAnnouncementWidget, self)._dispose()

    def __onAnnouncementUpdated(self, announcementType):
        if announcementType is None:
            self.as_setEnabledS(False)
        else:
            self.as_setEnabledS(True)
            announcementData = getAnnouncementWidgetData(announcementType)
            self.as_showAnnouncementS(announcementData.header, announcementData.body, announcementData.hasLockerIcon, announcementData.hasTimerIcon)
        return
