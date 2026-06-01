# scripts/battle/mechanics/jinying_mechanic.gd
## 金英专属机制: 神罚(治疗蓄能→神圣伤害) + 亲和(无伤回合回复)。
class_name JinyingMechanic
extends BaseMechanic

var _holy_charge: int = 0
var _heal_tracker: int = 0
var _damage_taken_this_turn: int = 0


func on_battle_start() -> void:
	_holy_charge = 0
	_heal_tracker = 0
	_damage_taken_this_turn = 0


func on_turn_start(_round_num: int) -> void:
	_damage_taken_this_turn = 0


## 治疗蓄能: 治疗量累加为神罚弹药
func on_heal(_target: Node, amount: int) -> void:
	_holy_charge += amount
	# 神圣之触遗物: 每回复4HP对随机敌人造成3神圣伤害
	_heal_tracker += amount
	while _heal_tracker >= 4:
		_heal_tracker -= 4
		if _enemy_mgr:
			var enemies: Array = _enemy_mgr.get_alive_enemies()
			if not enemies.is_empty():
				var enemy: Node = enemies.pick_random()
				_status_mgr.thorn_damage.emit(enemy, 3)


func on_damage_taken(_target: Node, _source: Node, amount: int) -> void:
	_damage_taken_this_turn += amount


## 亲和: 回合结束若本回合未受伤回复2HP
func on_turn_end() -> void:
	if _damage_taken_this_turn == 0 and _resource_mgr:
		_resource_mgr.modify_player_hp(2, "heal")


## 消耗神罚蓄能转化为神圣伤害量
func consume_holy_charge(amount: int) -> int:
	var consumed: int = mini(amount, _holy_charge)
	_holy_charge -= consumed
	return consumed


func get_holy_charge() -> int:
	return _holy_charge
