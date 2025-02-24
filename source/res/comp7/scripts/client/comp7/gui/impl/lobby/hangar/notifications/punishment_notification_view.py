# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/hangar/notifications/punishment_notification_view.py
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.lobby.hangar.notifications.punishment_notification_view import PunishmentView, AfkLeaverNotification
from gui.shared.utils.functions import getArenaShortName
from helpers import i18n

class Comp7BanView(PunishmentView):

    def __init__(self, arenaTypeID, time, duration, penalty, isQualification, layoutID=None):
        arenaName = getArenaShortName(arenaTypeID)
        if isQualification:
            message = R.strings.dialogs.punishmentWindow.message.ban.comp7.qualification
        else:
            message = R.strings.dialogs.punishmentWindow.message.ban.comp7
        super(Comp7BanView, self).__init__(layoutID=layoutID, iconResID=R.images.gui.maps.icons.lobby.dialog_ban(), text=backport.text(message(), arenaName=i18n.makeString(arenaName), time=time, penalty=penalty), title=backport.text(R.strings.dialogs.punishmentWindow.header.ban(), time=duration), reason=R.strings.dialogs.punishmentWindow.reason.mixed())


class Comp7BanNotificationWindow(AfkLeaverNotification):
    __slots__ = ('arenaTypeID', 'time', 'duration', 'penalty', 'isQualification')

    def __init__(self, arenaTypeID, time, duration, penalty, isQualification, parent=None):
        super(Comp7BanNotificationWindow, self).__init__(content=Comp7BanView(arenaTypeID, time, duration, penalty, isQualification), parent=parent)
        self.arenaTypeID = arenaTypeID
        self.time = time
        self.duration = duration
        self.penalty = penalty
        self.isQualification = isQualification

    def __eq__(self, other):
        return False if not isinstance(other, Comp7BanNotificationWindow) else self.arenaTypeID == other.arenaTypeID and self.time == other.time and self.duration == other.duration and self.penalty == other.penalty and self.isQualification == other.isQualification
