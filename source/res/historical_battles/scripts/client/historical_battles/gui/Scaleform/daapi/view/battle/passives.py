# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/passives.py
import ResMgr
from items import _xml
PATH = 'historical_battles/gui/passives.xml'

class PassivesConfig(object):
    _instance = None

    def __init__(self):
        self.passives = {}
        self.loadFromXml(PATH)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PassivesConfig, cls).__new__(cls)
        return cls._instance

    def loadFromXml(self, path):
        section = ResMgr.openSection(path)
        xmlCtx = (path, None)
        if section is None:
            _xml.raiseWrongXml(xmlCtx, path, 'can not open or read')
        for passives in section.values():
            passiveConfig = {'id': _xml.readInt(xmlCtx, passives, 'id')}
            passiveConfig['greenStateLivesCount'] = _xml.readInt(xmlCtx, passives, 'greenStateLivesCount')
            for stateName, state in passives['states'].items():
                stateConfig = {'iconPath': _xml.readString(xmlCtx, state, 'iconPath'),
                 'titleKey': _xml.readString(xmlCtx, state, 'titleKey'),
                 'descriptionKey': _xml.readString(xmlCtx, state, 'descriptionKey')}
                passiveConfig[stateName] = stateConfig
                passiveName = _xml.readString(xmlCtx, passives, 'name')
                self.passives[passiveName] = passiveConfig

        return
