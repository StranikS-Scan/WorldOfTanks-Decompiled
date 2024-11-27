# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/ny_rules.py
import CGF
from cgf_components.marker_component import LobbyGFMarkersManager
from cgf_components.token_component import TokenManager
from cgf_components.view_camera_sync import ViewCameraSyncManager, ViewCameraLinksManager
from cgf_script.managers_registrator import registerRule, registerManager, Rule
from new_year.cgf.lobby_customization_components import LobbyCustomizableObjectsManager
from new_year.cgf.new_year_components import NewYearClickManager, NewYearHoverManager
from new_year.cgf.raccoon_customization_components import RaccoonManager
from new_year.cgf.ny_animations import NewYearAnimatorManager

@registerRule
class NyHangarRule(Rule):
    category = 'New year rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(LobbyCustomizableObjectsManager)
    def reg1(self):
        return None

    @registerManager(NewYearClickManager)
    def reg2(self):
        return None

    @registerManager(ViewCameraSyncManager)
    def reg3(self):
        return None

    @registerManager(ViewCameraLinksManager)
    def reg4(self):
        return None

    @registerManager(LobbyGFMarkersManager)
    def reg5(self):
        return None

    @registerManager(NewYearHoverManager)
    def reg6(self):
        return None

    @registerManager(RaccoonManager)
    def reg7(self):
        return None

    @registerManager(NewYearAnimatorManager)
    def reg8(self):
        return None

    @registerManager(TokenManager)
    def reg9(self):
        return None
