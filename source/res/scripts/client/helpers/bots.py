# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/bots.py
import i18n
from constants import LOCALIZABLE_BOT_NAME, IS_DEVELOPMENT
from items import tankmen

def preprocessBotName(name):
    ids = LOCALIZABLE_BOT_NAME.parse(name)
    if ids is not None:
        nationID, firstNameID, lastNameID = ids
        nationConfig = tankmen.getNationConfig(nationID)
        firstName = i18n.convert(nationConfig.getFirstName(firstNameID))
        lastName = i18n.convert(nationConfig.getLastName(lastNameID))
        if IS_DEVELOPMENT:
            name = '{0}_{1}_{2} :{3} {4}:'.format(nationID, firstNameID, lastNameID, firstName, lastName)
        else:
            name = ':{0} {1}:'.format(firstName, lastName)
    return name
