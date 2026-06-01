# scripts/data/battle_reward_data.gd
## 战斗奖励数据结构。
class_name BattleRewardData
extends RefCounted

var crystals: int = 0
var card_choices: Array[CardData] = []
var can_skip_card: bool = true
var relic_drops: Array[RelicData] = []
var is_boss_reward: bool = false
var boss_relic_options: Array[RelicData] = []
var hp_restore: int = 0
