# scripts/battle/status_manager.gd
## 状态效果管理器。对所有实体（玩家/敌人）的 Buff/Debuff 进行增删改查和回合结算。
class_name StatusManager
extends Node

## 存储结构: {entity_instance_id: {status_id: {"stacks": int, "duration": int, "data": StatusEffectData}}}
var _statuses: Dictionary = {}
var _status_registry: Dictionary = {}  # status_id -> StatusEffectData


signal status_applied(entity: Node, status_id: String, stacks: int)
signal status_removed(entity: Node, status_id: String)
signal status_stacks_changed(entity: Node, status_id: String, current_stacks: int)
signal status_expired(entity: Node, expired_ids: Array)
signal tick_effect_triggered(entity: Node, effect: EffectData)
signal freeze_triggered(entity: Node)
signal thorn_damage(source: Node, damage: int)


## 注册状态效果数据（战斗开始时由角色 Mechanic 调用）
func register_status(data: StatusEffectData) -> void:
	_status_registry[data.status_id] = data


## 对目标施加状态
func apply_status(entity: Node, status_id: String, stacks: int = 1, duration: int = -1) -> void:
	if not status_id in _status_registry:
		push_warning("StatusManager: unknown status_id '%s'" % status_id)
		return
	var data: StatusEffectData = _status_registry[status_id]
	var key: int = entity.get_instance_id()
	if not key in _statuses:
		_statuses[key] = {}

	if status_id in _statuses[key]:
		var entry: Dictionary = _statuses[key][status_id]
		var new_duration: int = duration
		match data.stack_type:
			StatusEffectData.StackType.INTENSITY:
				var new_stacks: int = entry["stacks"] + stacks
				if data.max_stacks > 0:
					new_stacks = mini(new_stacks, data.max_stacks)
				entry["stacks"] = new_stacks
				if duration > 0:
					new_duration = maxi(entry["duration"], duration)
			StatusEffectData.StackType.DURATION_ONLY:
				new_duration = maxi(entry["duration"], duration)
			StatusEffectData.StackType.COUNTER:
				entry["stacks"] = entry["stacks"] + stacks
				new_duration = -1
		entry["duration"] = new_duration
	else:
		_statuses[key][status_id] = {
			"stacks": stacks,
			"duration": duration if duration > 0 else data.default_duration,
			"data": data
		}

	status_applied.emit(entity, status_id, stacks)

	if status_id == "frost":
		_check_freeze(entity)


## 检查目标是否有某个状态
func has_status(entity: Node, status_id: String) -> bool:
	var key: int = entity.get_instance_id()
	if not key in _statuses:
		return false
	return status_id in _statuses[key]


## 获取指定状态的层数
func get_stacks(entity: Node, status_id: String) -> int:
	var key: int = entity.get_instance_id()
	if not key in _statuses or not status_id in _statuses[key]:
		return 0
	return _statuses[key][status_id]["stacks"]


## 移除指定状态
func remove_status(entity: Node, status_id: String) -> void:
	var key: int = entity.get_instance_id()
	if key in _statuses and status_id in _statuses[key]:
		_statuses[key].erase(status_id)
		status_removed.emit(entity, status_id)


## 清除目标所有状态（冻结触发时）
func clear_all_statuses(entity: Node) -> void:
	var key: int = entity.get_instance_id()
	if key in _statuses:
		var removed: Array[String] = []
		for sid in _statuses[key].keys():
			removed.append(sid)
		_statuses[key].clear()
		for sid in removed:
			status_removed.emit(entity, sid)


## 回合结束时刷新状态：tick_effect → duration-1 → 移除到期状态
func tick_statuses(entity: Node) -> void:
	var key: int = entity.get_instance_id()
	if not key in _statuses:
		return

	var expired: Array[String] = []

	for status_id in _statuses[key].keys():
		var entry: Dictionary = _statuses[key][status_id]
		var data: StatusEffectData = entry["data"]

		for effect in data.tick_effects:
			tick_effect_triggered.emit(entity, effect)

		if entry["duration"] > 0:
			entry["duration"] -= 1
			if entry["duration"] <= 0:
				expired.append(status_id)

	for sid in expired:
		_statuses[key].erase(sid)

	if not expired.is_empty():
		status_expired.emit(entity, expired)

	if has_status(entity, "thorns"):
		var thorn_stacks: int = get_stacks(entity, "thorns")
		thorn_damage.emit(entity, thorn_stacks)


## 获取目标所有活跃状态（用于 UI 展示）
func get_active_statuses(entity: Node) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var key: int = entity.get_instance_id()
	if not key in _statuses:
		return result
	for sid in _statuses[key]:
		var entry: Dictionary = _statuses[key][sid]
		result.append({
			"status_id": sid,
			"stacks": entry["stacks"],
			"duration": entry["duration"],
			"display_name": entry["data"].display_name,
			"category": entry["data"].category,
			"icon_path": entry["data"].icon_path,
		})
	return result


## 获取伤害倍率修正（易伤/虚弱 抵消结算）
func get_damage_multiplier(entity: Node, is_dealing: bool) -> float:
	var mult: float = 1.0
	if is_dealing:
		var weak_stacks: int = get_stacks(entity, "weak")
		mult -= 0.25 * weak_stacks
	else:
		var vuln_stacks: int = get_stacks(entity, "vulnerable")
		mult += 0.25 * vuln_stacks
	return maxf(0.0, mult)


## 冰霜冻结检查（墨夜）
func _check_freeze(entity: Node) -> void:
	var frost_stacks: int = get_stacks(entity, "frost")
	if frost_stacks >= 8:
		freeze_triggered.emit(entity)
		clear_all_statuses(entity)
		apply_status(entity, "frozen", 1, 1)
