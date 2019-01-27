# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/referral_program/__init__.py
from helpers import dependency
from skeletons.gui.game_control import IReferralProgramController
from web_client_api import w2c, w2capi, W2CSchema, Field

class _CloseReferralProgramViewSchema(W2CSchema):
    pass


class _OpenContentPage(W2CSchema):
    url = Field(required=True, type=basestring)


@w2capi(name='referral_program', key='action')
class ReferralProgramWebApi(W2CSchema):
    __referralCtrl = dependency.descriptor(IReferralProgramController)

    @w2c(_CloseReferralProgramViewSchema, 'close_referral_program_view')
    def closeReferralProgramView(self, cmd):
        if self.__referralCtrl:
            self.__referralCtrl.hideWindow()
