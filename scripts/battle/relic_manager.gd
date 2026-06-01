# scripts/battle/relic_manager.gd
## 遗物管理器: 遗物注册 + 时机触发器 + 充能管理。
class_name RelicManager
extends Node

var relics: Array[RelicData] = []
var _effect_resolver: EffectResolver

signal relic_triggered(relic: RelicData, timing: String, result: Dictionary)
signal relic_gained(relic: RelicData)
signal relic_removed(relic: RelicData)
signal relic_charge_changed(relic: RelicData, current_charges: int)


func setup(resolver: EffectResolver) -> void:
    _effect_resolver = resolver


## 获得遗物
func register_relic(relic: RelicData) -> void:
    relic.init_charges()
    relics.append(relic)
    relic_gained.emit(relic)


## 移除遗物
func remove_relic(relic_id: String) -> void:
    for i in range(relics.size() - 1, -1, -1):
        if relics[i].relic_id == relic_id:
            var removed: RelicData = relics.pop_at(i)
            relic_removed.emit(removed)
            return


func has_relic(relic_id: String) -> bool:
    for relic in relics:
        if relic.relic_id == relic_id:
            return true
    return false


func get_relic(relic_id: String) -> RelicData:
    for relic in relics:
        if relic.relic_id == relic_id:
            return relic
    return null


## 触发指定时机的所有遗物
func trigger(timing: String, context: Dictionary) -> void:
    for relic in relics:
        if relic.trigger_timing != timing:
            continue
        if not relic.can_trigger():
            continue
        if not relic.trigger_condition.is_empty():
            if not _check_condition(relic.trigger_condition, context):
                continue
        relic.consume_charge()
        relic_charge_changed.emit(relic, relic.current_charges)
        for effect in relic.effects:
            if _effect_resolver:
                _effect_resolver.resolve_effects([effect], context.get("source", self), true)
        relic_triggered.emit(relic, timing, {})


## 充能管理
func add_charge(relic_id: String, amount: int) -> void:
    var relic: RelicData = get_relic(relic_id)
    if relic and relic.max_charges > 0:
        relic.current_charges = mini(relic.max_charges, relic.current_charges + amount)
        relic_charge_changed.emit(relic, relic.current_charges)


func _check_condition(condition: String, context: Dictionary) -> bool:
    if condition == "round <= 3":
        return context.get("round", 99) <= 3
    if condition == "hand.size() <= 3":
        return context.get("hand_size", 99) <= 3
    if condition == "HP < 50%":
        var hp: int = context.get("current_hp", 0)
        var max_hp: int = context.get("max_hp", 1)
        return float(hp) / float(max_hp) < 0.5
    return true
