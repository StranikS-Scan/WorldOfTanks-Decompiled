# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/tooltips/ability_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from grinch_progression.gui.impl.gen.view_models.views.lobby.tooltips.ability_tooltip_view_model import AbilityTooltipViewModel, AbilityType
from gui.impl import backport
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from items.vehicle_items import Gun
_logger = logging.getLogger(__name__)

class AbilityTooltipView(ViewImpl):
    __slots__ = ('__intCD', '__keyString')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, intCD, keyString):
        settings = ViewSettings(R.views.grinch_progression.lobby.tooltips.AbilityTooltipView())
        settings.model = AbilityTooltipViewModel()
        self.__intCD = intCD
        self.__keyString = keyString
        super(AbilityTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AbilityTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        if self.__intCD is None:
            _logger.error('__intCd cannot be None')
        ability = self.__itemsCache.items.getItemByCD(self.__intCD)
        name, type, description, radius, duration, debuffDuration = self.__getAbilityData(ability)
        with self.viewModel.transaction() as tx:
            tx.setName(name)
            tx.setDescription(description)
            tx.setAbilityType(type)
            tx.setKeyString(self.__keyString)
            tx.setRadius(radius)
            tx.setDuration(duration)
            tx.setDebuffDuration(debuffDuration)
        return

    def __getAbilityData(self, ability):
        abilityDescriptor = ability.descriptor
        if isinstance(abilityDescriptor, Gun):
            gunShell = abilityDescriptor.shots[0].shell
            name = gunShell.name
            type = AbilityType.GUN
            description = gunShell.description
            radius = 0
            duration = 0
            debuffDuration = 0
        else:
            name = ability.name
            type = AbilityType.ABILITY
            description = backport.text(R.strings.grinch_progression.abilityTooltip.description.dyn(name)())
            radius = abilityDescriptor.radius if abilityDescriptor.radius else 0
            duration = abilityDescriptor.duration if abilityDescriptor.duration else 0
            debuffDuration = abilityDescriptor.debuffDuration if abilityDescriptor.debuffDuration else 0
        return (name,
         type,
         description,
         radius,
         duration,
         debuffDuration)
