# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_ammunition_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as ms
from skeletons.gui.shared import IItemsCache
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_ammunition_tooltip_view_model import WtAmmunitionTooltipViewModel
_COOLDOWN_TEMPLATE = '{}: {} {}'

class WtAmmunitionTooltipView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.tooltips.AmmunitionTooltipView(), model=WtAmmunitionTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtAmmunitionTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtAmmunitionTooltipView, self)._onLoading(*args, **kwargs)
        intCD = kwargs.get('intCD')
        if not intCD:
            return
        item = self.__itemsCache.items.getItemByCD(int(intCD))
        emptyStr = backport.text(R.strings.artefacts.empty())

        def hasString(stringToCheck):
            return stringToCheck and stringToCheck != emptyStr

        with self.viewModel.transaction() as trx:
            trx.setIconName(item.descriptor.iconName)
            trx.setTitle(item.userName)
            trx.setDescription(item.fullDescription)
            if item.itemTypeID == GUI_ITEM_TYPE.SHELL:
                trx.setSubtitle(item.shortDescriptionSpecial)
                trx.setText(item.longDescriptionSpecial)
            else:
                name = item.descriptor.name
                attribs = R.strings.artefacts.dyn(name)
                onUseStr = self.__getOnUseStr(item, attribs)
                alwaysStr = self.__getAlwaysStr(item, attribs)
                featuresStr = backport.text(attribs.features())
                trx.setAdditionalInfoText(featuresStr)
                if hasString(onUseStr):
                    trx.setSubtitle(backport.text(R.strings.tooltips.equipment.onUse()))
                    if item.descriptor.cooldownSeconds > 0:
                        cooldownStr = _COOLDOWN_TEMPLATE.format(backport.text(R.strings.menu.moduleInfo.params.reloadCooldownSeconds()), item.descriptor.cooldownSeconds, ms(backport.msgid(R.strings.menu.tank_params.no_brackets.s())))
                        trx.setText(text_styles.concatStylesToMultiLine(onUseStr, cooldownStr))
                    else:
                        trx.setText(onUseStr)
                elif hasString(alwaysStr):
                    trx.setSubtitle(backport.text(R.strings.tooltips.equipment.always()))
                    trx.setText(alwaysStr)

    def __getOnUseStr(self, item, attribs):
        if item.descriptor.name in ('wt_stun_area', 'wt_stun_area_mod_a'):
            debuffDuration = item.descriptor.debuffDuration
            damageRadius = item.descriptor.damageRadius
            return backport.text(attribs.onUse(), time=int(debuffDuration), radius=int(damageRadius))
        return backport.text(attribs.onUse())

    def __getAlwaysStr(self, item, attribs):
        if item.descriptor.name == 'wt_union_strength':
            effectDuration = item.descriptor.effectDuration
            receiveDamageFactor = item.descriptor.receiveDamageFactor
            return backport.text(attribs.always(), damageIncrease=int(receiveDamageFactor * 100), percent=backport.text(R.strings.common.common.percent()), time=int(effectDuration))
        return backport.text(attribs.always())
