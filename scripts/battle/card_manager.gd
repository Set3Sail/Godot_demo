# scripts/battle/card_manager.gd
## 卡牌管理器: 四大牌堆管理 + 抽牌/弃牌/消耗 + 洗牌 + 锻造。
class_name CardManager
extends Node

var draw_pile: Array[CardData] = []        # 抽牌堆（顶部=下一个抽到）
var hand: Array[CardData] = []             # 手牌
var discard_pile: Array[CardData] = []     # 弃牌堆
var exhaust_pile: Array[CardData] = []     # 消耗堆
var _deck_initialized: bool = false

signal card_drawn(card: CardData, count: int)
signal card_played(card: CardData, target: Node)
signal card_discarded(card: CardData)
signal card_exhausted(card: CardData)
signal deck_shuffled
signal deck_cycle
signal hand_empty
signal card_upgraded(card: CardData, source: String)


## 用初始牌组初始化
func init_deck(deck_list: Array[CardData]) -> void:
	draw_pile.clear()
	hand.clear()
	discard_pile.clear()
	exhaust_pile.clear()
	for card in deck_list:
		draw_pile.append(card.create_runtime_copy())
	shuffle_deck()
	_deck_initialized = true


## 抽卡（含自动洗牌）
func draw_cards(count: int) -> Array[CardData]:
	var drawn: Array[CardData] = []
	var remaining: int = count
	while remaining > 0:
		if draw_pile.is_empty():
			if discard_pile.is_empty():
				break
			_cycle_discard_to_draw()
		var card: CardData = draw_pile.pop_back()
		hand.append(card)
		drawn.append(card)
		remaining -= 1
	card_drawn.emit(drawn[-1] if not drawn.is_empty() else null, drawn.size())
	return drawn


## 抽满到手牌数达到 hand_size（通常 5 张）
func draw_to_hand_size(hand_size: int) -> Array[CardData]:
	var missing: int = hand_size - hand.size()
	if missing <= 0:
		return []
	return draw_cards(missing)


## 从手牌打出卡牌（费用和有效性由 BattleManager 外层校验）
func play_card(card: CardData, target: Node) -> void:
	var idx: int = hand.find(card)
	if idx == -1:
		push_error("CardManager.play_card: card not in hand")
		return
	hand.remove_at(idx)

	if card.is_exhaust_card():
		exhaust_pile.append(card)
		card_exhausted.emit(card)
	else:
		discard_pile.append(card)
		card_discarded.emit(card)

	if hand.is_empty():
		hand_empty.emit()


## 弃所有手牌
func discard_hand() -> void:
	for card in hand:
		discard_pile.append(card)
	hand.clear()


## 指定弃牌
func discard_card(card: CardData) -> void:
	var idx: int = hand.find(card)
	if idx == -1:
		return
	hand.remove_at(idx)
	discard_pile.append(card)
	card_discarded.emit(card)


## 消耗牌
func exhaust_card(card: CardData) -> void:
	var idx: int = hand.find(card)
	if idx == -1:
		return
	hand.remove_at(idx)
	exhaust_pile.append(card)
	card_exhausted.emit(card)


## 战斗中新增卡牌（入弃牌堆）
func add_card_to_deck(card: CardData) -> void:
	discard_pile.append(card.create_runtime_copy())


## 直接入手牌
func add_card_to_hand(card: CardData) -> void:
	hand.append(card)


## 从战斗中完全移除
func remove_card_from_battle(card: CardData) -> void:
	var idx: int = hand.find(card)
	if idx != -1:
		hand.remove_at(idx)


## 锻造（叶默: 升级手牌中卡牌）
func forge_card_in_hand(card: CardData) -> void:
	if card.forge_count >= card._forge_max:
		return
	var idx: int = hand.find(card)
	if idx == -1:
		return
	var forged: CardData = card.create_runtime_copy()
	forged.is_forged = true
	forged.forge_count += 1
	for effect in forged.effects:
		match effect.type:
			EffectData.EffectType.DAMAGE, EffectData.EffectType.BLOCK:
				effect.base_value = int(ceilf(effect.base_value * 1.3))
	hand[idx] = forged
	card_upgraded.emit(forged, "forge")


## 洗牌
func shuffle_deck() -> void:
	draw_pile.shuffle()
	deck_shuffled.emit()


## 获取各牌堆信息
func get_draw_count() -> int:  return draw_pile.size()
func get_hand_size() -> int:  return hand.size()
func get_discard_count() -> int:  return discard_pile.size()
func get_exhaust_count() -> int:  return exhaust_pile.size()
func get_total_count() -> int:  return draw_pile.size() + hand.size() + discard_pile.size()


# ——— 内部 ———

func _cycle_discard_to_draw() -> void:
	draw_pile = discard_pile.duplicate()
	discard_pile.clear()
	shuffle_deck()
	deck_cycle.emit()
