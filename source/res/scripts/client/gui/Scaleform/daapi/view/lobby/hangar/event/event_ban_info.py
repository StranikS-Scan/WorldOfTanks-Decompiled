# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_ban_info.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from gui.server_events.game_event import ifGameEventDisabled
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
from gui.Scaleform.daapi.view.meta.EventBanInfoMeta import EventBanInfoMeta
from skeletons.gui.afk_controller import IAFKController

class BanInfo(EventBanInfoMeta):
    afkController = dependency.descriptor(IAFKController)

    def __init__(self):
        super(BanInfo, self).__init__()
        self.__isBanned = False

    def _populate(self):
        super(BanInfo, self)._populate()
        self.afkController.onBanUpdated += self.__onBanUpdated
        self.__update()

    def _dispose(self):
        self.afkController.onBanUpdated -= self.__onBanUpdated
        super(BanInfo, self)._dispose()

    def __onBanUpdated(self, *_):
        self.__update()

    @ifGameEventDisabled()
    def __update(self):
        specialAlias = TOOLTIPS_CONSTANTS.EVENT_BAN_INFO
        specialArgs = [self.afkController.banExpiryTime]
        if self.__isBanned != self.afkController.isBanned:
            self.__isBanned = self.afkController.isBanned
            self.as_setVisibleS(self.__isBanned)
        if self.__isBanned:
            banMessage = backport.text(R.strings.event.hangar.ban.description(), value=formatTimeAndDate(self.afkController.banExpiryTime))
            self.as_setEventBanInfoS({'description': banMessage,
             'tooltip': '',
             'specialArgs': specialArgs,
             'specialAlias': specialAlias,
             'isSpecial': True})
