# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/disable_player_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.disable_player_tooltip_model import DisablePlayerTooltipModel, DisabledReason
from gui.impl.pub import ViewImpl
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class DisablePlayerTooltip(ViewImpl):
    __mtBirthday = dependency.descriptor(ITanksBirthdayController)
    __slots__ = ('__playerId', '__cooldown')

    def __init__(self, playerId=None):
        settings = ViewSettings(R.views.mt_birthday.lobby.tooltips.DisablePlayerTooltip(), model=DisablePlayerTooltipModel())
        self.__cooldown = self.__mtBirthday.getCooldownGiftTime()
        self.__playerId = playerId
        super(DisablePlayerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DisablePlayerTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setTime(self.__cooldown)
            vm.setDisabledReason(self.__getBlockedReason())

    def __getBlockedReason(self):
        if self.__playerId is None:
            return DisabledReason.NOTAVAILABLE
        elif self.__playerId == 0:
            return DisabledReason.BOT
        elif self.__mtBirthday.isAlreadyReceivedGift(self.__playerId):
            return DisabledReason.NOTAVAILABLE
        elif self.__mtBirthday.isBannedPlayer(self.__playerId):
            return DisabledReason.BANNED
        else:
            return DisabledReason.BLACKLIST if self.__mtBirthday.isPlayerInBlackList(self.__playerId) else DisabledReason.NOTAVAILABLE
