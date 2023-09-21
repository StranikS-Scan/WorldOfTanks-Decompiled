# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_ammunition_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_ammunition_tooltip_view_model import WtEventAmmunitionTooltipViewModel
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as ms
from skeletons.gui.shared import IItemsCache
_ANIMATION_PATH = 'animations/wt_event/{}.swf'
_COOLDOWN_TEMPLATE = '{}: {} {}'

class WtEventAmmunitionTooltipView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.tooltips.WtEventAmmunitionTooltipView(), model=WtEventAmmunitionTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventAmmunitionTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventAmmunitionTooltipView, self)._onLoading(*args, **kwargs)
        intCD = kwargs.get('intCD')
        if not intCD:
            return
        item = self.__itemsCache.items.getItemByCD(int(intCD))
        emptyStr = backport.text(R.strings.artefacts.empty())

        def hasString(stringToCheck):
            return stringToCheck and stringToCheck != emptyStr

        with self.viewModel.transaction() as trx:
            trx.setIcon(R.images.gui.maps.icons.artefact.dyn(item.descriptor.iconName)())
            trx.setTitle(item.userName)
            trx.setDescription(item.fullDescription)
            if item.itemTypeID == GUI_ITEM_TYPE.SHELL:
                trx.setSubtitle(item.shortDescriptionSpecial)
                trx.setText(item.longDescriptionSpecial)
            else:
                name = item.descriptor.name
                attribs = R.strings.artefacts.dyn(name)
                onUseStr = backport.text(attribs.onUse())
                alwaysStr = backport.text(attribs.always())
                featuresStr = backport.text(attribs.features())
                trx.setAnimation(_ANIMATION_PATH.format(item.descriptor.iconName))
                trx.setAdditionalInfoText(featuresStr)
                if hasString(onUseStr):
                    trx.setSubtitle(backport.text(R.strings.tooltips.equipment.onUse()))
                    if item.descriptor.cooldownSeconds > 0:
                        cooldownStr = _COOLDOWN_TEMPLATE.format(backport.text(R.strings.menu.moduleInfo.params.cooldownSeconds()), item.descriptor.cooldownSeconds, ms(backport.msgid(R.strings.menu.tank_params.no_brackets.s())))
                        trx.setText(text_styles.concatStylesToMultiLine(onUseStr, cooldownStr))
                    else:
                        trx.setText(onUseStr)
                elif hasString(alwaysStr):
                    trx.setSubtitle(backport.text(R.strings.tooltips.equipment.always()))
                    trx.setText(alwaysStr)
