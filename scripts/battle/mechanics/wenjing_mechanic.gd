# scripts/battle/mechanics/wenjing_mechanic.gd
## 温静专属机制: 杀戮标记(增伤+引爆) + 连击计数器。
class_name WenjingMechanic
extends BaseMechanic

var _combo_counter: int = 0
var _combo_threshold: int = 3
var _mark_bonus_used: bool = false


func on_battle_start() -> void:
	_combo_counter = 0
	_mark_bonus_used = false


func on_turn_start(_round_num: int) -> void:
	_mark_bonus_used = false


func on_card_played(card: CardData, target: Node) -> void:
	if card.card_type == CardData.CardType.ATTACK:
		_combo_counter += 1
		if _combo_counter >= _combo_threshold:
			_trigger_combo()
			_combo_counter = 0


func get_extra_damage(target: Node) -> int:
	if _status_mgr and _status_mgr.has_status(target, "mark"):
		return 0  # +25% 伤害由 multiplier 处理
	return 0


func get_damage_multiplier(target: Node) -> float:
	if _status_mgr and _status_mgr.has_status(target, "mark"):
		return 1.25
	return 1.0


## 玫瑰印记: 每回合首次对被标记敌人造成伤害追加3点
func try_mark_bonus(target: Node) -> int:
	if _mark_bonus_used:
		return 0
	if _status_mgr and _status_mgr.has_status(target, "mark"):
		_mark_bonus_used = true
		return 3
	return 0


## 引爆标记: 移除标记+造成额外伤害
func detonate_mark(target: Node, base_damage: int) -> int:
	if not _status_mgr or not _status_mgr.has_status(target, "mark"):
		return base_damage
	var turns: int = _status_mgr.get_stacks(target, "mark")
	_status_mgr.remove_status(target, "mark")
	return base_damage + turns * 5


## 连击触发: 抽1张/+1精神力/全体4伤
func _trigger_combo() -> void:
	var pool: Array[int] = [0, 1, 2]
	match pool.pick_random():
		0:
			if _card_mgr:
				_card_mgr.draw_cards(1)
		1:
			if _resource_mgr:
				_resource_mgr.modify_player_energy(1)
		2:
			if _enemy_mgr:
				for enemy in _enemy_mgr.get_alive_enemies():
					_status_mgr.thorn_damage.emit(enemy, 4)


func set_combo_threshold(t: int) -> void:
	_combo_threshold = t
