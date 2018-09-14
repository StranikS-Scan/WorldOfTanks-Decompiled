# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization_2_0/shared.py
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.locale.CUSTOMIZATION import CUSTOMIZATION
from gui.customization_2_0.data_aggregator import CUSTOMIZATION_TYPE
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms

def getDialogRemoveElement(itemName, cType):
    deleteStr = text_styles.error(CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_DELETE)
    description = text_styles.main(_ms(CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_DESCRIPTION, elementName='{0} {1}'.format(__formatTypeName(cType, 1), text_styles.main(itemName)), delete=deleteStr))
    return I18nConfirmDialogMeta('customization/remove_element', messageCtx={'description': description}, focusedID=DIALOG_BUTTON_ID.CLOSE)


def getDialogReplaceElement(itemName, cType):
    deleteStr = text_styles.error(CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_DELETE)
    description = text_styles.main(_ms(CUSTOMIZATION.DIALOG_REPLACE_ELEMENT_DESCRIPTION, elementName='{0} {1}'.format(__formatTypeName(cType, 1), text_styles.main(itemName)), delete=deleteStr))
    return I18nConfirmDialogMeta('customization/replace_element', messageCtx={'description': description}, focusedID=DIALOG_BUTTON_ID.CLOSE)


def getDialogReplaceElements(elements):
    replaceElementCount = 0
    for replaceElements in elements:
        replaceElementCount += len(replaceElements)

    if replaceElementCount > 1:
        deleteStr = text_styles.error(CUSTOMIZATION.DIALOG_REMOVE_ELEMENTS_DELETE)
        description = text_styles.main(_ms(CUSTOMIZATION.DIALOG_REPLACE_ELEMENTS_DESCRIPTION, elementsName=__formatReplaceElements(elements), delete=deleteStr))
        return I18nConfirmDialogMeta('customization/replace_elements', messageCtx={'description': description}, focusedID=DIALOG_BUTTON_ID.CLOSE)
    for type in (CUSTOMIZATION_TYPE.CAMOUFLAGE, CUSTOMIZATION_TYPE.EMBLEM, CUSTOMIZATION_TYPE.INSCRIPTION):
        if elements[type]:
            return getDialogReplaceElement(elements[type][0], type)


def __formatReplaceElements(elements):
    rez = []
    for items in elements:
        count = len(items)
        if count > 0:
            separator = _ms(CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_ELEMENTS_SEPARATOR)
            rez.append('{0} {1}'.format(__formatTypeName(elements.index(items), count), separator.join(items)))

    return '{0}{1}'.format(_ms(CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_GROUPS_SEPARATOR).join(rez), _ms(CUSTOMIZATION.DIALOG_REMOVE_ELEMENT_GROUPS_END))


def __formatTypeName(cType, count):
    if count > 1:
        formatter = '#customization:dialog/remove_elements/typeName/{0}'
    else:
        formatter = '#customization:dialog/remove_element/typeName/{0}'
    return text_styles.standard(formatter.format(cType))
