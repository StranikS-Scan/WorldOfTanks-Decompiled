# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/tooltips/daily_widget_tooltip.py
import time
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from gui.impl.lobby.halloween.event_helpers import getCurrentVehicle
from gui.impl.gen.view_models.views.lobby.halloween.tooltips.daily_tooltip_model import DailyTooltipModel

class DailyWidgetTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, vehCD=None):
        settings = ViewSettings(R.views.lobby.halloween.tooltips.DailyTooltip())
        settings.model = DailyTooltipModel()
        self.__vehCD = vehCD
        super(DailyWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DailyWidgetTooltip, self).getViewModel()

    def _onLoading(self):
        super(DailyWidgetTooltip, self)._onLoading()
        if self.__vehCD is None:
            vehicle = getCurrentVehicle(self._itemsCache)
        else:
            vehicle = self._itemsCache.items.getVehicleCopyByCD(self.__vehCD)
        self.viewModel.setName(vehicle.userName)
        self.viewModel.setType(vehicle.type)
        self.viewModel.setImage(replaceHyphenToUnderscore(vehicle.name.replace(':', '-')))
        tm = time.gmtime(self._eventsCache.getEventFinishTime() + time_utils.ONE_MINUTE)
        self.viewModel.setFooter(backport.text(R.strings.event.hangarView.dailyTooltip.body2(), year=tm.tm_year, month=tm.tm_mon, day=tm.tm_mday, hour=str(tm.tm_hour).zfill(2), minute=str(tm.tm_min).zfill(2)))
        return
