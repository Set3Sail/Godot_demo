# scripts/data/enemy_data.gd
## 敌人数据定义。
class_name EnemyData
extends Resource

enum EnemyType { NORMAL, ELITE, BOSS }

@export var enemy_id: String = ""
@export var display_name: String = ""
@export var base_hp: int = 40
@export var enemy_type: EnemyType = EnemyType.NORMAL
@export var phase_configs: Array[PhaseConfig] = []     # Boss 多阶段
@export var intent_pattern: Array[IntentData] = []     # 意图循环序列
@export var crystal_drop: int = 1                      # 魔晶掉落
@export var status_resistances: Dictionary = {}         # {"freeze": 0.5}
@export var special_rules: Array[String] = []          # 特殊规则 id
@export var sprite_path: String = ""
