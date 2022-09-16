# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/formatters/invites.py
from copy import deepcopy
from constants import PREBATTLE_TYPE
from fun_random.gui.feature.fun_random_helpers import getDisabledFunRandomTooltip
from gui.impl.gen import R
from gui.prb_control.formatters.invites import PrbInviteHtmlTextFormatter
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunPrbInviteHtmlTextFormatter(PrbInviteHtmlTextFormatter):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def canAcceptInvite(self, invite):
        canAccept = super(FunPrbInviteHtmlTextFormatter, self).canAcceptInvite(invite)
        return canAccept and self.__funRandomCtrl.hasSuitableVehicles()

    def updateTooltips(self, invite, canAccept, message):
        if 'buttonsLayout' not in message:
            return message
        if not canAccept and invite.type == PREBATTLE_TYPE.FUN_RANDOM:
            tooltip, message = '', deepcopy(message)
            if self.__funRandomCtrl.isAvailable() and not self.__funRandomCtrl.hasSuitableVehicles():
                tooltipStr = R.strings.invites.invites.tooltip.funRandom.noVehicles()
                tooltip = makeTooltip(body=getDisabledFunRandomTooltip(tooltipStr))
            buttonsLayout = message.get('buttonsLayout')
            buttonsLayout[0]['tooltip'] = tooltip
        return message
