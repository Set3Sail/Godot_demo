# scripts/autoload/event_bus.gd
## 全局事件总线（Autoload），用于跨层级通信。
## [br][br]
## 只在模块间确实无直接父子关系时使用。
## 本地通信优先使用场景内信号的直接连接。
extends Node

## 战斗生命周期
signal battle_started
signal battle_won
signal battle_lost

## 回合流程
signal player_turn_started(round_number: int)
signal player_turn_ended
signal enemy_turn_started
signal enemy_turn_ended
signal round_ended

## 卡牌事件
signal card_played(card_id: String, target: Node)
signal card_drawn(card_id: String)
signal card_discarded(card_id: String)
signal card_exhausted(card_id: String)
signal deck_shuffled

## 资源变化
signal hp_changed(entity: Node, current: int, max_hp: int, delta: int)
signal energy_changed(current: int)
signal block_changed(entity: Node, current: int)
signal entity_died(entity: Node, killer: Node)

## 游戏控制
signal end_turn_requested
