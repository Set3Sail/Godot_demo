# scripts/data/relic_data.gd
## 遗物数据定义。
class_name RelicData
extends Resource

enum RelicRarity { STARTER, COMMON, UNCOMMON, RARE, BOSS, CHARACTER_SPECIFIC, EVENT_EXCLUSIVE }

@export var relic_id: String = ""                      # "night_vision_goggles"
@export var display_name: String = ""
@export var rarity: RelicRarity = RelicRarity.COMMON
@export var character: String = ""                     # 角色专属时填写
@export var trigger_timing: String = ""                # 触发时机标识
@export var trigger_condition: String = ""             # 条件表达式
@export var effects: Array[EffectData] = []            # 触发时执行的效果
@export var max_charges: int = -1                      # 最大充能, -1=无充能制
@export var charges_per_trigger: int = 0               # 每次触发消耗
@export var cost_description: String = ""              # Boss遗物代价描述
@export var description: String = ""
@export var icon_path: String = ""

# 运行时状态
var current_charges: int = 0


## 初始化充能
func init_charges() -> void:
    current_charges = max_charges


## 检查是否有足够充能触发
func can_trigger() -> bool:
    if max_charges == -1:
        return true
    return current_charges >= charges_per_trigger


## 消耗充能
func consume_charge() -> void:
    if max_charges > 0:
        current_charges = maxi(0, current_charges - charges_per_trigger)
