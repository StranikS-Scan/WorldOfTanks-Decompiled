# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/clan_short_info_content_model.py
from frameworks.wulf import ViewModel

class ClanShortInfoContentModel(ViewModel):
    __slots__ = ()

    def getEmblem(self):
        return self._getString(0)

    def setEmblem(self, value):
        self._setString(0, value)

    def getFullName(self):
        return self._getString(1)

    def setFullName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ClanShortInfoContentModel, self)._initialize()
        self._addStringProperty('emblem', '')
        self._addStringProperty('fullName', '')
