# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/common/badge_tooltip.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf.view.view import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.utils import getPlayerName
from helpers import dependency, int2roman
from skeletons.gui.shared import IItemsCache
from story_mode.gui.impl.gen.view_models.views.common.badge_tooltip_view_model import BadgeTooltipViewModel

class BadgeTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, badgeId):
        settings = ViewSettings(R.views.story_mode.common.BadgeTooltip(), model=BadgeTooltipViewModel())
        super(BadgeTooltip, self).__init__(settings)
        self._badgeId = badgeId

    @property
    def viewModel(self):
        return super(BadgeTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BadgeTooltip, self)._onLoading(*args, **kwargs)
        badge = self.__itemsCache.items.getBadges()[self._badgeId]
        badgeIcon = R.images.gui.maps.icons.library.badges.c_220x220.dyn('badge_{}'.format(self._badgeId))()
        self.viewModel.setImage(badgeIcon)
        self.viewModel.setName(backport.text(R.strings.sm_common.badgeTooltip.title(), badge_name=badge.getUserName()))
        self.viewModel.setDescription(backport.text(R.strings.badge.dyn('badge_{}_descr'.format(self._badgeId))()))
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            badgeIcon = R.images.gui.maps.icons.library.badges.c_24x24.dyn('badge_{}'.format(self._badgeId))()
            self.viewModel.setSmallBadgeIcon(badgeIcon)
            self.viewModel.setVehicleIcon(vehicle.iconContour)
            self.viewModel.setVehicleLevel(int2roman(vehicle.level))
            self.viewModel.setPlayerName(getPlayerName())
