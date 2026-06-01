# scripts/battle/mechanics/moye_mechanic.gd
## 墨夜专属机制: 冰霜叠层减伤+冻结 + 天怒标签首次双倍伤害。
class_name MoyeMechanic
extends BaseMechanic

var _fury_used: bool = false
var _frost_energy_counter: int = 0
var _frost_triggers_this_turn: int = 0
const FROST_MAX_TRIGGERS: int = 2


func on_battle_start() -> void:
	_fury_used = false
	_frost_energy_counter = 0
	_frost_triggers_this_turn = 0


func on_turn_start(_round_num: int) -> void:
	_frost_triggers_this_turn = 0


## 天怒: 每场战斗首次使用天怒标签卡牌伤害×2
func try_activate_fury() -> float:
	if not _fury_used:
		_fury_used = true
		return 2.0
	return 1.0


## 冰晶护符: 每施加3层冰霜获得1精神力（每回合最多2次）
func on_frost_applied(stacks: int) -> void:
	if _frost_triggers_this_turn >= FROST_MAX_TRIGGERS:
		return
	_frost_energy_counter += stacks
	while _frost_energy_counter >= 3 and _frost_triggers_this_turn < FROST_MAX_TRIGGERS:
		_frost_energy_counter -= 3
		_frost_triggers_this_turn += 1
		if _resource_mgr:
			_resource_mgr.modify_player_energy(1)
