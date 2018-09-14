# Embedded file name: scripts/client/gui/miniclient/__init__.py
import ResMgr
import shop as _shop
import continue_download as _continue_download
import contacts as _contacts
import dynamic_squads as _dynamic_squads
import promo_controller as _promo_controller
from lobby import configure_pointcuts as _configure_lobby_pointcuts
from tech_tree import configure_pointcuts as _configure_tech_tree_pointcuts
from invitations import configure_pointcuts as _configure_invitation_pointcuts
from fortified_regions import configure_pointcuts as _configure_fort_pointcuts
from personal_quests import configure_pointcuts as _configure_personal_quests_pointcuts

class CONTENT_TYPE:
    DEFAULT = 0
    SD_TEXTURES = 1
    HD_TEXTURES = 2
    INCOMPLETE = 3
    TUTORIAL = 4
    SANDBOX = 5


def configure_state():
    content_type = ResMgr.activeContentType()
    if content_type == CONTENT_TYPE.SANDBOX:
        config = _get_config(content_type)
        _shop.OnShopItemWrapPointcut(config)
        _continue_download.OnHyperlinkClickPointcut()
        _continue_download.OnSquadHyperlinkClickPointcut()
        _continue_download.PrepareLibrariesListPointcut()
        _continue_download.OnBrowserHyperlinkClickPointcut()
        _continue_download.OnFailLoadingFramePointcut()
        _contacts.CreateSquadPointcut()
        _configure_lobby_pointcuts(config)
        _configure_fort_pointcuts()
        _configure_tech_tree_pointcuts(config)
        _configure_invitation_pointcuts()
        _configure_personal_quests_pointcuts()
        _dynamic_squads.ParametrizeInitPointcut()
        _dynamic_squads.DisableGameSettingPointcut()
        _dynamic_squads.InviteReceivedMessagePointcut()
        _promo_controller.ShowPromoBrowserPointcut()


def _get_config(content_type):

    def vehicle_filter(vehicle_item):
        extraCondition = not vehicle_item.isOnlyForEventBattles
        if content_type == CONTENT_TYPE.SANDBOX:
            max_vehicle_level = 2
            extraCondition = extraCondition and not vehicle_item.isExcludedFromSandbox
        elif content_type == CONTENT_TYPE.TUTORIAL:
            max_vehicle_level = 1
        else:
            max_vehicle_level = 10
            extraCondition = True
        return vehicle_item.level <= max_vehicle_level and extraCondition

    return {'vehicle_is_available': vehicle_filter}


__all__ = ('configure_state',)
