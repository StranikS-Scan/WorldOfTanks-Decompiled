# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/perks_constants.py
PERKS_XML_FILE = 'perks.xml'

class PERKS_TYPE:
    SIMPLE = 1
    ULTIMATE = 2
    ANY = SIMPLE | ULTIMATE
    CONFIGURATION_MAPPING = {True: ULTIMATE,
     False: SIMPLE}
