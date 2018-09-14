# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BrowserMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BrowserMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def browserAction(self, action):
        """
        :param action:
        :return :
        """
        self._printOverrideError('browserAction')

    def browserMove(self, x, y, z):
        """
        :param x:
        :param y:
        :param z:
        :return :
        """
        self._printOverrideError('browserMove')

    def browserDown(self, x, y, z):
        """
        :param x:
        :param y:
        :param z:
        :return :
        """
        self._printOverrideError('browserDown')

    def browserUp(self, x, y, z):
        """
        :param x:
        :param y:
        :param z:
        :return :
        """
        self._printOverrideError('browserUp')

    def browserFocusOut(self):
        """
        :return :
        """
        self._printOverrideError('browserFocusOut')

    def onBrowserShow(self, needRefresh):
        """
        :param needRefresh:
        :return :
        """
        self._printOverrideError('onBrowserShow')

    def onBrowserHide(self):
        """
        :return :
        """
        self._printOverrideError('onBrowserHide')

    def as_loadingStartS(self):
        """
        :return :
        """
        return self.flashObject.as_loadingStart() if self._isDAAPIInited() else None

    def as_loadingStopS(self):
        """
        :return :
        """
        return self.flashObject.as_loadingStop() if self._isDAAPIInited() else None

    def as_configureS(self, isDefaultBrowser, title, showActionBtn, showCloseBtn):
        """
        :param isDefaultBrowser:
        :param title:
        :param showActionBtn:
        :param showCloseBtn:
        :return :
        """
        return self.flashObject.as_configure(isDefaultBrowser, title, showActionBtn, showCloseBtn) if self._isDAAPIInited() else None

    def as_setBrowserSizeS(self, width, height):
        """
        :param width:
        :param height:
        :return :
        """
        return self.flashObject.as_setBrowserSize(width, height) if self._isDAAPIInited() else None

    def as_showServiceViewS(self, header, description):
        """
        :param header:
        :param description:
        :return :
        """
        return self.flashObject.as_showServiceView(header, description) if self._isDAAPIInited() else None

    def as_hideServiceViewS(self):
        """
        :return :
        """
        return self.flashObject.as_hideServiceView() if self._isDAAPIInited() else None
