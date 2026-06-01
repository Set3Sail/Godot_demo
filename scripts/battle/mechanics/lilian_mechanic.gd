# scripts/battle/mechanics/lilian_mechanic.gd
## 莉莲专属机制: 战甲攻/防双模式切换 + 过热管理 + 双面卡。
class_name LilianMechanic
extends BaseMechanic

enum ArmorMode { ATTACK, DEFENSE }

var _current_mode: ArmorMode = ArmorMode.ATTACK
var _switch_counter: int = 0
var _overheat_threshold: int = 3
var _is_overheated: bool = false
var _free_switches_this_turn: int = 1
var _switches_used: int = 0


func on_battle_start() -> void:
	_current_mode = ArmorMode.ATTACK
	_switch_counter = 0
	_is_overheated = false
	_switches_used = 0


func on_turn_start(_round_num: int) -> void:
	_switches_used = 0
	if _is_overheated:
		_is_overheated = false
		if _resource_mgr:
			_resource_mgr.modify_player_strength(2)
			_resource_mgr.modify_player_dexterity(2)


func on_turn_end() -> void:
	if not _resource_mgr:
		return
	match _current_mode:
		ArmorMode.ATTACK:
			_resource_mgr.modify_player_hp(-2, "normal")
		ArmorMode.DEFENSE:
			_resource_mgr.modify_player_hp(2, "heal")


## 切换模式
func switch_mode() -> void:
	if _is_overheated:
		return
	if _switches_used >= _free_switches_this_turn:
		if not _resource_mgr or _resource_mgr.get_player_energy() < 1:
			return
		_resource_mgr.modify_player_energy(-1)
	_switches_used += 1
	_current_mode = ArmorMode.DEFENSE if _current_mode == ArmorMode.ATTACK else ArmorMode.ATTACK
	_switch_counter += 1
	if _switch_counter >= _overheat_threshold:
		_is_overheated = true
		_switch_counter = 0


func get_damage_multiplier(_target: Node) -> float:
	return 1.3 if _current_mode == ArmorMode.ATTACK else 1.0


func get_block_multiplier() -> float:
	return 1.3 if _current_mode == ArmorMode.DEFENSE else 1.0


func get_current_mode() -> ArmorMode:
	return _current_mode


func set_overheat_threshold(t: int) -> void:
	_overheat_threshold = t
