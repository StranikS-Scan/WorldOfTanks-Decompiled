# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well_personality.py
from gui.shared.system_factory import registerAwardControllerHandlers
from resource_well.gui.Scaleform import registerResourceWellScaleform
from resource_well.gui.game_control import registerResourceWellController
from resource_well.gui.game_control.award_controller_handlers import ResourceWellRewardHandler
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


def init():
    pass


def start():
    pass


def fini():
    pass
