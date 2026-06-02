# scripts/data/effect_data.gd
## 卡牌/遗物的效果定义资源。一组 EffectData 数组构成一张卡牌的全部效果。
##
## [param type] 效果类型: DAMAGE / BLOCK / DRAW / GAIN_ENERGY / BUFF / DEBUFF /
##              HEAL / MODIFY_STAT / REMOVE_STATUS / SPECIAL
## [param target] 目标选择: SELF / SINGLE_ENEMY / ALL_ENEMIES / RANDOM_ENEMY /
##                 ALL_ALLIES / FRONTMOST_ENEMY
## [param base_value] 基础数值（伤害/格挡/治疗量）
## [param scale_stat] 受哪个属性加成: "strength" / "dexterity" / "none"
## [param repeat_count] 执行次数, 默认 1
## [param condition] 可选条件表达式, 如 "target_has_mark"
## [param status_id] 施加的状态 id（BUFF/DEBUFF 类型时填写）
## [param status_stacks] 状态施加层数
## [param status_duration] 状态持续回合数, -1 表示永久/本场
## [param cost_hp] 血祭消耗 HP（盛元专用）, 默认 0
class_name EffectData
extends Resource

enum EffectType {
	DAMAGE, BLOCK, DRAW, GAIN_ENERGY,
	BUFF, DEBUFF, HEAL,
	MODIFY_STAT, REMOVE_STATUS, SPECIAL
}

enum EffectTarget {
	SELF, SINGLE_ENEMY, ALL_ENEMIES,
	RANDOM_ENEMY, ALL_ALLIES, FRONTMOST_ENEMY
}

@export var type: EffectType = EffectType.DAMAGE
@export var target: EffectTarget = EffectTarget.SINGLE_ENEMY
@export var base_value: int = 0
@export var scale_stat: String = "none"  # "strength" / "dexterity" / "none"
@export var repeat_count: int = 1
@export var condition: String = ""
@export var status_id: String = ""
@export var status_stacks: int = 0
@export var status_duration: int = -1
@export var cost_hp: int = 0


## 返回此效果的人类可读描述
func get_description() -> String:
	var desc: String = ""
	match type:
		EffectType.DAMAGE:
			desc = "造成 %d 点伤害" % base_value
		EffectType.BLOCK:
			desc = "获得 %d 点格挡" % base_value
		EffectType.DRAW:
			desc = "抽 %d 张牌" % base_value
		EffectType.GAIN_ENERGY:
			desc = "获得 %d 点精神力" % base_value
		EffectType.BUFF:
			desc = "获得 %d 层 %s" % [status_stacks, status_id]
		EffectType.DEBUFF:
			desc = "施加 %d 层 %s" % [status_stacks, status_id]
		EffectType.HEAL:
			desc = "回复 %d 点 HP" % base_value
		EffectType.MODIFY_STAT:
			desc = "修改属性: %s %+d" % [status_id, base_value]
		EffectType.REMOVE_STATUS:
			desc = "移除状态: %s" % status_id
		EffectType.SPECIAL:
			desc = "特殊效果"
	if repeat_count > 1:
		desc += " ×%d" % repeat_count
	if not condition.is_empty():
		desc += " [条件: %s]" % condition
	return desc
