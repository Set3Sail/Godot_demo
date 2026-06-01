# scripts/data/event_choice.gd
## 命运事件选项数据。
class_name EventChoice
extends Resource

enum ChoiceResult { GAIN_CARD, GAIN_RELIC, GAIN_CRYSTALS, REMOVE_CARD,
    UPGRADE_CARD, HEAL, DAMAGE, RANDOM_COMBAT, GAIN_EQUIPMENT,
    UPGRADE_RANDOM, REMOVE_CURSE, NOTHING }

@export var choice_text: String = ""       # 选项描述
@export var result_type: ChoiceResult = ChoiceResult.NOTHING
@export var result_value: int = 0          # 数值（HP变动/魔晶/升级数量）
@export var result_value2: int = 0         # 第二数值
@export var success_chance: float = 1.0    # 成功率（1.0=必然，0.5=50%）
@export var fail_result_type: ChoiceResult = ChoiceResult.NOTHING
@export var fail_result_value: int = 0
@export var result_description: String = "" # 结果描述
