# Embedded file name: scripts/client/gui/miniclient/lobby/header/account_popover.py
from gui.Scaleform.locale.MINICLIENT import MINICLIENT
from gui.shared.utils.functions import makeTooltip
from helpers import aop
from helpers.i18n import makeString as _ms

class ClanBtnsUnavailableAspect(aop.Aspect):

    def atReturn(self, cd):
        original_return_value = cd.returned
        warnTooltip = makeTooltip(None, None, None, _ms(MINICLIENT.ACCOUNTPOPOVER_WARNING))
        original_return_value['btnTooltip'] = warnTooltip
        original_return_value['requestInviteBtnTooltip'] = warnTooltip
        original_return_value['searchClanTooltip'] = warnTooltip
        original_return_value['isOpenInviteBtnEnabled'] = False
        original_return_value['isSearchClanBtnEnabled'] = False
        original_return_value['btnEnabled'] = False
        return original_return_value


class MyClanInvitesBtnUnavailableAspect(aop.Aspect):

    def atReturn(self, cd):
        original_return_value = cd.returned
        original_return_value['inviteBtnTooltip'] = makeTooltip(None, None, None, _ms(MINICLIENT.ACCOUNTPOPOVER_WARNING))
        original_return_value['inviteBtnEnabled'] = False
        return original_return_value


class ClanBtnsUnavailable(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.header.AccountPopover', 'AccountPopover', '_getClanBtnsParams', aspects=(ClanBtnsUnavailableAspect,))


class MyClanInvitesBtnUnavailable(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.header.AccountPopover', 'AccountPopover', '_getMyInvitesBtnParams', aspects=(MyClanInvitesBtnUnavailableAspect,))
