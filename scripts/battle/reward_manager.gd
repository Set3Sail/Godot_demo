# scripts/battle/reward_manager.gd
## 战斗奖励管理器: 卡牌选择/遗物掉落/魔晶结算。
class_name RewardManager
extends RefCounted

var _rng: RandomNumberGenerator = RandomNumberGenerator.new()

# 稀有度权重表 (白/绿/蓝/紫/橙)
const NORMAL_FIGHT_WEIGHTS: Array[float] = [60.0, 25.0, 10.0, 4.0, 1.0]
const ELITE_FIGHT_WEIGHTS: Array[float] = [0.0, 50.0, 35.0, 12.0, 3.0]
const BOSS_FIGHT_WEIGHTS: Array[float] = [0.0, 0.0, 67.0, 33.0, 0.0]

# 精英遗物掉落率
const ELITE_RELIC_DROP_CHANCE: float = 0.6
# 遗物稀有度权重
const RELIC_RARITY_WEIGHTS: Array[float] = [60.0, 25.0, 10.0, 0.0, 5.0]


## 生成普通战斗奖励
func generate_normal_reward(character: String, chapter: int) -> BattleRewardData:
	var reward: BattleRewardData = BattleRewardData.new()
	reward.card_choices = _pick_random_cards(3, NORMAL_FIGHT_WEIGHTS, character)
	reward.can_skip_card = true
	reward.relic_drops = []
	return reward


## 生成精英战斗奖励
func generate_elite_reward(character: String, chapter: int) -> BattleRewardData:
	var reward: BattleRewardData = BattleRewardData.new()
	reward.card_choices = _pick_random_cards(3, ELITE_FIGHT_WEIGHTS, character)
	reward.can_skip_card = true

	if _rng.randf() < ELITE_RELIC_DROP_CHANCE:
		var relic: RelicData = _pick_random_relic(null)
		if relic:
			reward.relic_drops.append(relic)

	return reward


## 生成Boss战斗奖励
func generate_boss_reward(character: String, chapter: int) -> BattleRewardData:
	var reward: BattleRewardData = BattleRewardData.new()
	reward.card_choices = _pick_random_cards(3, BOSS_FIGHT_WEIGHTS, character)
	reward.can_skip_card = false
	reward.is_boss_reward = true
	return reward


## 选卡: 按角色和稀有度权重随机
func _pick_random_cards(count: int, weights: Array[float], character: String) -> Array[CardData]:
	var available: Array[CardData] = _get_available_cards(character)
	if available.is_empty():
		return []

	var chosen: Array[CardData] = []
	var pool: Array[CardData] = available.duplicate()

	for i in range(count):
		if pool.is_empty():
			break
		# 按权重选择稀有度
		var rarity: int = _weighted_random_rarity(weights)
		# 从池中筛选对应稀有度的卡牌
		var filtered: Array[CardData] = _filter_by_rarity(pool, rarity)
		if filtered.is_empty():
			filtered = pool  # 回退到全池
		var card: CardData = filtered[_rng.randi_range(0, filtered.size() - 1)]
		chosen.append(card)
		pool.erase(card)  # 不重复

	return chosen


## 按稀有度权重随机选取遗物
func _pick_random_relic(character: String = "") -> RelicData:
	# 加载所有遗物 .tres
	var all_relics: Array[RelicData] = _load_available_relics(character)
	if all_relics.is_empty():
		return null

	var rarity: int = _weighted_random_rarity(RELIC_RARITY_WEIGHTS)
	var filtered: Array[RelicData] = []
	for relic in all_relics:
		if relic.rarity == rarity:
			filtered.append(relic)
	if filtered.is_empty():
		return all_relics[_rng.randi_range(0, all_relics.size() - 1)]

	return filtered[_rng.randi_range(0, filtered.size() - 1)]


func _weighted_random_rarity(weights: Array[float]) -> int:
	var total: float = 0.0
	for w in weights:
		total += w
	var roll: float = _rng.randf() * total
	var cumulative: float = 0.0
	for i in range(weights.size()):
		cumulative += weights[i]
		if roll <= cumulative:
			return i
	return 0  # COMMON


func _filter_by_rarity(pool: Array[CardData], rarity: int) -> Array[CardData]:
	var result: Array[CardData] = []
	for card in pool:
		if card.rarity == rarity:
			result.append(card)
	return result


func _get_available_cards(character: String) -> Array[CardData]:
	# 加载该角色所有卡牌 .tres
	var cards: Array[CardData] = []
	var dir_path: String = "res://resources/cards/%s/" % _character_to_dir(character)
	var dir: DirAccess = DirAccess.open(dir_path)
	if dir:
		dir.list_dir_begin()
		var file_name: String = dir.get_next()
		while not file_name.is_empty():
			if file_name.ends_with(".tres") and not dir.current_is_dir():
				var card: CardData = load(dir_path + file_name) as CardData
				if card:
					cards.append(card)
			file_name = dir.get_next()
		dir.list_dir_end()
	return cards


func _load_available_relics(character: String = "") -> Array[RelicData]:
	var relics: Array[RelicData] = []
	var dirs: Array[String] = [
		"res://resources/relics/common/",
		"res://resources/relics/uncommon/",
		"res://resources/relics/rare/",
		"res://resources/relics/character/",
	]
	for dir_path in dirs:
		var dir: DirAccess = DirAccess.open(dir_path)
		if not dir:
			continue
		dir.list_dir_begin()
		var file_name: String = dir.get_next()
		while not file_name.is_empty():
			if file_name.ends_with(".tres") and not dir.current_is_dir():
				var relic: RelicData = load(dir_path + file_name) as RelicData
				if relic:
					# 过滤角色专属遗物
					if relic.character.is_empty() or relic.character == character:
						relics.append(relic)
			file_name = dir.get_next()
		dir.list_dir_end()
	return relics


func _character_to_dir(character: String) -> String:
	match character:
		"叶默": return "yemo"
		"墨夜": return "moye"
		"温静": return "wenjing"
		"盛元": return "shengyuan"
		"金英": return "jinying"
		"红发": return "hongfa"
		"莉莲": return "lilian"
	return "yemo"
