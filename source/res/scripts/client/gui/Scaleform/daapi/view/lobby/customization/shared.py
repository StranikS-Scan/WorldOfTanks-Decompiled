# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/shared.py
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui.customization.shared import CUSTOMIZATION_TYPE

def getDialogRemoveElement(itemName, cType):
    deleteStr = text_styles.error(VEHICLE_CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_DELETE)
    description = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_DESCRIPTION, elementName='{0} {1}'.format(__formatTypeName(cType, 1), text_styles.main(itemName)), delete=deleteStr))
    return I18nConfirmDialogMeta('customization/remove_element', messageCtx={'description': description}, focusedID=DIALOG_BUTTON_ID.CLOSE)


def getDialogReplaceElement(itemName, cType):
    deleteStr = text_styles.error(VEHICLE_CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_DELETE)
    description = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.DIALOG_REPLACE_ELEMENT_DESCRIPTION, elementName='{0} {1}'.format(__formatTypeName(cType, 1), text_styles.main(itemName)), delete=deleteStr))
    return I18nConfirmDialogMeta('customization/replace_element', messageCtx={'description': description}, focusedID=DIALOG_BUTTON_ID.CLOSE)


def getDialogReplaceElements(elementGroups):
    elementsCount = sum([ len(x) for x in elementGroups ])
    if elementsCount > 1:
        deleteStr = text_styles.error(VEHICLE_CUSTOMIZATION.DIALOG_REMOVE_ELEMENTS_DELETE)
        description = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.DIALOG_REPLACE_ELEMENTS_DESCRIPTION, elementsName=__formatReplaceElements(elementGroups), delete=deleteStr))
        return I18nConfirmDialogMeta('customization/replace_elements', messageCtx={'description': description}, focusedID=DIALOG_BUTTON_ID.CLOSE)
    for elements, cType in zip(elementGroups, CUSTOMIZATION_TYPE.ALL):
        if elements:
            return getDialogReplaceElement(elements[0], cType)


def __formatReplaceElements(elementGroups):
    result = []
    for elements, cType in zip(elementGroups, CUSTOMIZATION_TYPE.ALL):
        if elements:
            result.append('{0} {1}'.format(__formatTypeName(cType, len(elements)), _ms(VEHICLE_CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_ELEMENTS_SEPARATOR).join(elements)))

    return '{0}{1}'.format(_ms(VEHICLE_CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_GROUPS_SEPARATOR).join(result), _ms(VEHICLE_CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_GROUPS_END))


def __formatTypeName(cType, count):
    if count > 1:
        formatter = '#vehicle_customization:dialog/remove_elements/typeName/{0}'
    else:
        formatter = '#vehicle_customization:dialog/remove_element/typeName/{0}'
    return text_styles.standard(formatter.format(cType))
