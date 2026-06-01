# scripts/battle/turn_state_machine.gd
## 回合状态机: 管理 7 个状态流转。
##
## BATTLE_START → PLAYER_TURN_START → PLAYER_PLAY → PLAYER_TURN_END
## → ENEMY_TURN → ROUND_END → (loop) → BATTLE_WIN / BATTLE_LOSE
class_name TurnStateMachine
extends Node

enum BattleState {
	BATTLE_START,
	PLAYER_TURN_START,
	PLAYER_PLAY,
	PLAYER_TURN_END,
	ENEMY_TURN,
	ROUND_END,
	BATTLE_WIN,
	BATTLE_LOSE
}

var current_state: BattleState = BattleState.BATTLE_START
var round_number: int = 0
var _hand_size: int = 5                            # 每回合手牌上限
var _energy_per_turn: int = 3                      # 每回合精神力

signal state_changed(from_state: BattleState, to_state: BattleState)
signal player_turn_started(round_num: int)
signal player_turn_ended
signal enemy_turn_started
signal enemy_turn_ended
signal round_ended
signal battle_won
signal battle_lost


## 设置战斗参数
func configure(hand_size: int = 5, energy_per_turn: int = 3) -> void:
	_hand_size = hand_size
	_energy_per_turn = energy_per_turn


## 开始战斗
func start_battle() -> void:
	_transition_to(BattleState.BATTLE_START)


## 玩家请求结束回合
func request_end_turn() -> void:
	if current_state == BattleState.PLAYER_PLAY:
		_transition_to(BattleState.PLAYER_TURN_END)


## 获取手牌上限
func get_hand_size() -> int:  return _hand_size
func get_energy_per_turn() -> int:  return _energy_per_turn


func _transition_to(new_state: BattleState) -> void:
	var old_state: BattleState = current_state
	current_state = new_state
	state_changed.emit(old_state, new_state)

	match new_state:
		BattleState.BATTLE_START:
			pass
		BattleState.PLAYER_TURN_START:
			round_number += 1
			player_turn_started.emit(round_number)
		BattleState.PLAYER_PLAY:
			pass
		BattleState.PLAYER_TURN_END:
			player_turn_ended.emit()
		BattleState.ENEMY_TURN:
			enemy_turn_started.emit()
		BattleState.ROUND_END:
			round_ended.emit()
		BattleState.BATTLE_WIN:
			battle_won.emit()
		BattleState.BATTLE_LOSE:
			battle_lost.emit()


## 进入玩家回合
func _go_to_player_turn() -> void:
	_transition_to(BattleState.PLAYER_TURN_START)
	_transition_to(BattleState.PLAYER_PLAY)


## 结束玩家回合
func _go_to_player_turn_end() -> void:
	_transition_to(BattleState.PLAYER_TURN_END)


## 进入敌人回合
func _go_to_enemy_turn() -> void:
	_transition_to(BattleState.ENEMY_TURN)


## 回合结束
func _go_to_round_end() -> void:
	_transition_to(BattleState.ROUND_END)
	_go_to_player_turn()


## 胜利/失败
func trigger_victory() -> void:
	_transition_to(BattleState.BATTLE_WIN)

func trigger_defeat() -> void:
	_transition_to(BattleState.BATTLE_LOSE)
