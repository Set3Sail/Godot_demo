# scripts/data/equipment_card_data.gd
## 装备卡数据, 继承 CardData, 添加装备槽和耐久字段。
class_name EquipmentCardData
extends CardData

enum EquipmentSlot { WEAPON, ARMOR, ACCESSORY }

@export var equipment_slot: EquipmentSlot = EquipmentSlot.WEAPON
@export var active_effects: Array[EffectData] = []
@export var on_equip_effects: Array[EffectData] = []
@export var on_unequip_effects: Array[EffectData] = []
@export var durability: int = -1


func _init() -> void:
	card_type = CardType.EQUIPMENT
	exhaust_on_use = true
