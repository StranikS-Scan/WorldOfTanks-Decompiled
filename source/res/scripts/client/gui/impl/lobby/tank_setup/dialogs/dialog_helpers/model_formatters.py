# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/dialog_helpers/model_formatters.py


def initItemInfo(viewModel, device, currency):
    with viewModel.transaction() as model:
        model.detailsDevice.setOverlayType(device.getHighlightType())
        model.detailsDevice.setLevel(device.level)
        model.detailsDevice.setDeviceName(device.name)
        model.detailsPriceBlock.setCurrencyName(currency)
        model.detailsPriceBlock.setCountDevice(device.inventoryCount)
        actualPrices = device.sellPrices.itemPrice.price
        model.detailsPriceBlock.setPriceDevice(actualPrices.toSignDict().get(currency, 0))
