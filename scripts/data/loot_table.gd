# scripts/data/loot_table.gd
## 掉落表配置。定义每个章节的卡牌稀有度权重偏移。
class_name LootTable
extends Resource

@export var chapter: int = 1
@export var common_weight: float = 60.0
@export var uncommon_weight: float = 25.0
@export var rare_weight: float = 10.0
@export var epic_weight: float = 4.0
@export var legendary_weight: float = 1.0
@export var elite_relic_chance: float = 0.6
@export var boss_relic_count: int = 1


## 获取该章节的战斗选卡权重
func get_fight_weights() -> Array[float]:
	return [common_weight, uncommon_weight, rare_weight, epic_weight, legendary_weight]


## 获取精英选卡权重（优秀保底）
func get_elite_weights() -> Array[float]:
	return [0.0, 50.0, 35.0, 12.0, 3.0]
