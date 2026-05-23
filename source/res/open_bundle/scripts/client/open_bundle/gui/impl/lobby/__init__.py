# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/__init__.py
from __future__ import absolute_import
from gui.shared.system_factory import registerBannerEntryPointValidator
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from open_bundle.gui.constants import OPEN_BUNDLE_ENTRY_POINT_NAME
from open_bundle.gui.impl.lobby.event_banner import isOpenBundleEntryPointAvailable, OpenBundleEventBanner

def getStateMachineRegistrators():
    from open_bundle.gui.impl.lobby.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass


def registerEventBanners():
    ebc = EventBannersContainer()
    ebc.registerEventBanner(OpenBundleEventBanner)
    registerBannerEntryPointValidator(OPEN_BUNDLE_ENTRY_POINT_NAME, isOpenBundleEntryPointAvailable)
