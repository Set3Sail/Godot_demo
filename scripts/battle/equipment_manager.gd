# scripts/battle/equipment_manager.gd
## 装备槽管理器: 武器/防具/饰品三槽 + 装备/卸下/替换 + 结算管道集成。
class_name EquipmentManager
extends Node

var slots: Dictionary = {
    "WEAPON": null,
    "ARMOR": null,
    "ACCESSORY": null,
}

var _effect_resolver: EffectResolver

signal equipment_equipped(card: EquipmentCardData, slot: String)
signal equipment_unequipped(card: EquipmentCardData, slot: String)
signal equipment_durability_changed(card: EquipmentCardData, current: int)


func setup(resolver: EffectResolver) -> void:
    _effect_resolver = resolver


func equip(card: EquipmentCardData) -> void:
    var slot: String = _slot_to_string(card.equipment_slot)
    if slots[slot] != null:
        unequip(slots[slot])
    slots[slot] = card
    if _effect_resolver:
        _effect_resolver.resolve_effects(card.on_equip_effects, self, true)
    equipment_equipped.emit(card, slot)


func unequip(card: EquipmentCardData) -> void:
    var slot: String = _slot_to_string(card.equipment_slot)
    if _effect_resolver:
        _effect_resolver.resolve_effects(card.on_unequip_effects, self, true)
    slots[slot] = null
    equipment_unequipped.emit(card, slot)


## 获取指定槽位的持续效果
func get_slot_active_effects(slot_name: String) -> Array[EffectData]:
    var card: EquipmentCardData = slots.get(slot_name)
    if card == null:
        return []
    return card.active_effects


## 获取额外伤害修正
func get_extra_damage() -> int:
    var total: int = 0
    for slot_name in ["WEAPON", "ACCESSORY"]:
        for effect in get_slot_active_effects(slot_name):
            if effect.type == EffectData.EffectType.DAMAGE:
                total += effect.base_value
    return total


## 获取额外格挡修正
func get_extra_block() -> int:
    var total: int = 0
    for effect in get_slot_active_effects("ARMOR"):
        if effect.type == EffectData.EffectType.BLOCK:
            total += effect.base_value
    return total


func _slot_to_string(slot: int) -> String:
    match slot:
        EquipmentCardData.EquipmentSlot.WEAPON:  return "WEAPON"
        EquipmentCardData.EquipmentSlot.ARMOR:    return "ARMOR"
        EquipmentCardData.EquipmentSlot.ACCESSORY: return "ACCESSORY"
    return "WEAPON"
