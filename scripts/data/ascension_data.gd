# scripts/data/ascension_data.gd
## Ascension 挑战难度配置数据。
class_name AscensionData
extends Resource

@export var level: int = 0
@export var extra_elites: int = 0
@export var enemy_damage_bonus: int = 0
@export var enemy_hp_mult: float = 1.0
@export var wheel_cost_increase: int = 0
@export var camp_heal_pct: float = 0.30
@export var elite_extra_skills: bool = false
@export var initial_hp_penalty: int = 0
@export var boss_hp_mult: float = 1.0
@export var burning_nodes: bool = false
@export var boss_extra_skills: bool = false
@export var no_uncommon_plus_drops: bool = false
@export var dual_boss_chance: float = 0.0
@export var description: String = ""
