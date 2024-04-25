# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/frontmen_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.frontman_tooltip_model import FrontmanTooltipModel
from historical_battles.gui.impl.lobby.widgets.frontman_widget import FrontmanRoleIDToRole
from items import vehicles
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class FrontmanTooltip(ViewImpl):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, frontmanID, showRoleAbility=False):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.FrontmanTooltip())
        settings.model = model = FrontmanTooltipModel()
        super(FrontmanTooltip, self).__init__(settings)
        frontmanData = self.gameEventController.getGameEventData().get('frontmen', {}).get(frontmanID, {})
        model.setFrontmanID(frontmanID)
        model.setRole(FrontmanRoleIDToRole.get(frontmanData.get('roleID', 0)).value)
        model.setShowRoleAbility(showRoleAbility)
        if showRoleAbility:
            roleAbilities = frontmanData.get('roleAbilities', [])
            if roleAbilities:
                roleAbility = vehicles.g_cache.equipments()[roleAbilities.get('eqId', '')]
                roleAbilityModel = model.roleAbility
                roleAbilityModel.setTitle(roleAbility.userString)
                roleAbilityModel.setIcon(roleAbility.iconName)
                roleAbilityModel.setDescr(roleAbility.description)
