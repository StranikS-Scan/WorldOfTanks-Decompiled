# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/SearchContactViewMeta.py
from messenger.gui.Scaleform.view.lobby.BaseContactView import BaseContactView

class SearchContactViewMeta(BaseContactView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseContactView
    null
    """

    def search(self, data):
        """
        :param data:
        :return :
        """
        self._printOverrideError('search')

    def as_getSearchDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getSearchDP() if self._isDAAPIInited() else None

    def as_setSearchResultTextS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_setSearchResultText(message) if self._isDAAPIInited() else None

    def as_setSearchDisabledS(self, coolDown):
        """
        :param coolDown:
        :return :
        """
        return self.flashObject.as_setSearchDisabled(coolDown) if self._isDAAPIInited() else None
