# scripts/data/status_effect_data.gd
## 状态效果数据定义。定义 Buff/Debuff 的属性、叠层规则和回合结束效果。
class_name StatusEffectData
extends Resource

enum StackType { INTENSITY, DURATION_ONLY, COUNTER }
enum StatusCategory { BUFF, DEBUFF }

@export var status_id: String = ""                     # "strength_up" / "frost" / "vulnerable"
@export var display_name: String = ""                  # "力量+" / "冰霜"
@export var category: StatusCategory = StatusCategory.BUFF
@export var stack_type: StackType = StackType.INTENSITY
@export var max_stacks: int = -1                       # 最大层数, -1=无上限
@export var default_duration: int = -1                 # 默认持续回合, -1=永久
@export var icon_path: String = ""                     # UI 图标
@export var tick_effects: Array[EffectData] = []       # 回合结束触发的效果（中毒/灼烧）
@export var description: String = ""                   # 描述文本
@export var character_specific: String = ""            # 专属角色（通用留空）


## 计算剩余回合的影响
func should_remove_after_tick(current_duration: int) -> bool:
    return stack_type == StackType.DURATION_ONLY and current_duration <= 1
