# scripts/battle/resource_manager.gd
## 战斗中所有数值资源管理: HP、精神力、力量、敏捷、格挡、魔晶。
## 通过信号通知 UI 层资源变化。
class_name ResourceManager
extends Node

# ——— 玩家资源 ———
var _player_hp: int = 0
var _player_max_hp: int = 75
var _player_energy: int = 3
var _max_energy_per_turn: int = 3
var _player_block: int = 0
var _player_strength: int = 0
var _player_dexterity: int = 0
var _crystals: int = 0

# ——— 敌人资源（字典, key = Enemy 的 instance_id） ———
var _enemy_hp: Dictionary = {}             # id: current_hp
var _enemy_max_hp: Dictionary = {}         # id: max_hp
var _enemy_block: Dictionary = {}          # id: block
var _enemy_strength: Dictionary = {}       # id: strength
var _enemy_dexterity: Dictionary = {}      # id: dexterity

# ——— 信号 ———
signal player_hp_changed(current: int, max_hp: int, delta: int)
signal player_energy_changed(current: int)
signal player_block_changed(current: int)
signal player_strength_changed(value: int)
signal player_dexterity_changed(value: int)
signal crystals_changed(count: int)
signal entity_hp_changed(entity: Node, current: int, max_hp: int, delta: int)
signal entity_block_changed(entity: Node, current: int)
signal entity_died(entity: Node, killer: Node)
signal player_died


## 初始化玩家资源
func init_player(hp: int, max_hp: int, energy: int = 3) -> void:
	_player_hp = hp
	_player_max_hp = max_hp
	_player_energy = energy
	_max_energy_per_turn = energy
	_player_block = 0
	_player_strength = 0
	_player_dexterity = 0
	_crystals = 0
	player_hp_changed.emit(_player_hp, _player_max_hp, 0)
	player_energy_changed.emit(_player_energy)


## 注册敌人到资源管理器
func register_enemy(enemy: Node, max_hp: int) -> void:
	var key: int = enemy.get_instance_id()
	_enemy_hp[key] = max_hp
	_enemy_max_hp[key] = max_hp
	_enemy_block[key] = 0
	_enemy_strength[key] = 0
	_enemy_dexterity[key] = 0


## 注销敌人
func unregister_enemy(enemy: Node) -> void:
	var key: int = enemy.get_instance_id()
	_enemy_hp.erase(key)
	_enemy_max_hp.erase(key)
	_enemy_block.erase(key)
	_enemy_strength.erase(key)
	_enemy_dexterity.erase(key)


# ——— 玩家方法 ———

func get_player_hp() -> int:  return _player_hp
func get_player_max_hp() -> int:  return _player_max_hp
func get_player_energy() -> int:  return _player_energy
func get_player_block() -> int:  return _player_block
func get_player_strength() -> int:  return _player_strength
func get_player_dexterity() -> int:  return _player_dexterity
func get_crystals() -> int:  return _crystals


## 伤害/治疗入口。damage_type: "normal" / "holy" (神圣伤害无视格挡)
func modify_player_hp(delta: int, damage_type: String = "normal") -> void:
	if delta < 0:
		var actual_damage: int = _calculate_damage(-delta, _player_block, damage_type)
		_player_hp = maxi(0, _player_hp - actual_damage)
	else:
		_player_hp = mini(_player_max_hp, _player_hp + delta)
	player_hp_changed.emit(_player_hp, _player_max_hp, delta)
	_check_player_death()


func modify_player_max_hp(delta: int) -> void:
	_player_max_hp = maxi(1, _player_max_hp + delta)
	_player_hp = mini(_player_hp, _player_max_hp)
	player_hp_changed.emit(_player_hp, _player_max_hp, 0)


func modify_player_energy(delta: int) -> void:
	_player_energy = maxi(0, _player_energy + delta)
	player_energy_changed.emit(_player_energy)


func modify_player_block(delta: int) -> void:
	_player_block = maxi(0, _player_block + delta)
	player_block_changed.emit(_player_block)


func modify_player_strength(delta: int) -> void:
	_player_strength += delta
	player_strength_changed.emit(_player_strength)


