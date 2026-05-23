# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle_personality.py
from __future__ import absolute_import
from gui.shared.system_factory import registerScaleformLobbyPackages
from open_bundle.gui.impl.lobby import registerEventBanners
from open_bundle.skeletons import registerOpenBundleController
from open_bundle.notification import registerOpenBundleNotifications
from open_bundle.web.w2c_api import registerOpenBundleWebApi

def preInit():
    registerOpenBundleController()
    registerOpenBundleNotifications()
    registerOpenBundleWebApi()
    registerEventBanners()


def init():
    registerScaleformLobbyPackages(('open_bundle.gui.impl.lobby',))


def start():
    pass


def fini():
    pass
