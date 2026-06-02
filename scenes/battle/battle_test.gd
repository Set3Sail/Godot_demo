# scenes/battle/battle_test.gd
extends Node

@onready var battle_mgr := $BattleManager
@onready var hand_ui: HandUI = $"PlayerArea/HandArea"


func _ready() -> void:
	# 等待一帧让所有 _ready 完成
	await get_tree().process_frame

	# —— 初始化 HandUI ——
	hand_ui.setup(battle_mgr._card_mgr)

	# —— 加载测试数据 ——
	var slash: CardData = load("res://resources/cards/slash.tres")
	var defend: CardData = load("res://resources/cards/defend.tres")
	var deck: Array[CardData] = [slash, slash, slash, slash, slash, defend, defend, defend, defend, defend, slash, defend]

	var zombie: EnemyData = load("res://resources/enemies/normal_zombie.tres")
	var enemies: Array[EnemyData] = [zombie]

	# —— 启动战斗 ——
	battle_mgr.start_battle(75, 75, deck, enemies)
	print("Battle started! Round: ", battle_mgr._turn_sm.round_number)

	# 等待回合开始
	await get_tree().create_timer(0.5).timeout

	# 验证手牌
	var hand_size: int = battle_mgr._card_mgr.get_hand_size()
	print("Hand size: ", hand_size, " (expected 5)")
