# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_header_clan_info_model.py
from frameworks.wulf import ViewModel

class PremDashboardHeaderClanInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PremDashboardHeaderClanInfoModel, self).__init__(properties=properties, commands=commands)

    def getClanAbbrev(self):
        return self._getString(0)

    def setClanAbbrev(self, value):
        self._setString(0, value)

    def getRoleInClan(self):
        return self._getString(1)

    def setRoleInClan(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(PremDashboardHeaderClanInfoModel, self)._initialize()
        self._addStringProperty('clanAbbrev', '')
        self._addStringProperty('roleInClan', '')
