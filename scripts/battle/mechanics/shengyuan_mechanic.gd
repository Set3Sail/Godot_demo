# scripts/battle/mechanics/shengyuan_mechanic.gd
## 盛元专属机制: 复仇叠层(损血增伤) + 血祭(自伤换力量)。
class_name ShengyuanMechanic
extends BaseMechanic

var _revenge_stacks: int = 0


func on_battle_start() -> void:
	_revenge_stacks = 0


## 每损失5HP获得1层复仇
func on_damage_taken(_target: Node, _source: Node, amount: int) -> void:
	_revenge_stacks += floori(float(amount) / 5.0)


## 亡者意志: HP<50% +1精神力; HP<25% +2精神力
func on_turn_start(_round_num: int) -> void:
	if not _resource_mgr:
		return
	var hp: int = _resource_mgr.get_player_hp()
	var max_hp: int = _resource_mgr.get_player_max_hp()
	if max_hp <= 0:
		return
	var ratio: float = float(hp) / float(max_hp)
	if ratio < 0.25:
		_resource_mgr.modify_player_energy(2)
	elif ratio < 0.5:
		_resource_mgr.modify_player_energy(1)


## 每层复仇+2伤害
func get_extra_damage(_target: Node) -> int:
	return _revenge_stacks * 2


## 攻击牌打出后复仇清零
func on_card_played(card: CardData, _target: Node) -> void:
	if card.card_type == CardData.CardType.ATTACK:
		_revenge_stacks = 0


## 血祭HP消耗量
func get_blood_cost(card: CardData) -> int:
	for effect in card.effects:
		if effect.cost_hp > 0:
			return effect.cost_hp
	return 0
