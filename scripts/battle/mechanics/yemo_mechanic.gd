# scripts/battle/mechanics/yemo_mechanic.gd
## 叶默专属机制: 锻造升级（战斗中临时升级手牌）+ 荆棘（回合结束自动伤害）
class_name YemoMechanic
extends BaseMechanic

var _thorn_stacks: int = 0
var _forge_used_this_turn: bool = false


func on_battle_start() -> void:
	_thorn_stacks = 2  # 初始遗物变异种子袋效果


func on_turn_end() -> void:
	if _thorn_stacks > 0 and _enemy_mgr:
		for enemy in _enemy_mgr.get_alive_enemies():
			_status_mgr.thorn_damage.emit(enemy, _thorn_stacks)


func on_card_played(card: CardData, _target: Node) -> void:
	if "锻造" in card.keywords:
		_forge_random_card()


func get_extra_damage(target: Node) -> int:
	var extra: int = 0
	if _status_mgr.has_status(target, "thorns"):
		extra += _thorn_stacks
	return extra


func add_thorns(amount: int) -> void:
	_thorn_stacks += amount


## 叶默锻造：随机升级手牌中一张卡
func _forge_random_card() -> void:
	var hand_cards: Array = _card_mgr.hand
	if hand_cards.is_empty():
		return
	var candidates: Array[CardData] = []
	for c in hand_cards:
		if c.forge_count < c._forge_max:
			candidates.append(c)
	if candidates.is_empty():
		return
	var target: CardData = candidates.pick_random()
	_card_mgr.forge_card_in_hand(target)
