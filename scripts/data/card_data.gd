# scripts/data/card_data.gd
## 卡牌数据资源。每张卡牌在 Godot 中是一个 .tres 文件。
## 战斗中通过 CardManager 复制实例来追踪状态。
class_name CardData
extends Resource

enum CardType { ATTACK, SKILL, ABILITY, EQUIPMENT }
enum CardRarity { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }

@export var card_id: String = ""                       # 唯一标识 "yemo_forge_strike"
@export var card_name: String = ""                     # 显示名 "锻造打击"
@export var character: String = "通用"                  # 所属角色
@export var card_type: CardType = CardType.ATTACK
@export var rarity: CardRarity = CardRarity.COMMON
@export var cost: int = 1                              # 精神力消耗 0-4
@export var effects: Array[EffectData] = []             # 效果列表
@export var keywords: Array[String] = []               # ["锻造", "荆棘"]
@export var is_upgraded: bool = false                   # 是否已营地升级
@export var is_forged: bool = false                     # 锻造（叶默临时）
@export var forge_count: int = 0                        # 锻造次数
@export var upgrade_version: String = ""               # 营地升级目标卡牌 id
@export var exhaust_on_use: bool = false               # 是否消耗（能力卡/装备卡自动 true）
@export var description: String = ""                   # 展示文本
@export var art_path: String = ""                      # 卡面资源路径

# 战斗运行时状态（非 @export，不序列化到 .tres）
var _forge_max: int = 1                                # 本场最大锻造次数
var _temporary_modifiers: Dictionary = {}              # 临时数值修正


## 创建此卡牌的独立运行时副本
func create_runtime_copy() -> CardData:
    var copy := CardData.new()
    copy.card_id = card_id
    copy.card_name = card_name
    copy.character = character
    copy.card_type = card_type
    copy.rarity = rarity
    copy.cost = cost
    copy.effects = effects  # EffectData 是 Resource, 共享引用
    copy.keywords = keywords.duplicate()
    copy.is_upgraded = is_upgraded
    copy.is_forged = is_forged
    copy.forge_count = forge_count
    copy.upgrade_version = upgrade_version
    copy.exhaust_on_use = exhaust_on_use or card_type in [CardType.ABILITY, CardType.EQUIPMENT]
    copy.description = description
    copy.art_path = art_path
    copy._forge_max = _forge_max
    copy._temporary_modifiers = _temporary_modifiers.duplicate()
    return copy


## 获取当前有效费用（考虑遗物/能力修正）
func get_effective_cost() -> int:
    var c: int = cost + _temporary_modifiers.get("cost_modifier", 0)
    return clampi(c, 0, 99)


## 检查是否拥有指定关键词
func has_keyword(kw: String) -> bool:
    return kw in keywords


## 是否为消耗卡
func is_exhaust_card() -> bool:
    return exhaust_on_use
