# scripts/battle/mechanics/moye_mechanic.gd
## 墨夜专属机制: 冰霜叠层减伤+冻结 + 天怒标签双倍伤害。
class_name MoyeMechanic
extends BaseMechanic

var _fury_used: bool = false
var _frost_energy_counter: int = 0
var _frost_energy_triggers_this_turn: int = 0
const FROST_ENERGY_MAX_PER_TURN: int = 2


func on_battle_start() -> void:
	_fury_used = false
	_frost_energy_counter = 0
	_frost_energy_triggers_this_turn = 0


func on_turn_start(_round_num: int) -> void:
	_frost_energy_triggers_this_turn = 0


## 天怒标签: 每场战斗首次使用伤害 ×2
func try_activate_fury() -> float:
	if not _fury_used:
		_fury_used = true
		return 2.0
	return 1.0


## 冰晶护符: 每施加 3 层冰霜, 获得 1 精神力（每回合最多 2 次）
func on_frost_applied(stacks: int) -> void:
	if _frost_energy_triggers_this_turn >= FROST_ENERGY_MAX_PER_TURN:
		return
	_frost_energy_counter += stacks
	while _frost_energy_counter >= 3 and _frost_energy_triggers_this_turn < FROST_ENERGY_MAX_PER_TURN:
		_frost_energy_counter -= 3
		_frost_energy_triggers_this_turn += 1
		if _resource_mgr:
			_resource_mgr.modify_player_energy(1)


## 冰霜减伤: 每层冰霜使敌人造成的伤害 -5%
func get_damage_multiplier(_target: Node) -> float:
	# 此方法在 EffectResolver 计算敌人对玩家伤害时调用
	# 冰霜减伤逻辑在 EffectResolver._execute_damage 的 damage_multiplier 中处理
	return 1.0
