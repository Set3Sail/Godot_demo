# scripts/battle/mechanics/hongfa_mechanic.gd
## 红发专属机制: 召唤丧尸随从 + 牺牲爆发 + 恐惧控制。
class_name HongfaMechanic
extends BaseMechanic

var _max_zombies: int = 4
var _zombie_counter: int = 0


func on_battle_start() -> void:
	_zombie_counter = 0


## 召唤丧尸到友方格
func summon_zombie(hp: int = 10, attack: int = 5) -> Node:
	if _enemy_mgr.get_alive_allies().size() >= _max_zombies:
		return null
	_zombie_counter += 1
	var zombie := Node.new()
	zombie.set_meta("display_name", "丧尸%d" % _zombie_counter)
	zombie.set_meta("max_hp", hp)
	zombie.set_meta("current_hp", hp)
	zombie.set_meta("attack_damage", attack)
	_enemy_mgr._allies.append(zombie)
	_enemy_mgr.add_child(zombie)
	_enemy_mgr.ally_spawned.emit(zombie, _enemy_mgr._allies.find(zombie))
	return zombie


## 牺牲所有丧尸, 返回数量(狂物之鸣用)
func sacrifice_all_zombies() -> int:
	var allies: Array = _enemy_mgr.get_alive_allies()
	var count: int = allies.size()
	for ally in allies:
		_enemy_mgr._allies.erase(ally)
		_enemy_mgr.ally_killed.emit(ally)
		if is_instance_valid(ally):
			ally.queue_free()
	return count


## 丧尸死亡→+2格挡
func on_ally_killed() -> void:
	if _resource_mgr:
		_resource_mgr.modify_player_block(2)


## 意识结晶: 每只存活丧尸+1格挡/回合(最多+4)
func get_extra_block() -> int:
	if not _enemy_mgr:
		return 0
	var alive: int = _enemy_mgr.get_alive_allies().size()
	return mini(alive, 4)


## 遗物扩展最大丧尸数
func set_max_zombies(n: int) -> void:
	_max_zombies = n
