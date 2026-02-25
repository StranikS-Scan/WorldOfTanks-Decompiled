# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/configs/modes/mode.py
from __future__ import absolute_import
import typing
from dict2model import fields, models, schemas
from fun_random.gui.feature.configs.modes.assets_pack import funModeAssetsPackConfigurationSchema
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.configs.modes.assets_pack import FunModeAssetsPackConfigurationModel

class FunModeConfigurationModel(models.Model):
    __slots__ = ('assetsPack',)

    def __init__(self, assetsPack):
        super(FunModeConfigurationModel, self).__init__()
        self.assetsPack = assetsPack


class FunModeCompositeConfigurationModel(models.Model):
    __slots__ = ('mode',)

    def __init__(self, mode):
        super(FunModeCompositeConfigurationModel, self).__init__()
        self.mode = mode


funModeConfigurationSchema = schemas.Schema[FunModeConfigurationModel](fields={'assetsPack': fields.Nested(schema=funModeAssetsPackConfigurationSchema, required=True)}, modelClass=FunModeConfigurationModel)
funModeCompositeConfigurationSchema = schemas.Schema[FunModeCompositeConfigurationModel](fields={'mode': fields.Nested(schema=funModeConfigurationSchema, required=True)}, modelClass=FunModeCompositeConfigurationModel)
