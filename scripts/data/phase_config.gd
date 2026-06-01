# scripts/data/phase_config.gd
## Boss 多阶段配置。
class_name PhaseConfig
extends Resource

@export var hp_threshold: float = 1.0                  # 触发 HP 百分比 (0.0-1.0)
@export var sprite_path: String = ""                   # 阶段美术资源
@export var new_intent_pattern: Array[IntentData] = []  # 新意图循环
@export var phase_animation: String = ""               # 切换动画名
@export var clear_statuses: Array[String] = []         # 进阶段时清除的状态 id
