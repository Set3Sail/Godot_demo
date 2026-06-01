# scripts/battle/enemy_manager.gd
## 敌人管理器: 敌方格 + 友方格 slot 管理 + AI 调度。
class_name EnemyManager
extends Node

const MAX_ENEMY_SLOTS: int = 5
const MAX_ALLY_SLOTS: int = 5

var _enemies: Array[Node] = []               # 存活敌人列表（按 slot 顺序）
var _allies: Array[Node] = []                # 友方随从（红发丧尸）
var _enemy_data_map: Dictionary = {}          # Node -> EnemyData
var _enemy_ai_map: Dictionary = {}            # Node -> IntentData
var _crystal_drops: Dictionary = {}           # Node -> crystal count

signal enemy_intent_revealed(enemy: Node, intent: IntentData)
signal enemy_acted(enemy: Node, intent: IntentData, result: Dictionary)
signal enemy_spawned(enemy: Node, slot_index: int)
signal enemy_killed(enemy: Node, crystal_reward: int)
signal boss_phase_changed(boss: Node, phase_index: int)
signal ally_spawned(ally: Node, slot_index: int)
signal ally_acted(ally: Node, target: Node, damage: int)
signal ally_killed(ally: Node)


## 根据 EnemyData 生成敌人并加入敌方格
func spawn_enemy(data: EnemyData, slot_index: int = -1) -> Node:
	var enemy := Node.new()
	enemy.set_meta("enemy_id", data.enemy_id)
	enemy.set_meta("display_name", data.display_name)
	add_child(enemy)
	var rm: ResourceManager = _get_resource_manager()
	rm.register_enemy(enemy, data.base_hp)
	_enemy_data_map[enemy] = data
	_crystal_drops[enemy] = data.crystal_drop

	if slot_index == -1 or slot_index >= MAX_ENEMY_SLOTS:
		_enemies.append(enemy)
	else:
		_enemies.insert(slot_index, enemy)

	_generate_and_reveal_intent(enemy, data)
	enemy_spawned.emit(enemy, _enemies.find(enemy))
	return enemy


## 移除敌人
func remove_enemy(enemy: Node) -> void:
	var idx: int = _enemies.find(enemy)
	if idx != -1:
		_enemies.remove_at(idx)
	var rm: ResourceManager = _get_resource_manager()
	rm.unregister_enemy(enemy)
	_enemy_data_map.erase(enemy)
	_crystal_drops.erase(enemy)
	_enemy_ai_map.erase(enemy)
	if is_instance_valid(enemy):
		enemy.queue_free()


## 执行所有敌方意图（ENEMY_TURN 阶段）
func execute_all_enemy_intents() -> void:
	for enemy in _enemies:
		if not is_instance_valid(enemy):
			continue
		var intent: IntentData = _enemy_ai_map.get(enemy)
		if intent:
			_execute_intent(enemy, intent)
			var data: EnemyData = _enemy_data_map.get(enemy)
			if data:
				_generate_and_reveal_intent(enemy, data)


## 友方随从自动攻击
func ally_auto_attack_all() -> void:
	for ally in _allies:
		if not is_instance_valid(ally):
			continue
		var enemies: Array = get_alive_enemies()
		if enemies.is_empty():
			return
		var target: Node = enemies.pick_random()
		var damage: int = ally.get_meta("attack_damage", 3)
		ally_acted.emit(ally, target, damage)


## 获取存活敌人列表
func get_alive_enemies() -> Array[Node]:
	var alive: Array[Node] = []
	for enemy in _enemies:
		if is_instance_valid(enemy) and _get_resource_manager().get_enemy_hp(enemy) > 0:
			alive.append(enemy)
	return alive


func get_frontmost_enemy() -> Node:
	for enemy in _enemies:
		if is_instance_valid(enemy) and _get_resource_manager().get_enemy_hp(enemy) > 0:
			return enemy
	return null


func get_alive_allies() -> Array[Node]:
	var alive: Array[Node] = []
	for ally in _allies:
		if is_instance_valid(ally):
			alive.append(ally)
	return alive


func get_crystal_drop(enemy: Node) -> int:
	return _crystal_drops.get(enemy, 0)


# ——— 内部 ———

func _generate_and_reveal_intent(enemy: Node, data: EnemyData) -> void:
	if data.intent_pattern.is_empty():
		return
	var intent: IntentData = data.intent_pattern[0]
	_enemy_ai_map[enemy] = intent
	enemy_intent_revealed.emit(enemy, intent)


func _execute_intent(enemy: Node, intent: IntentData) -> void:
	var result: Dictionary = {}
	var rm: ResourceManager = _get_resource_manager()
	match intent.type:
		IntentData.IntentType.ATTACK:
			var target: Node = _get_player_node()
			var dmg: int = _calculate_actual_value(intent.base_value, intent.value_variance)
			rm.modify_player_hp(-dmg, "normal")
			result = {"damage": dmg}
		IntentData.IntentType.DEFEND:
			var block_amount: int = _calculate_actual_value(intent.base_value, intent.value_variance)
			rm.modify_enemy_block(enemy, block_amount)
			result = {"block": block_amount}
		IntentData.IntentType.BUFF:
			var sm: StatusManager = _get_status_manager()
			sm.apply_status(enemy, intent.status_id, intent.secondary_value, intent.status_duration)
			result = {"status": intent.status_id, "stacks": intent.secondary_value}
		IntentData.IntentType.DEBUFF:
			var sm: StatusManager = _get_status_manager()
			var target: Node = _get_player_node()
			sm.apply_status(target, intent.status_id, intent.secondary_value, intent.status_duration)
			result = {"status": intent.status_id, "stacks": intent.secondary_value}
		IntentData.IntentType.SUMMON:
			pass
		IntentData.IntentType.SPECIAL:
			pass
	enemy_acted.emit(enemy, intent, result)


func _calculate_actual_value(base: int, variance: float) -> int:
	var min_val: int = int(ceilf(base * (1.0 - variance)))
	var max_val: int = int(ceilf(base * (1.0 + variance)))
	return randi_range(min_val, max_val)


func _get_resource_manager() -> ResourceManager:
	return get_parent().get_node("ResourceManager") as ResourceManager


func _get_status_manager() -> StatusManager:
	return get_parent().get_node("StatusManager") as StatusManager


func _get_player_node() -> Node:
	return get_tree().get_first_node_in_group("player")
