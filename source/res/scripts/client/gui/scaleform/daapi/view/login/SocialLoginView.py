# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/SocialLoginView.py
import BigWorld
from gui.login.social_networks import SOCIAL_NETWORKS
from LoginView import LoginView
from login_modes.social_mode import SOCIAL_NETWORK_TO_DOMAIN_MAPPING

class SocialLoginView(LoginView):

    def onRegister(self, host):
        self._loginMode.doSocialLogin(SOCIAL_NETWORKS.WGNI, host, True)

    def onLoginBySocial(self, socialNetworkName, serverName):
        self._loginMode.doSocialLogin(socialNetworkName, serverName, False)

    def onTextLinkClick(self, socialNetworkName):
        if socialNetworkName in SOCIAL_NETWORK_TO_DOMAIN_MAPPING:
            BigWorld.wg_openWebBrowser(SOCIAL_NETWORK_TO_DOMAIN_MAPPING[socialNetworkName])
            return
        super(SocialLoginView, self).onTextLinkClick(socialNetworkName)
