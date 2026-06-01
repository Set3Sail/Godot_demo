# scripts/autoload/game_progress.gd
## 局外进度管理（Autoload）: 角色进化等阶、成就、章节解锁、Ascension。
extends Node

const MAX_ASCENSION: int = 20

# 角色经验: {character_name: int}
var character_exp: Dictionary = {}
# 角色等阶: {character_name: int}  (0=普通人, 1-10=一星~十星)
var character_ranks: Dictionary = {}
# 已解锁角色
var unlocked_characters: Array[String] = ["叶默", "墨夜", "温静"]
# 已解锁章节
var unlocked_chapters: int = 1
# 已解锁成就
var unlocked_achievements: Array[String] = []
# Ascension等级
var ascension_level: int = 0
# 已解锁卡牌
var unlocked_cards: Array[String] = []
# 已解锁遗物
var unlocked_relics: Array[String] = []

# 等阶经验表
const RANK_EXP: Array[int] = [0, 100, 250, 500, 800, 1200, 1600, 2000, 2500, 3000, 5000]
# 等阶名称
const RANK_NAMES: Array[String] = ["普通人", "一星", "二星", "三星", "四星", "五星", "六星", "七星", "八星", "九星", "十星"]

signal character_ranked_up(character: String, new_rank: int)
signal achievement_unlocked(achievement_id: String)
signal character_unlocked(character: String)
signal chapter_unlocked(chapter: int)

func _ready() -> void:
	for character in unlocked_characters:
		if not character in character_exp:
			character_exp[character] = 0
		if not character in character_ranks:
			character_ranks[character] = 0

func add_exp(character: String, amount: int) -> void:
	character_exp[character] = character_exp.get(character, 0) + amount
	_check_rank_up(character)

func get_rank(character: String) -> int:
	return character_ranks.get(character, 0)

func get_rank_name(character: String) -> String:
	var rank: int = get_rank(character)
	return RANK_NAMES[rank] if rank < RANK_NAMES.size() else "十星"

func unlock_character(character: String) -> void:
	if not character in unlocked_characters:
		unlocked_characters.append(character)
		character_exp[character] = 0
		character_ranks[character] = 0
		character_unlocked.emit(character)

func unlock_chapter(chapter: int) -> void:
	if chapter > unlocked_chapters:
		unlocked_chapters = chapter
		chapter_unlocked.emit(chapter)

func unlock_achievement(achievement_id: String) -> void:
	if not achievement_id in unlocked_achievements:
		unlocked_achievements.append(achievement_id)
		achievement_unlocked.emit(achievement_id)

func _check_rank_up(character: String) -> void:
	var exp: int = character_exp.get(character, 0)
	var current_rank: int = character_ranks.get(character, 0)
	for i in range(current_rank + 1, RANK_EXP.size()):
		if exp >= RANK_EXP[i]:
			character_ranks[character] = i
			character_ranked_up.emit(character, i)
		else:
			break
