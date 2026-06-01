# scripts/autoload/save_manager.gd
## 存档管理器（Autoload）: 章节存档、死亡重试、数据持久化。
extends Node

const SAVE_DIR: String = "user://saves/"
const MAX_SAVES_PER_CHARACTER: int = 3

# 当前运行状态
var current_character: String = ""
var current_chapter: int = 1
var current_deck: Array[CardData] = []
var current_relics: Array[RelicData] = []
var current_hp: int = 0
var current_max_hp: int = 0
var current_crystals: int = 0

# 章节开始快照（用于死亡重试）
var _chapter_snapshot: Dictionary = {}

signal game_saved(slot: int)
signal game_loaded(slot: int)

func _ready() -> void:
	DirAccess.make_dir_absolute(SAVE_DIR)

func create_chapter_snapshot() -> void:
	_chapter_snapshot = {
		"character": current_character,
		"chapter": current_chapter,
		"deck": current_deck.duplicate(),
		"relics": current_relics.duplicate(),
		"hp": current_hp,
		"max_hp": current_max_hp,
		"crystals": current_crystals,
	}

func restore_chapter_snapshot() -> void:
	if _chapter_snapshot.is_empty():
		return
	current_character = _chapter_snapshot["character"]
	current_chapter = _chapter_snapshot["chapter"]
	current_deck = _chapter_snapshot["deck"]
	current_relics = _chapter_snapshot["relics"]
	current_hp = _chapter_snapshot["hp"]
	current_max_hp = _chapter_snapshot["max_hp"]
	current_crystals = _chapter_snapshot["crystals"]

func save_game(slot: int) -> void:
	var save_path: String = SAVE_DIR + "%s_slot%d.sav" % [current_character, slot]
	var data: Dictionary = {
		"character": current_character,
		"chapter": current_chapter,
		"deck_card_ids": _serialize_deck(),
		"relic_ids": _serialize_relics(),
		"hp": current_hp,
		"max_hp": current_max_hp,
	}
	var file: FileAccess = FileAccess.open(save_path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()
	game_saved.emit(slot)

func load_game(slot: int) -> Dictionary:
	var save_path: String = SAVE_DIR + "%s_slot%d.sav" % [current_character, slot]
	if not FileAccess.file_exists(save_path):
		return {}
	var file: FileAccess = FileAccess.open(save_path, FileAccess.READ)
	var json_str: String = file.get_as_text()
	file.close()
	var data: Dictionary = JSON.parse_string(json_str)
	game_loaded.emit(slot)
	return data

func _serialize_deck() -> Array[String]:
	var ids: Array[String] = []
	for card in current_deck:
		ids.append(card.card_id)
	return ids

func _serialize_relics() -> Array[String]:
	var ids: Array[String] = []
	for relic in current_relics:
		ids.append(relic.relic_id)
	return ids
