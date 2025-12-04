# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/ny_rules.py
import CGF
from new_year.cgf.ny_surprice_machine_components import NewYearMachineButtonsManager, NewYearMachineActivatorManager
from cgf_components.view_camera_sync import ViewCameraSyncManager, ViewCameraLinksManager
from new_year.cgf.lobby_customization_components import LobbyCustomizableObjectsManager
from new_year.cgf.new_year_components import NewYearClickManager, NewYearHoverManager
from new_year.cgf.ny_events_listener_component import NewYearEventsListenerManager
from cgf_script.managers_registrator import registerRule, registerManager, Rule
from new_year.cgf.raccoon_customization_components import RaccoonManager
from new_year.cgf.ny_env_switch_rule import NewYearEnvironmentLoader
from new_year.cgf.raccoon_marker_manager import RaccoonMarkerManager
from cgf_components.marker_component import LobbyGFMarkersManager
from new_year.cgf.ny_animations import NewYearAnimatorManager
from cgf_components.token_component import TokenManager
from new_year.cgf.oldman_manager import OldManManager

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

    @registerManager(NewYearEnvironmentLoader)
    def reg10(self):
        return None

    @registerManager(NewYearMachineButtonsManager)
    def reg11(self):
        return None

    @registerManager(NewYearMachineActivatorManager)
    def reg12(self):
        return None

    @registerManager(RaccoonMarkerManager)
    def reg13(self):
        return None

    @registerManager(OldManManager)
    def reg14(self):
        return None

    @registerManager(NewYearEventsListenerManager)
    def reg15(self):
        return None
