# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/configs/halloween_bestiary.py
from __future__ import absolute_import
from game_params_common.base_manager import GameParamsSchema
from dict2model import models, fields, schemas
from halloween_common.halloween_constants import HALLOWEEN_BESTIARY_PARAMS_KEY

class SoundsModel(models.Model):
    __slots__ = ('select',)

    def __init__(self, select):
        super(SoundsModel, self).__init__()
        self.select = select


class ShopModel(models.Model):
    __slots__ = ('vehicle', 'bundles')

    def __init__(self, vehicle, bundles):
        super(ShopModel, self).__init__()
        self.vehicle = vehicle
        self.bundles = bundles or []
        if self.bundles and not self.vehicle:
            raise ValueError('The vehicle must not be empty.')


class EnemyModel(models.Model):
    __slots__ = ('name', 'unlockedByToken', 'style', 'ability', 'shop', 'needShowInHangar', 'sounds')

    def __init__(self, name, unlockedByToken, style, ability, shop, needShowInHangar, sounds):
        super(EnemyModel, self).__init__()
        self.name = name
        self.unlockedByToken = unlockedByToken
        self.style = style
        self.ability = ability
        self.shop = shop
        self.needShowInHangar = needShowInHangar
        self.sounds = sounds


class EnemiesModel(models.Model):
    __slots__ = ('enemy',)

    def __init__(self, enemy):
        super(EnemiesModel, self).__init__()
        self.enemy = enemy


class BestiaryModel(models.Model):
    __slots__ = ('enemies',)

    def __init__(self, enemies):
        super(BestiaryModel, self).__init__()
        self.enemies = enemies


shopSchema = schemas.Schema(fields={'vehicle': fields.String(required=False),
 'bundles': fields.ListFromString(field=fields.String(), required=False)}, modelClass=ShopModel, checkUnknown=True)
soundsSchema = schemas.Schema(fields={'select': fields.String(required=False)}, modelClass=SoundsModel, checkUnknown=True)
enemySchema = schemas.Schema(fields={'name': fields.String(required=True),
 'unlockedByToken': fields.String(required=True),
 'style': fields.Integer(required=False),
 'ability': fields.String(required=False),
 'shop': fields.Nested(schema=shopSchema, required=False),
 'needShowInHangar': fields.Boolean(required=True),
 'sounds': fields.Nested(schema=soundsSchema)}, modelClass=EnemyModel, checkUnknown=True)
enemiesSchema = schemas.Schema(fields={'enemy': fields.List(fieldOrSchema=enemySchema, required=True)}, modelClass=EnemiesModel, checkUnknown=True)
bestiarySchema = GameParamsSchema[BestiaryModel](gameParamsKey=HALLOWEEN_BESTIARY_PARAMS_KEY, fields={'enemies': fields.Nested(schema=enemiesSchema, required=True)}, modelClass=BestiaryModel, checkUnknown=True, usedInReplay=True)
