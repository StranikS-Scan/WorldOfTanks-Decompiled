# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/referral_program/__init__.py
from helpers import dependency
from skeletons.gui.game_control import IReferralProgramController
from web.client_web_api.api import C2WHandler, c2w
from web.common import formatReferralProgramInfo

class ReferralProgramEventHandler(C2WHandler):
    __referralProgram = dependency.descriptor(IReferralProgramController)

    def init(self):
        super(ReferralProgramEventHandler, self).init()
        self.__referralProgram.onPointsChanged += self.__sendInfo

    def fini(self):
        self.__referralProgram.onPointsChanged -= self.__sendInfo
        super(ReferralProgramEventHandler, self).fini()

    @c2w(name='referral_program_info_changed')
    def __sendInfo(self, *args, **kwargs):
        return formatReferralProgramInfo()
