# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AbstractRallyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class AbstractRallyWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def canGoBack(self):
        self._printOverrideError('canGoBack')

    def onBrowseRallies(self):
        self._printOverrideError('onBrowseRallies')

    def onCreateRally(self):
        self._printOverrideError('onCreateRally')

    def onJoinRally(self, rallyId, slotIndex, peripheryId):
        self._printOverrideError('onJoinRally')

    def as_loadViewS(self, flashAlias, pyAlias):
        return self.flashObject.as_loadView(flashAlias, pyAlias) if self._isDAAPIInited() else None

    def as_enableWndCloseBtnS(self, value):
        return self.flashObject.as_enableWndCloseBtn(value) if self._isDAAPIInited() else None
