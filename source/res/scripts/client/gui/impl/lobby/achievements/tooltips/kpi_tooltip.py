# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/tooltips/kpi_tooltip.py
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.achievements.achievements_constants import KPITypes
from gui.impl.lobby.achievements.profile_utils import getFormattedValue
from gui.impl.gen.view_models.views.lobby.achievements.tooltips.kpi_tooltip_view_model import KpiTooltipViewModel
from skeletons.gui.shared import IItemsCache
KPI_STATTS = {KPITypes.ASSISTANCE.value: lambda randomStats: [getFormattedValue(randomStats.getDamageAssistedEfficiency()), getFormattedValue(randomStats.getMaxAssisted()), randomStats.getMaxAssistedVehicle()],
 KPITypes.DESTROYED.value: lambda randomStats: [getFormattedValue(randomStats.getFragsCount()), getFormattedValue(randomStats.getMaxFrags()), randomStats.getMaxFragsVehicle()],
 KPITypes.BLOCKED.value: lambda randomStats: [getFormattedValue(randomStats.getAvgDamageBlocked()), getFormattedValue(randomStats.getMaxDamageBlockedByArmor()), randomStats.getMaxDamageBlockedByArmorVehicle()],
 KPITypes.EXPERIENCE.value: lambda randomStats: [getFormattedValue(randomStats.getAvgXP()), getFormattedValue(randomStats.getMaxXp()), randomStats.getMaxXpVehicle()],
 KPITypes.DAMAGE.value: lambda randomStats: [getFormattedValue(randomStats.getAvgDamage()), getFormattedValue(randomStats.getMaxDamage()), randomStats.getMaxDamageVehicle()]}

class KPITooltip(ViewImpl):
    __slots__ = ('__kpiType', '__userId')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, kpiType, userId):
        settings = ViewSettings(R.views.lobby.achievements.tooltips.KPITooltip(), model=KpiTooltipViewModel())
        self.__kpiType = kpiType
        self.__userId = userId
        super(KPITooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(KPITooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(KPITooltip, self)._onLoading(*args, **kwargs)
        stats = self.__getStats(self.__kpiType)
        with self.viewModel.transaction() as model:
            model.setKpiType(self.__kpiType)
            model.setAvgValue(stats[0])
            model.setMaxValue(stats[1])
            model.setTankName(self.__getVehicleName(stats[2]))

    def _finalize(self):
        self.__kpiType = None
        super(KPITooltip, self)._finalize()
        return

    def __getStats(self, kpiType):
        randomStats = self.__itemsCache.items.getAccountDossier(self.__userId).getRandomStats()
        kpiStats = KPI_STATTS.get(kpiType)
        return kpiStats(randomStats) if kpiStats else ['0', '0', '']

    def __getVehicleName(self, intCD):
        vehicle = self.__itemsCache.items.getItemByCD(intCD)
        return vehicle.shortUserName if vehicle is not None else ''
