# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hangar_rules.py
import CGF
from cgf_components.tooltip_component import TooltipManager
from cgf_components.trigger_vse_component import TriggerVSEComponentsManager
from cgf_components.token_component import TokenManager
from cgf_script.managers_registrator import registerManager, Rule, registerRule
from hover_component import HoverManager
from highlight_component import HighlightManager
from on_click_components import ClickManager, ClientSelectableComponentsManager
from armory_yard_components import AssemblyStageIndexManager
from hangar_camera_manager import HangarCameraManager
from c11n_logic_manager import C11nLogicManager
from view_camera_sync import ViewCameraSyncManager, ViewCameraLinksManager
from marker_component import LobbyGFMarkersManager

@registerRule
class SelectionRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(HoverManager)
    def reg1(self):
        return None

    @registerManager(HighlightManager)
    def reg2(self):
        return None

    @registerManager(ClickManager)
    def reg3(self):
        return None

    @registerManager(TooltipManager)
    def reg4(self):
        return None

    @registerManager(ClientSelectableComponentsManager)
    def reg5(self):
        return None


@registerRule
class ArmoryYardRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(AssemblyStageIndexManager)
    def reg1(self):
        return None


@registerRule
class CameraRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(HangarCameraManager)
    def reg1(self):
        return None


@registerRule
class C11nLogicRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(C11nLogicManager)
    def reg1(self):
        return None


@registerRule
class HangarTokenRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(TokenManager)
    def reg1(self):
        return None

    @registerManager(TriggerVSEComponentsManager)
    def reg2(self):
        return None


@registerRule
class ViewCameraSyncRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(ViewCameraSyncManager)
    def reg1(self):
        return None

    @registerManager(ViewCameraLinksManager)
    def reg2(self):
        return None


@registerRule
class LobbyGFMarkerRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(LobbyGFMarkersManager)
    def reg1(self):
        return None
