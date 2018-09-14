# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortClanBattleListMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class FortClanBattleListMeta(BaseRallyListView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyListView
    """

    def as_setClanBattleDataS(self, data):
        """
        :param data: Represented by ClanBattleListVO (AS)
        """
        return self.flashObject.as_setClanBattleData(data) if self._isDAAPIInited() else None

    def as_upateClanBattlesCountS(self, value):
        return self.flashObject.as_upateClanBattlesCount(value) if self._isDAAPIInited() else None
