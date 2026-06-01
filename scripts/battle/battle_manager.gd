# scripts/battle/battle_manager.gd
## 顶层战斗协调器。初始化所有子管理器, 连接回合状态机信号,
## 协调整个战斗流程。
class_name BattleManager
extends Node

@export var hand_size: int = 5
@export var energy_per_turn: int = 3

@onready var _turn_sm: TurnStateMachine = $TurnStateMachine
@onready var _card_mgr: CardManager = $CardManager
@onready var _resource_mgr: ResourceManager = $ResourceManager
@onready var _status_mgr: StatusManager = $StatusManager
@onready var _effect_resolver: EffectResolver = $EffectResolver
@onready var _enemy_mgr: EnemyManager = $EnemyManager
@onready var _relic_mgr: Node = $RelicManager

var _player_deck: Array[CardData] = []
var _enemy_configs: Array[EnemyData] = []
var _battle_reward: Dictionary = {}
var _battle_ended: bool = false


func _ready() -> void:
	_setup_dependencies()
	_connect_signals()
	_turn_sm.configure(hand_size, energy_per_turn)


## 启动战斗（由局外 MapLevel 调用）
func start_battle(player_hp: int, player_max_hp: int, deck: Array[CardData], enemies: Array[EnemyData]) -> void:
	_player_deck = deck
	_enemy_configs = enemies
	_resource_mgr.init_player(player_hp, player_max_hp, energy_per_turn)
	_card_mgr.init_deck(deck)
	_spawn_enemies(enemies)
	_turn_sm.start_battle()


## 打出卡牌（由 UI 层调用）
func play_card(card: CardData, target: Node) -> void:
	var effective_cost: int = card.get_effective_cost()
	if _resource_mgr.get_player_energy() < effective_cost:
		return  # 精神力不足

	for effect in card.effects:
		if effect.cost_hp > 0:
			_resource_mgr.modify_player_hp(-effect.cost_hp, "normal")

	_resource_mgr.modify_player_energy(-effective_cost)
	_effect_resolver.resolve_effects_on_target(card.effects, target, self, true)
	_card_mgr.play_card(card, target)


func _setup_dependencies() -> void:
	_effect_resolver.setup(_resource_mgr, _card_mgr, _status_mgr, _enemy_mgr, _relic_mgr)


func _connect_signals() -> void:
	_turn_sm.state_changed.connect(_on_state_changed)
	_resource_mgr.player_died.connect(_on_player_died)
	_resource_mgr.entity_died.connect(_on_enemy_died)


func _spawn_enemies(configs: Array[EnemyData]) -> void:
	for data in configs:
		_enemy_mgr.spawn_enemy(data)


# ——— 状态机回调 ———

func _on_state_changed(from_state: int, to_state: int) -> void:
	match to_state:
		TurnStateMachine.BattleState.BATTLE_START:
			_on_battle_start()
		TurnStateMachine.BattleState.PLAYER_TURN_START:
			_on_player_turn_start()
		TurnStateMachine.BattleState.PLAYER_TURN_END:
			_on_player_turn_end()
		TurnStateMachine.BattleState.ENEMY_TURN:
			_on_enemy_turn()
		TurnStateMachine.BattleState.ROUND_END:
			_on_round_end()


func _on_battle_start() -> void:
	_card_mgr.draw_cards(hand_size)
	_turn_sm._go_to_player_turn()


func _on_player_turn_start() -> void:
	_resource_mgr.on_turn_start()
	_card_mgr.draw_to_hand_size(hand_size)


func _on_player_turn_end() -> void:
	_card_mgr.discard_hand()
	_resource_mgr.on_turn_end()
	_status_mgr.tick_statuses(_get_player_node())
	# Tick enemy statuses too
	for enemy in _enemy_mgr.get_alive_enemies():
		_status_mgr.tick_statuses(enemy)
	_turn_sm._go_to_enemy_turn()


func _on_enemy_turn() -> void:
	_enemy_mgr.execute_all_enemy_intents()
	_enemy_mgr.ally_auto_attack_all()
	_turn_sm._go_to_round_end()


func _on_round_end() -> void:
	var alive_enemies: Array = _enemy_mgr.get_alive_enemies()
	if alive_enemies.is_empty():
		_on_battle_victory()
	elif _resource_mgr.get_player_hp() <= 0:
		_on_player_died()
	else:
		_turn_sm._go_to_player_turn()


func _on_battle_victory() -> void:
	if _battle_ended and _turn_sm.current_state == TurnStateMachine.BattleState.BATTLE_WIN:
		return
	var total_crystals: int = 0
	for enemy in _enemy_mgr._enemies:
		total_crystals += _enemy_mgr.get_crystal_drop(enemy)
	_resource_mgr.add_crystals(total_crystals)
	_turn_sm.trigger_victory()


func _on_player_died() -> void:
	_turn_sm.trigger_defeat()


func _on_enemy_died(entity: Node, killer: Node) -> void:
	var crystals: int = _enemy_mgr.get_crystal_drop(entity)
	_resource_mgr.add_crystals(crystals)
	_enemy_mgr.remove_enemy(entity)
	call_deferred("_check_all_enemies_dead")


func _check_all_enemies_dead() -> void:
	if _battle_ended:
		return
	if _enemy_mgr.get_alive_enemies().is_empty():
		_battle_ended = true
		_on_battle_victory()


func _get_player_node() -> Node:
	return get_tree().get_first_node_in_group("player")