func modify_player_dexterity(delta: int) -> void:
	_player_dexterity += delta
	player_dexterity_changed.emit(_player_dexterity)


func add_crystals(amount: int) -> void:
	_crystals += amount
	crystals_changed.emit(_crystals)


# ——— 敌人方法 ———

func get_enemy_hp(enemy: Node) -> int:
	var key: int = enemy.get_instance_id()
	return _enemy_hp.get(key, 0)


func get_enemy_max_hp(enemy: Node) -> int:
	var key: int = enemy.get_instance_id()
	return _enemy_max_hp.get(key, 0)


func get_enemy_block(enemy: Node) -> int:
	var key: int = enemy.get_instance_id()
	return _enemy_block.get(key, 0)


func get_enemy_strength(enemy: Node) -> int:
	var key: int = enemy.get_instance_id()
	return _enemy_strength.get(key, 0)


func get_enemy_dexterity(enemy: Node) -> int:
	var key: int = enemy.get_instance_id()
	return _enemy_dexterity.get(key, 0)


func modify_enemy_hp(enemy: Node, delta: int, damage_type: String = "normal") -> void:
	var key: int = enemy.get_instance_id()
	var current_hp: int = _enemy_hp.get(key, 0)
	var max_hp: int = _enemy_max_hp.get(key, 0)
	if delta < 0:
		var block: int = _enemy_block.get(key, 0)
		var actual: int = _calculate_damage(-delta, block, damage_type)
		_enemy_hp[key] = maxi(0, current_hp - actual)
	else:
		_enemy_hp[key] = mini(max_hp, current_hp + delta)
	entity_hp_changed.emit(enemy, _enemy_hp[key], max_hp, delta)
	if _enemy_hp[key] <= 0:
		_on_entity_death(enemy, null)


func modify_enemy_block(enemy: Node, delta: int) -> void:
	var key: int = enemy.get_instance_id()
	var current: int = _enemy_block.get(key, 0)
	_enemy_block[key] = maxi(0, current + delta)
	entity_block_changed.emit(enemy, _enemy_block[key])


func modify_enemy_strength(enemy: Node, delta: int) -> void:
	var key: int = enemy.get_instance_id()
	_enemy_strength[key] = _enemy_strength.get(key, 0) + delta


func modify_enemy_dexterity(enemy: Node, delta: int) -> void:
	var key: int = enemy.get_instance_id()
	_enemy_dexterity[key] = _enemy_dexterity.get(key, 0) + delta


# ——— 回合方法 ———

## 回合开始时调用：精神力回满，格挡清零
func on_turn_start() -> void:
	_player_energy = _max_energy_per_turn
	_player_block = 0
	player_energy_changed.emit(_player_energy)
	player_block_changed.emit(_player_block)
	for key in _enemy_block.keys():
		_enemy_block[key] = 0
		var enemy: Node = instance_from_id(key)
		if enemy:
			entity_block_changed.emit(enemy, 0)


## 回合结束时调用
func on_turn_end() -> void:
	_player_block = 0
	player_block_changed.emit(_player_block)


# ——— 属性加成 ———

## 计算有效伤害值 = 基础值 + 力量
func get_effective_damage(base: int, is_player: bool = true) -> int:
	var extra: int = _player_strength if is_player else 0
	return maxi(0, base + extra)


## 计算有效格挡值 = 基础值 + 敏捷
func get_effective_block(base: int, is_player: bool = true) -> int:
	var extra: int = _player_dexterity if is_player else 0
	return maxi(0, base + extra)


# ——— 内部方法 ———

func _calculate_damage(raw: int, block: int, damage_type: String) -> int:
	if damage_type == "holy":
		return raw  # 神圣伤害无视格挡
	var blocked: int = mini(raw, block)
	var actual: int = raw - blocked
	return maxi(1, actual)  # 至少 1 点伤害


func _check_player_death() -> void:
	if _player_hp <= 0:
		player_died.emit()


func _on_entity_death(entity: Node, killer: Node) -> void:
	entity_died.emit(entity, killer)
