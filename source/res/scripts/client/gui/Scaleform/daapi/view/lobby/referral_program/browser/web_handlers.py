# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/referral_program/browser/web_handlers.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showReferralProgramWindow
from web.web_client_api import webApiCollection
from web.web_client_api.referral_program import ReferralProgramWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import SoundWebApi
from web.web_client_api.ui import OpenWindowWebApi, OpenTabWebApi, UtilWebApi, ContextMenuWebApi, CloseWindowWebApi

class _OpenTabWebApi(OpenTabWebApi):

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getReturnCallback(cmd.back_url)

    def __getReturnCallback(self, backUrl):
        return (lambda : showReferralProgramWindow(backUrl)) if backUrl is not None else None


def createReferralWebHandlers():
    return webApiCollection(SoundWebApi, RequestWebApi, ReferralProgramWebApi, ContextMenuWebApi, OpenWindowWebApi, UtilWebApi, RewardsWebApi, SocialWebApi, ShopWebApi, CloseWindowWebApi, _OpenTabWebApi)
