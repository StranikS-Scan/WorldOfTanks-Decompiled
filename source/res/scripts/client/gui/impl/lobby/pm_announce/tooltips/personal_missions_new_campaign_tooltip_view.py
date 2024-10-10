# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pm_announce/tooltips/personal_missions_new_campaign_tooltip_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_new_campaign_tooltip_view_model import PersonalMissionsNewCampaignTooltipViewModel
from gui.impl.pub import ViewImpl

class PersonalMissionsNewCampaignTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PersonalMissionsNewCampaignTooltipViewModel()
        super(PersonalMissionsNewCampaignTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsNewCampaignTooltipView, self).getViewModel()
