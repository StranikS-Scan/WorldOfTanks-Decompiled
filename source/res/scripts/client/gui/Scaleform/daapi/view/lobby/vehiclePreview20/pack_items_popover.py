# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/pack_items_popover.py
from gui.Scaleform.daapi.view.meta.PackItemsPopoverMeta import PackItemsPopoverMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.utils import flashObject2Dict
_R_SHOP_PACK = R.strings.tooltips.vehiclePreview.shopPack

class PackItemsPopover(PackItemsPopoverMeta):

    def __init__(self, ctx=None):
        super(PackItemsPopover, self).__init__(ctx)
        self.__rawData = ctx.get('data')

    def _populate(self):
        super(PackItemsPopover, self)._populate()
        pack = flashObject2Dict(self.__rawData)
        title = text_styles.highTitle(pack.get('title', backport.text(_R_SHOP_PACK.title())))
        items = []
        for item in pack.get('items'):
            item = flashObject2Dict(item)
            count = item.get('count') or 0
            items.append({'value': backport.text(_R_SHOP_PACK.count()).format(count=count) if count > 1 else None,
             'icon': item.get('icon'),
             'overlayType': item.get('overlay'),
             'description': item.get('desc'),
             'hasCompensation': item.get('hasCompensation', False)})

        self.as_setItemsS(title, items)
        return

    def _dispose(self):
        self.__rawData = None
        super(PackItemsPopover, self)._dispose()
        return
