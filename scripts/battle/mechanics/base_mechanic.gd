# scripts/battle/mechanics/base_mechanic.gd
## 角色机制策略基类。每个角色一个子类, 覆写对应的生命周期回调。
class_name BaseMechanic
extends Node

var _resource_mgr: ResourceManager
var _card_mgr: CardManager
var _status_mgr: StatusManager
var _enemy_mgr: EnemyManager


func setup(rm: ResourceManager, cm: CardManager, sm: StatusManager, em: EnemyManager) -> void:
	_resource_mgr = rm
	_card_mgr = cm
	_status_mgr = sm
	_enemy_mgr = em


# ——— 生命周期回调（子类按需覆写） ———

func on_battle_start() -> void:
	pass

func on_turn_start(round_num: int) -> void:
	pass

func on_card_played(card: CardData, target: Node) -> void:
	pass

func on_turn_end() -> void:
	pass

func on_damage_dealt(source: Node, target: Node, amount: int) -> void:
	pass

func on_damage_taken(target: Node, source: Node, amount: int) -> void:
	pass

func on_kill(target: Node, is_enemy: bool) -> void:
	pass

func on_heal(target: Node, amount: int) -> void:
	pass

func on_shuffle() -> void:
	pass

func get_extra_damage(_target: Node) -> int:
	return 0

func get_extra_block() -> int:
	return 0

func get_damage_multiplier(_target: Node) -> float:
	return 1.0

func get_block_multiplier() -> float:
	return 1.0
