# scripts/data/intent_data.gd
## 敌人意图数据。定义单个意图回合的行为。
class_name IntentData
extends Resource

enum IntentType { ATTACK, DEFEND, BUFF, DEBUFF, SUMMON, SPECIAL }

@export var type: IntentType = IntentType.ATTACK
@export var base_value: int = 0                        # 伤害/格挡基础值
@export var value_variance: float = 0.2                # 波动范围（±20%）
@export var secondary_value: int = 0                   # 第二数值（层数/召唤数量）
@export var status_id: String = ""                     # 施加的状态 id
@export var status_duration: int = 1                   # 状态持续回合
@export var target_count: int = 1                      # 目标数, 0=全体
@export var description: String = ""                   # 展示文本
@export var icon: String = ""                          # 意图图标
