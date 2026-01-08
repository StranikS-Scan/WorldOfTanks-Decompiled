# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well_personality.py
from __future__ import absolute_import
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.shared.system_factory import registerAwardControllerHandlers
from gui.shared.system_factory import registerBannerEntryPointValidator
from resource_well.gui.Scaleform import registerResourceWellScaleform
from resource_well.gui.game_control import registerResourceWellController
from resource_well.gui.game_control.award_controller_handlers import ResourceWellRewardHandler
from resource_well.gui.impl.lobby.feature.event_banner import ResourceWellEventBanner, isResourceWellEventBannerAvailable
from resource_well.messenger import registerResourceWellMessengerFormatter
from resource_well.notification import registerResourceWellNotifications
from resource_well.web.resource_well_w2c import registerResourceWellOpenTabWebApi

def preInit():
    registerResourceWellController()
    registerResourceWellScaleform()
    registerAwardControllerHandlers((ResourceWellRewardHandler,))
    registerResourceWellNotifications()
    registerResourceWellMessengerFormatter()
    registerResourceWellOpenTabWebApi()
    EventBannersContainer().registerEventBanner(ResourceWellEventBanner)
    registerBannerEntryPointValidator(ResourceWellEventBanner.NAME, isResourceWellEventBannerAvailable)


def init():
    pass


def start():
    pass


def fini():
    pass
