# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/lobby/portal_banner_entry_point.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.PortalBannerEntryPointMeta import PortalBannerEntryPointMeta
from portal.gui.impl.lobby.portal_banner_entry_point import PortalBannerEntryPointView
from portal_account_settings import getEventEntrypointIsNew

class PortalBannerEntryPoint(PortalBannerEntryPointMeta):

    def _makeInjectView(self):
        self.__view = PortalBannerEntryPointView(ViewFlags.VIEW)
        return self.__view

    def _populate(self):
        super(PortalBannerEntryPoint, self)._populate()
        self.__view.onAnimationFinished += self.__onShowingAnimationFinish

    def _dispose(self):
        self.__view.onAnimationFinished -= self.__onShowingAnimationFinish
        super(PortalBannerEntryPoint, self)._dispose()

    def _hasNewMark(self):
        return getEventEntrypointIsNew()

    def __onShowingAnimationFinish(self):
        self.setIsNewS(self._hasNewMark())
