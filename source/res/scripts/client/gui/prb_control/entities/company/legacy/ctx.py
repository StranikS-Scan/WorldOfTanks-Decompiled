# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/company/legacy/ctx.py
from constants import PREBATTLE_COMPANY_DIVISION, PREBATTLE_TYPE
from gui.prb_control.entities.base.legacy.ctx import TeamSettingsCtx, JoinLegacyCtx, LegacyRequestCtx
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_SETTING_NAME, REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('__division', 'division'))
class CompanySettingsCtx(TeamSettingsCtx):
    """
    Context to change company's division
    """
    __slots__ = ('__division',)

    def __init__(self, waitingID='', isOpened=True, comment='', division=PREBATTLE_COMPANY_DIVISION.CHAMPION, isRequestToCreate=True, flags=FUNCTIONAL_FLAG.UNDEFINED):
        super(CompanySettingsCtx, self).__init__(PREBATTLE_TYPE.COMPANY, waitingID, isOpened, comment, isRequestToCreate, flags)
        self.__division = division

    def getDivision(self):
        """
        Gets the division number
        """
        return self.__division

    def setDivision(self, division):
        """
        Sets the division number
        """
        self.__division = division

    def isDivisionChanged(self, settings):
        """
        Was the division changed
        Args:
            settings: prebattle settings
        """
        return self.__division != settings[PREBATTLE_SETTING_NAME.DIVISION]


class JoinCompanyCtx(JoinLegacyCtx):
    """
    Join company request context
    """
    __slots__ = ()

    def __init__(self, prbID, waitingID='', flags=FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinCompanyCtx, self).__init__(prbID, PREBATTLE_TYPE.COMPANY, waitingID=waitingID, flags=flags)


@ReprInjector.withParent('isNotInBattle', 'division', 'creatorMask')
class RequestCompaniesCtx(LegacyRequestCtx):
    """
    Companies list request context
    """
    __slots__ = ('isNotInBattle', 'division', 'creatorMask')

    def __init__(self, isNotInBattle=False, division=0, creatorMask='', waitingID=''):
        super(RequestCompaniesCtx, self).__init__(entityType=PREBATTLE_TYPE.COMPANY, waitingID=waitingID)
        self.isNotInBattle = isNotInBattle
        self.creatorMask = creatorMask
        if division in PREBATTLE_COMPANY_DIVISION.RANGE:
            self.division = division
        else:
            self.division = 0

    def getRequestType(self):
        return REQUEST_TYPE.PREBATTLES_LIST

    def byDivision(self):
        """
        Gets filter by division.
        """
        return self.division in PREBATTLE_COMPANY_DIVISION.RANGE

    def byName(self):
        """
        Gets filter by name.
        """
        return self.creatorMask is not None and len(self.creatorMask) > 0
