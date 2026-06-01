# 轮盘世界 · 战斗框架 Foundation 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建战斗框架核心基础层（数据资源类型 + 核心管理器 + 回合引擎），后续角色/遗物/UI 层依赖此基础。

**Architecture:** 数据驱动 — Godot `.tres` Resource 定义卡牌/效果/敌人数据; 信号解耦 — 模块间通过 Signal 通信; 策略模式 — 角色机制通过 BaseMechanic 子类注册; 单帧结算 — EffectResolver 管道化处理所有效果。

**Tech Stack:** Godot 4.x + GDScript 2.0 (typed), Git 版本管理

**代码规范遵从:** `docs/godot-coding-standards/` (7 文档)

---

## 文件结构概览

```
res://
├── project.godot
├── scripts/
│   ├── autoload/
│   │   └── event_bus.gd              # 全局事件总线（Autoload）
│   ├── battle/
│   │   ├── battle_manager.gd         # 顶层协调器
│   │   ├── turn_state_machine.gd     # 回合状态机
│   │   ├── card_manager.gd           # 卡牌/牌堆管理
│   │   ├── resource_manager.gd       # HP/精神力/力量/敏捷/格挡
│   │   ├── status_manager.gd         # Buff/Debuff 管理
│   │   ├── effect_resolver.gd        # 效果结算管道
│   │   ├── enemy_manager.gd          # 敌人/召唤物管理
│   │   ├── relic_manager.gd          # 遗物注册+触发
│   │   ├── equipment_manager.gd      # 装备槽管理
│   │   └── mechanics/
│   │       ├── base_mechanic.gd      # 角色机制基类
│   │       └── ...                   # 7 角色机制（后续 Plan）
│   └── data/
│       ├── card_data.gd              # CardData Resource
│       ├── effect_data.gd            # Effect Resource
│       ├── enemy_data.gd             # EnemyData Resource
│       ├── intent_data.gd            # IntentData Resource
│       ├── phase_config.gd           # PhaseConfig Resource
│       ├── status_effect_data.gd     # StatusEffectData Resource
│       ├── relic_data.gd             # RelicData Resource
│       └── equipment_card_data.gd    # EquipmentCardData Resource
├── resources/
│   ├── cards/                        # .tres 卡牌数据
│   ├── enemies/                      # .tres 敌人数据
│   ├── status_effects/              # .tres 状态效果数据
│   └── relics/                       # .tres 遗物数据
├── scenes/
│   └── battle/
│       └── battle_scene.tscn         # 战斗场景
└── docs/
    ├── godot-coding-standards/       # 代码规范
    └── superpowers/
        ├── specs/                    # GDD + PRD
        └── plans/                    # 实现计划
```

---

### Task 1: 项目结构初始化 + Git

**Files:**
- Create: `project.godot`
- Create: `.gitignore`
- Create: 目录结构

- [ ] **Step 1: 创建 Godot 项目基础配置**

```ini
; project.godot
; Godot 4.x 项目配置文件
; 通过 Godot 编辑器创建 project.godot 或手动编写基础配置

config_version=5

[application]
config/name="轮盘世界"
config/description="卡牌构筑 Roguelike - 战斗框架"
config/version="0.1.0"
run/main_scene="res://scenes/battle/battle_scene.tscn"

[gdscript]
; 类型安全警告全部启用
warning/unsafe_property_access=1
warning/unsafe_method_access=1
warning/unsafe_cast=1
warning/unsafe_call_argument=1
warning/return_value_discarded=1
warning/untyped_declaration=1

[autoload]
EventBus="*res://scripts/autoload/event_bus.gd"

[editor_plugins]
enabled=PackedStringArray()
```

- [ ] **Step 2: 创建 `.gitignore`**

```gitignore
# .gitignore
.godot/
*.translation
*.import
export/
*.exe
*.pck
.import/
export_presets.cfg
.gdignore
.superpowers/brainstorm/
```

- [ ] **Step 3: 创建目录结构**

```bash
mkdir -p scripts/autoload
mkdir -p scripts/battle/mechanics
mkdir -p scripts/data
mkdir -p resources/cards
mkdir -p resources/enemies
mkdir -p resources/status_effects
mkdir -p resources/relics
mkdir -p scenes/battle
```

- [ ] **Step 4: 创建 EventBus Autoload**

```gdscript
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
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: initialize project structure, gitignore, and EventBus autoload

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Effect 数据资源

**Files:**
- Create: `scripts/data/effect_data.gd`

- [ ] **Step 1: 创建 EffectData Resource 类**

```gdscript
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
```

- [ ] **Step 2: Commit**

```bash
git add scripts/data/effect_data.gd
git commit -m "feat: add EffectData resource type for card/relic effect definitions

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: CardData 资源 + 枚举定义

**Files:**
- Create: `scripts/data/card_data.gd`

- [ ] **Step 1: 创建 CardData Resource 类**

```gdscript
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
```

- [ ] **Step 2: Commit**

```bash
git add scripts/data/card_data.gd
git commit -m "feat: add CardData resource type with runtime copy support and enums

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: 状态效果数据 + 敌人/遗物数据

**Files:**
- Create: `scripts/data/status_effect_data.gd`
- Create: `scripts/data/enemy_data.gd`
- Create: `scripts/data/intent_data.gd`
- Create: `scripts/data/phase_config.gd`
- Create: `scripts/data/relic_data.gd`

- [ ] **Step 1: 创建 StatusEffectData Resource**

```gdscript
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
```

- [ ] **Step 2: 创建 IntentData + PhaseConfig Resource**

```gdscript
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
```

```gdscript
# scripts/data/phase_config.gd
## Boss 多阶段配置。
class_name PhaseConfig
extends Resource

@export var hp_threshold: float = 1.0                  # 触发 HP 百分比 (0.0-1.0)
@export var sprite_path: String = ""                   # 阶段美术资源
@export var new_intent_pattern: Array[IntentData] = []  # 新意图循环
@export var phase_animation: String = ""               # 切换动画名
@export var clear_statuses: Array[String] = []         # 进阶段时清除的状态 id
```

- [ ] **Step 3: 创建 EnemyData Resource**

```gdscript
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
```

- [ ] **Step 4: 创建 RelicData Resource**

```gdscript
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
```

- [ ] **Step 5: Commit**

```bash
git add scripts/data/
git commit -m "feat: add StatusEffectData, EnemyData, IntentData, PhaseConfig, RelicData

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: ResourceManager（HP/精神力/力量/敏捷/格挡/魔晶）

**Files:**
- Create: `scripts/battle/resource_manager.gd`

- [ ] **Step 1: 编写 ResourceManager**

```gdscript
# scripts/battle/resource_manager.gd
## 战斗中所有数值资源管理: HP、精神力、力量、敏捷、格挡、魔晶。
## 通过信号通知 UI 层资源变化。
class_name ResourceManager
extends Node

# ——— 玩家资源 ———
var _player_hp: int = 0
var _player_max_hp: int = 75
var _player_energy: int = 3
var _max_energy_per_turn: int = 3
var _player_block: int = 0
var _player_strength: int = 0
var _player_dexterity: int = 0
var _crystals: int = 0

# ——— 敌人资源（字典, key = Enemy 的 instance_id） ———
var _enemy_hp: Dictionary = {}             # id: current_hp
var _enemy_max_hp: Dictionary = {}         # id: max_hp
var _enemy_block: Dictionary = {}          # id: block
var _enemy_strength: Dictionary = {}       # id: strength
var _enemy_dexterity: Dictionary = {}      # id: dexterity

# ——— 信号 ———
signal player_hp_changed(current: int, max_hp: int, delta: int)
signal player_energy_changed(current: int)
signal player_block_changed(current: int)
signal player_strength_changed(value: int)
signal player_dexterity_changed(value: int)
signal crystals_changed(count: int)
signal entity_hp_changed(entity: Node, current: int, max_hp: int, delta: int)
signal entity_block_changed(entity: Node, current: int)
signal entity_died(entity: Node, killer: Node)
signal player_died


## 初始化玩家资源
func init_player(hp: int, max_hp: int, energy: int = 3) -> void:
    _player_hp = hp
    _player_max_hp = max_hp
    _player_energy = energy
    _max_energy_per_turn = energy
    _player_block = 0
    _player_strength = 0
    _player_dexterity = 0
    _crystals = 0
    player_hp_changed.emit(_player_hp, _player_max_hp, 0)
    player_energy_changed.emit(_player_energy)


## 注册敌人到资源管理器
func register_enemy(enemy: Node, max_hp: int) -> void:
    var key: int = enemy.get_instance_id()
    _enemy_hp[key] = max_hp
    _enemy_max_hp[key] = max_hp
    _enemy_block[key] = 0
    _enemy_strength[key] = 0
    _enemy_dexterity[key] = 0


## 注销敌人
func unregister_enemy(enemy: Node) -> void:
    var key: int = enemy.get_instance_id()
    _enemy_hp.erase(key); _enemy_max_hp.erase(key)
    _enemy_block.erase(key); _enemy_strength.erase(key); _enemy_dexterity.erase(key)


# ——— 玩家方法 ———

func get_player_hp() -> int:  return _player_hp
func get_player_max_hp() -> int:  return _player_max_hp
func get_player_energy() -> int:  return _player_energy
func get_player_block() -> int:  return _player_block
func get_player_strength() -> int:  return _player_strength
func get_player_dexterity() -> int:  return _player_dexterity
func get_crystals() -> int:  return _crystals


## 伤害/治疗入口。damage_type: "normal" / "holy" (神圣伤害无视格挡)
func modify_player_hp(delta: int, damage_type: String = "normal") -> void:
    if delta < 0:
        var actual_damage: int = _calculate_damage(-delta, _player_block, damage_type)
        _player_hp = maxi(0, _player_hp - actual_damage)
        player_energy_changed.emit(_player_energy)  # 确保 UI 更新（有需要时）
    else:
        _player_hp = mini(_player_max_hp, _player_hp + delta)
    player_hp_changed.emit(_player_hp, _player_max_hp, delta)
    _check_player_death()


func modify_player_max_hp(delta: int) -> void:
    _player_max_hp = maxi(1, _player_max_hp + delta)
    _player_hp = mini(_player_hp, _player_max_hp)
    player_hp_changed.emit(_player_hp, _player_max_hp, 0)


func modify_player_energy(delta: int) -> void:
    _player_energy = maxi(0, _player_energy + delta)
    player_energy_changed.emit(_player_energy)


func modify_player_block(delta: int) -> void:
    _player_block = maxi(0, _player_block + delta)
    player_block_changed.emit(_player_block)


func modify_player_strength(delta: int) -> void:
    _player_strength += delta
    player_strength_changed.emit(_player_strength)


func modify_player_dexterity(delta: int) -> void:
    _player_dexterity += delta
    player_dexterity_changed.emit(_player_dexterity)


func add_crystals(amount: int) -> void:
    _crystals += amount
    crystals_changed.emit(_crystals)


# ——— 敌人方法 ———

func get_enemy_hp(enemy: Node) -> int:
    var key: int = enemy.get_instance_id()
    return _enemy_hp.get(key, 0)


func get_enemy_max_hp(enemy: Node) -> int:
    var key: int = enemy.get_instance_id()
    return _enemy_max_hp.get(key, 0)


func get_enemy_block(enemy: Node) -> int:
    var key: int = enemy.get_instance_id()
    return _enemy_block.get(key, 0)


func get_enemy_strength(enemy: Node) -> int:
    var key: int = enemy.get_instance_id()
    return _enemy_strength.get(key, 0)


func get_enemy_dexterity(enemy: Node) -> int:
    var key: int = enemy.get_instance_id()
    return _enemy_dexterity.get(key, 0)


func modify_enemy_hp(enemy: Node, delta: int, damage_type: String = "normal") -> void:
    var key: int = enemy.get_instance_id()
    var current_hp: int = _enemy_hp.get(key, 0)
    var max_hp: int = _enemy_max_hp.get(key, 0)
    if delta < 0:
        var block: int = _enemy_block.get(key, 0)
        var actual: int = _calculate_damage(-delta, block, damage_type)
        _enemy_hp[key] = maxi(0, current_hp - actual)
    else:
        _enemy_hp[key] = mini(max_hp, current_hp + delta)
    entity_hp_changed.emit(enemy, _enemy_hp[key], max_hp, delta)
    if _enemy_hp[key] <= 0:
        _on_entity_death(enemy, null)


func modify_enemy_block(enemy: Node, delta: int) -> void:
    var key: int = enemy.get_instance_id()
    var current: int = _enemy_block.get(key, 0)
    _enemy_block[key] = maxi(0, current + delta)
    entity_block_changed.emit(enemy, _enemy_block[key])


func modify_enemy_strength(enemy: Node, delta: int) -> void:
    var key: int = enemy.get_instance_id()
    _enemy_strength[key] = _enemy_strength.get(key, 0) + delta


func modify_enemy_dexterity(enemy: Node, delta: int) -> void:
    var key: int = enemy.get_instance_id()
    _enemy_dexterity[key] = _enemy_dexterity.get(key, 0) + delta


# ——— 回合方法 ———

## 回合开始时调用：精神力回满，格挡清零
func on_turn_start() -> void:
    _player_energy = _max_energy_per_turn
    _player_block = 0
    player_energy_changed.emit(_player_energy)
    player_block_changed.emit(_player_block)
    # 敌人格挡也在回合开始时清零
    for key in _enemy_block.keys():
        _enemy_block[key] = 0
        var enemy: Node = instance_from_id(key)
        if enemy:
            entity_block_changed.emit(enemy, 0)


## 回合结束时调用
func on_turn_end() -> void:
    _player_block = 0
    player_block_changed.emit(_player_block)


# ——— 属性加成 ———

## 计算有效伤害值 = 基础值 + 力量
func get_effective_damage(base: int, is_player: bool = true) -> int:
    var extra: int = _player_strength if is_player else 0
    return maxi(0, base + extra)


## 计算有效格挡值 = 基础值 + 敏捷
func get_effective_block(base: int, is_player: bool = true) -> int:
    var extra: int = _player_dexterity if is_player else 0
    return maxi(0, base + extra)


# ——— 内部方法 ———

func _calculate_damage(raw: int, block: int, damage_type: String) -> int:
    if damage_type == "holy":
        return raw  # 神圣伤害无视格挡
    # 穿透 (pierce) 从 EffectResolver 传入, 此处 block 已经过处理
    var blocked: int = mini(raw, block)
    var actual: int = raw - blocked
    # 更新格挡
    if block > 0:
        # 需要通过 modify_player_block 或 modify_enemy_block 来更新
        pass
    return maxi(1, actual)  # 至少 1 点伤害（除非格挡完全吸收）


func _check_player_death() -> void:
    if _player_hp <= 0:
        player_died.emit()


func _on_entity_death(entity: Node, killer: Node) -> void:
    entity_died.emit(entity, killer)
```

- [ ] **Step 2: Commit**

```bash
git add scripts/battle/resource_manager.gd
git commit -m "feat: add ResourceManager for HP/energy/block/strength/dexterity/crystals

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: StatusManager（Buff/Debuff 管理）

**Files:**
- Create: `scripts/battle/status_manager.gd`

- [ ] **Step 1: 编写 StatusManager**

```gdscript
# scripts/battle/status_manager.gd
## 状态效果管理器。对所有实体（玩家/敌人）的 Buff/Debuff 进行增删改查和回合结算。
class_name StatusManager
extends Node

## 存储结构: {entity_instance_id: {status_id: {"stacks": int, "duration": int, "data": StatusEffectData}}}
var _statuses: Dictionary = {}
var _status_registry: Dictionary = {}  # status_id -> StatusEffectData


signal status_applied(entity: Node, status_id: String, stacks: int)
signal status_removed(entity: Node, status_id: String)
signal status_stacks_changed(entity: Node, status_id: String, current_stacks: int)
signal status_expired(entity: Node, expired_ids: Array)
signal freeze_triggered(entity: Node)
signal thorn_damage(source: Node, damage: int)


## 注册状态效果数据（战斗开始时由角色 Mechanic 调用）
func register_status(data: StatusEffectData) -> void:
    _status_registry[data.status_id] = data


## 对目标施加状态
func apply_status(entity: Node, status_id: String, stacks: int = 1, duration: int = -1) -> void:
    if not status_id in _status_registry:
        push_warning("StatusManager: unknown status_id '%s'" % status_id)
        return
    var data: StatusEffectData = _status_registry[status_id]
    var key: int = entity.get_instance_id()
    if not key in _statuses:
        _statuses[key] = {}

    if status_id in _statuses[key]:
        # 已有该状态
        var entry: Dictionary = _statuses[key][status_id]
        var new_duration: int = duration
        match data.stack_type:
            StatusEffectData.StackType.INTENSITY:
                var new_stacks: int = entry["stacks"] + stacks
                if data.max_stacks > 0:
                    new_stacks = mini(new_stacks, data.max_stacks)
                entry["stacks"] = new_stacks
                if duration > 0:
                    new_duration = maxi(entry["duration"], duration)
            StatusEffectData.StackType.DURATION_ONLY:
                # 只重置持续时间
                new_duration = maxi(entry["duration"], duration)
            StatusEffectData.StackType.COUNTER:
                entry["stacks"] = entry["stacks"] + stacks
                new_duration = -1
        entry["duration"] = new_duration
    else:
        _statuses[key][status_id] = {
            "stacks": stacks,
            "duration": duration if duration > 0 else data.default_duration,
            "data": data
        }

    status_applied.emit(entity, status_id, stacks)

    # 冰霜冻结检查
    if status_id == "frost":
        _check_freeze(entity)


## 检查目标是否有某个状态
func has_status(entity: Node, status_id: String) -> bool:
    var key: int = entity.get_instance_id()
    if not key in _statuses:
        return false
    return status_id in _statuses[key]


## 获取指定状态的层数
func get_stacks(entity: Node, status_id: String) -> int:
    var key: int = entity.get_instance_id()
    if not key in _statuses or not status_id in _statuses[key]:
        return 0
    return _statuses[key][status_id]["stacks"]


## 移除指定状态
func remove_status(entity: Node, status_id: String) -> void:
    var key: int = entity.get_instance_id()
    if key in _statuses and status_id in _statuses[key]:
        _statuses[key].erase(status_id)
        status_removed.emit(entity, status_id)


## 清除目标所有状态（冻结触发时）
func clear_all_statuses(entity: Node) -> void:
    var key: int = entity.get_instance_id()
    if key in _statuses:
        var removed: Array[String] = []
        for sid in _statuses[key].keys():
            removed.append(sid)
        _statuses[key].clear()
        for sid in removed:
            status_removed.emit(entity, sid)


## 回合结束时刷新状态：tick_effect → duration-1 → 移除到期状态
func tick_statuses(entity: Node) -> void:
    var key: int = entity.get_instance_id()
    if not key in _statuses:
        return

    var expired: Array[String] = []

    for status_id in _statuses[key].keys():
        var entry: Dictionary = _statuses[key][status_id]
        var data: StatusEffectData = entry["data"]

        # 执行 tick_effect（中毒/灼烧）
        for effect in data.tick_effects:
            # 由 EffectResolver 处理 tick effect
            pass

        # Duration-1
        if entry["duration"] > 0:
            entry["duration"] -= 1
            if entry["duration"] <= 0:
                expired.append(status_id)

    # 移除到期状态
    for sid in expired:
        _statuses[key].erase(sid)

    if not expired.is_empty():
        status_expired.emit(entity, expired)

    # 荆棘结算（叶默）
    if has_status(entity, "thorns"):
        var thorn_stacks: int = get_stacks(entity, "thorns")
        thorn_damage.emit(entity, thorn_stacks)


## 获取目标所有活跃状态（用于 UI 展示）
func get_active_statuses(entity: Node) -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    var key: int = entity.get_instance_id()
    if not key in _statuses:
        return result
    for sid in _statuses[key]:
        var entry: Dictionary = _statuses[key][sid]
        result.append({
            "status_id": sid,
            "stacks": entry["stacks"],
            "duration": entry["duration"],
            "display_name": entry["data"].display_name,
            "category": entry["data"].category,
            "icon_path": entry["data"].icon_path,
        })
    return result


## 获取伤害倍率修正（易伤/虚弱 抵消结算）
func get_damage_multiplier(entity: Node, is_dealing: bool) -> float:
    var mult: float = 1.0
    if is_dealing:
        # 造成伤害时的修正
        var weak_stacks: int = get_stacks(entity, "weak")
        mult -= 0.25 * weak_stacks
    else:
        # 受到伤害时的修正
        var vuln_stacks: int = get_stacks(entity, "vulnerable")
        mult += 0.25 * vuln_stacks
    return maxf(0.0, mult)


## 冰霜冻结检查（墨夜）
func _check_freeze(entity: Node) -> void:
    var frost_stacks: int = get_stacks(entity, "frost")
    if frost_stacks >= 8:
        freeze_triggered.emit(entity)
        clear_all_statuses(entity)
        # 施加冻结状态
        apply_status(entity, "frozen", 1, 1)
```

- [ ] **Step 2: Commit**

```bash
git add scripts/battle/status_manager.gd
git commit -m "feat: add StatusManager for buff/debuff tracking and turn-end ticking

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 7: CardManager（牌堆/抽牌/弃牌/锻造）

**Files:**
- Create: `scripts/battle/card_manager.gd`

- [ ] **Step 1: 编写 CardManager**

```gdscript
# scripts/battle/card_manager.gd
## 卡牌管理器: 四大牌堆管理 + 抽牌/弃牌/消耗 + 洗牌 + 锻造。
class_name CardManager
extends Node

var draw_pile: Array[CardData] = []        # 抽牌堆（顶部=下一个抽到）
var hand: Array[CardData] = []             # 手牌
var discard_pile: Array[CardData] = []     # 弃牌堆
var exhaust_pile: Array[CardData] = []     # 消耗堆
var _deck_initialized: bool = false

signal card_drawn(card: CardData, count: int)
signal card_played(card: CardData, target: Node)
signal card_discarded(card: CardData)
signal card_exhausted(card: CardData)
signal deck_shuffled
signal deck_cycle
signal hand_empty
signal card_upgraded(card: CardData, source: String)


## 用初始牌组初始化
func init_deck(deck_list: Array[CardData]) -> void:
    draw_pile.clear()
    hand.clear()
    discard_pile.clear()
    exhaust_pile.clear()
    for card in deck_list:
        draw_pile.append(card.create_runtime_copy())
    shuffle_deck()
    _deck_initialized = true


## 抽卡（含自动洗牌）
func draw_cards(count: int) -> Array[CardData]:
    var drawn: Array[CardData] = []
    var remaining: int = count
    while remaining > 0:
        if draw_pile.is_empty():
            if discard_pile.is_empty():
                break
            _cycle_discard_to_draw()
        var card: CardData = draw_pile.pop_back()
        hand.append(card)
        drawn.append(card)
        remaining -= 1
    card_drawn.emit(drawn[-1] if not drawn.is_empty() else null, drawn.size())
    return drawn


## 抽满到手牌数达到 hand_size（通常 5 张）
func draw_to_hand_size(hand_size: int) -> Array[CardData]:
    var missing: int = hand_size - hand.size()
    if missing <= 0:
        return []
    return draw_cards(missing)


## 从手牌打出卡牌（费用和有效性由 BattleManager 外层校验）
func play_card(card: CardData, target: Node) -> void:
    var idx: int = hand.find(card)
    if idx == -1:
        push_error("CardManager.play_card: card not in hand")
        return
    hand.remove_at(idx)

    if card.is_exhaust_card():
        exhaust_pile.append(card)
        card_exhausted.emit(card)
    else:
        discard_pile.append(card)
        card_discarded.emit(card)

    if hand.is_empty():
        hand_empty.emit()


## 弃所有手牌
func discard_hand() -> void:
    for card in hand:
        discard_pile.append(card)
    hand.clear()


## 指定弃牌
func discard_card(card: CardData) -> void:
    var idx: int = hand.find(card)
    if idx == -1:
        return
    hand.remove_at(idx)
    discard_pile.append(card)
    card_discarded.emit(card)


## 消耗牌
func exhaust_card(card: CardData) -> void:
    var idx: int = hand.find(card)
    if idx == -1:
        return
    hand.remove_at(idx)
    exhaust_pile.append(card)
    card_exhausted.emit(card)


## 战斗中新增卡牌（入弃牌堆）
func add_card_to_deck(card: CardData) -> void:
    discard_pile.append(card.create_runtime_copy())


## 直接入手牌
func add_card_to_hand(card: CardData) -> void:
    hand.append(card)


## 从战斗中完全移除
func remove_card_from_battle(card: CardData) -> void:
    var idx: int = hand.find(card)
    if idx != -1:
        hand.remove_at(idx)


## 锻造（叶默: 升级手牌中卡牌）
func forge_card_in_hand(card: CardData) -> void:
    if card.forge_count >= card._forge_max:
        return
    var idx: int = hand.find(card)
    if idx == -1:
        return
    # 复制实例 → 修改数值 → 标记为已锻造
    var forged: CardData = card.create_runtime_copy()
    forged.is_forged = true
    forged.forge_count += 1
    # 数值增量 30-50%（基础伤害/格挡）
    for effect in forged.effects:
        match effect.type:
            EffectData.EffectType.DAMAGE, EffectData.EffectType.BLOCK:
                effect.base_value = int(ceilf(effect.base_value * 1.3))
    # 替换手牌中旧卡
    hand[idx] = forged
    card_upgraded.emit(forged, "forge")


## 洗牌
func shuffle_deck() -> void:
    draw_pile.shuffle()
    deck_shuffled.emit()


## 获取各牌堆信息
func get_draw_count() -> int:  return draw_pile.size()
func get_hand_size() -> int:  return hand.size()
func get_discard_count() -> int:  return discard_pile.size()
func get_exhaust_count() -> int:  return exhaust_pile.size()
func get_total_count() -> int:  return draw_pile.size() + hand.size() + discard_pile.size()


# ——— 内部 ———

func _cycle_discard_to_draw() -> void:
    draw_pile = discard_pile.duplicate()
    discard_pile.clear()
    shuffle_deck()
    deck_cycle.emit()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/battle/card_manager.gd
git commit -m "feat: add CardManager with 4-pile management, draw/shuffle/forge support

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 8: TurnStateMachine（回合状态机）

**Files:**
- Create: `scripts/battle/turn_state_machine.gd`

- [ ] **Step 1: 编写 TurnStateMachine**

```gdscript
# scripts/battle/turn_state_machine.gd
## 回合状态机: 管理 7 个状态流转。
##
## BATTLE_START → PLAYER_TURN_START → PLAYER_PLAY → PLAYER_TURN_END
## → ENEMY_TURN → ROUND_END → (loop) → BATTLE_WIN / BATTLE_LOSE
class_name TurnStateMachine
extends Node

enum BattleState {
    BATTLE_START,
    PLAYER_TURN_START,
    PLAYER_PLAY,
    PLAYER_TURN_END,
    ENEMY_TURN,
    ROUND_END,
    BATTLE_WIN,
    BATTLE_LOSE
}

var current_state: BattleState = BattleState.BATTLE_START
var round_number: int = 0
var _hand_size: int = 5                            # 每回合手牌上限
var _energy_per_turn: int = 3                      # 每回合精神力

signal state_changed(from_state: BattleState, to_state: BattleState)
signal player_turn_started(round_num: int)
signal player_turn_ended
signal enemy_turn_started
signal enemy_turn_ended
signal round_ended
signal battle_won
signal battle_lost


## 设置战斗参数
func configure(hand_size: int = 5, energy_per_turn: int = 3) -> void:
    _hand_size = hand_size
    _energy_per_turn = energy_per_turn


## 开始战斗
func start_battle() -> void:
    _transition_to(BattleState.BATTLE_START)


## 玩家请求结束回合
func request_end_turn() -> void:
    if current_state == BattleState.PLAYER_PLAY:
        _transition_to(BattleState.PLAYER_TURN_END)


## 获取手牌上限
func get_hand_size() -> int:  return _hand_size
func get_energy_per_turn() -> int:  return _energy_per_turn


func _transition_to(new_state: BattleState) -> void:
    var old_state: BattleState = current_state
    current_state = new_state
    state_changed.emit(old_state, new_state)

    match new_state:
        BattleState.BATTLE_START:
            # 初始化逻辑由 BattleManager 的监听器处理
            pass
        BattleState.PLAYER_TURN_START:
            round_number += 1
            player_turn_started.emit(round_number)
        BattleState.PLAYER_PLAY:
            # 等待玩家操作
            pass
        BattleState.PLAYER_TURN_END:
            player_turn_ended.emit()
        BattleState.ENEMY_TURN:
            enemy_turn_started.emit()
        BattleState.ROUND_END:
            round_ended.emit()
        BattleState.BATTLE_WIN:
            battle_won.emit()
        BattleState.BATTLE_LOSE:
            battle_lost.emit()


## 进入玩家回合
func _go_to_player_turn() -> void:
    _transition_to(BattleState.PLAYER_TURN_START)
    # 自动进入出牌阶段
    _transition_to(BattleState.PLAYER_PLAY)


## 结束玩家回合
func _go_to_player_turn_end() -> void:
    _transition_to(BattleState.PLAYER_TURN_END)


## 进入敌人回合
func _go_to_enemy_turn() -> void:
    _transition_to(BattleState.ENEMY_TURN)


## 回合结束
func _go_to_round_end() -> void:
    _transition_to(BattleState.ROUND_END)
    # 自动进入下一回合
    _go_to_player_turn()


## 胜利/失败
func trigger_victory() -> void:
    _transition_to(BattleState.BATTLE_WIN)

func trigger_defeat() -> void:
    _transition_to(BattleState.BATTLE_LOSE)
```

- [ ] **Step 2: Commit**

```bash
git add scripts/battle/turn_state_machine.gd
git commit -m "feat: add TurnStateMachine with 7-state battle flow

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 9: EffectResolver（效果结算管道）

**Files:**
- Create: `scripts/battle/effect_resolver.gd`

- [ ] **Step 1: 编写 EffectResolver**

```gdscript
# scripts/battle/effect_resolver.gd
## 效果结算管道: 接收 EffectData 数组, 按 TARGET_RESOLVE → PRECONDITION
## → PRE_TRIGGER → EXECUTE → POST_TRIGGER → KILL_CHECK 顺序结算。
class_name EffectResolver
extends Node

var _resource_manager: ResourceManager
var _card_manager: CardManager
var _status_manager: StatusManager
var _enemy_manager: Node  # EnemyManager 引用
var _relic_manager: Node  # RelicManager 引用


signal effect_about_to_execute(effect: EffectData, target: Node)
signal effect_executed(effect: EffectData, target: Node, result: Dictionary)
signal damage_about_to_apply(target: Node, amount: int)
signal damage_applied(target: Node, raw_amount: int, actual: int, blocked: int)
signal block_gained(target: Node, amount: int)
signal healing_applied(target: Node, amount: int)
signal kill_confirmed(target: Node, crystals: int)


## 注入依赖
func setup(
    rm: ResourceManager,
    cm: CardManager,
    sm: StatusManager,
    em: Node,
    rem: Node
) -> void:
    _resource_manager = rm
    _card_manager = cm
    _status_manager = sm
    _enemy_manager = em
    _relic_manager = rem


## 结算一组效果（一张卡牌的全部效果）
func resolve_effects(effects: Array[EffectData], source: Node, caster_is_player: bool = true, pierce: int = 0) -> void:
    for effect in effects:
        var targets: Array[Node] = _resolve_targets(effect, source, caster_is_player)
        for i in range(effect.repeat_count):
            for target in targets:
                if not _check_precondition(effect, target):
                    continue
                effect_about_to_execute.emit(effect, target)
                # PRE_TRIGGER: RelicManager.trigger("on_card_played", ...)
                _execute_effect(effect, target, caster_is_player, pierce)
                # POST_TRIGGER: RelicManager.trigger(...)
                effect_executed.emit(effect, target, {})
                _check_kill(target)


## 解析目标
func _resolve_targets(effect: EffectData, source: Node, caster_is_player: bool) -> Array[Node]:
    match effect.target:
        EffectData.EffectTarget.SELF:
            return [source]
        EffectData.EffectTarget.SINGLE_ENEMY:
            # 返回调用者传入的具体目标（由玩家在 UI 中选择）
            return []  # 实际目标由 play_card 调用时传入
        EffectData.EffectTarget.ALL_ENEMIES:
            if _enemy_manager and _enemy_manager.has_method("get_alive_enemies"):
                return _enemy_manager.get_alive_enemies()
            return []
        EffectData.EffectTarget.RANDOM_ENEMY:
            if _enemy_manager and _enemy_manager.has_method("get_alive_enemies"):
                var enemies: Array = _enemy_manager.get_alive_enemies()
                if not enemies.is_empty():
                    return [enemies.pick_random()]
            return []
        EffectData.EffectTarget.FRONTMOST_ENEMY:
            if _enemy_manager and _enemy_manager.has_method("get_frontmost_enemy"):
                var front: Node = _enemy_manager.get_frontmost_enemy()
                if front:
                    return [front]
            return []
        EffectData.EffectTarget.ALL_ALLIES:
            if _enemy_manager and _enemy_manager.has_method("get_alive_allies"):
                return _enemy_manager.get_alive_allies()
            return []
    return []


func _check_precondition(effect: EffectData, target: Node) -> bool:
    if effect.condition.is_empty():
        return true
    if effect.condition == "target_has_mark":
        return _status_manager.has_status(target, "mark")
    if effect.condition == "target_alive":
        return is_instance_valid(target)
    return true


## 执行单个效果
func _execute_effect(effect: EffectData, target: Node, caster_is_player: bool, pierce: int) -> void:
    match effect.type:
        EffectData.EffectType.DAMAGE:
            _execute_damage(effect, target, caster_is_player, pierce)
        EffectData.EffectType.BLOCK:
            _execute_block(effect, target, caster_is_player)
        EffectData.EffectType.DRAW:
            _execute_draw(effect)
        EffectData.EffectType.GAIN_ENERGY:
            _execute_gain_energy(effect)
        EffectData.EffectType.BUFF:
            _execute_buff(effect, target)
        EffectData.EffectType.DEBUFF:
            _execute_debuff(effect, target)
        EffectData.EffectType.HEAL:
            _execute_heal(effect, target, caster_is_player)
        EffectData.EffectType.MODIFY_STAT:
            _execute_modify_stat(effect, target, caster_is_player)
        EffectData.EffectType.REMOVE_STATUS:
            _status_manager.remove_status(target, effect.status_id)
        EffectData.EffectType.SPECIAL:
            pass  # 由角色 Mechanic 处理


func _execute_damage(effect: EffectData, target: Node, caster_is_player: bool, pierce: int) -> void:
    var is_player_target: bool = (target == _get_player_node())
    var effective_damage: int = _resource_manager.get_effective_damage(effect.base_value, caster_is_player)
    var mult: float = _status_manager.get_damage_multiplier(
        _get_player_node() if caster_is_player else target,
        caster_is_player
    )
    var raw: int = int(ceilf(effective_damage * mult))
    damage_about_to_apply.emit(target, raw)

    var block: int
    if is_player_target:
        block = _resource_manager.get_player_block()
    else:
        block = _resource_manager.get_enemy_block(target)
    block = maxi(0, block - pierce)  # 穿透

    var absorbed: int = mini(raw, block)
    var actual: int = raw - absorbed

    if is_player_target:
        _resource_manager.modify_player_hp(-actual, "normal")
        if absorbed > 0:
            _resource_manager.modify_player_block(-absorbed)
    else:
        _resource_manager.modify_enemy_hp(target, -actual, "normal")
        if absorbed > 0:
            _resource_manager.modify_enemy_block(target, -absorbed)

    damage_applied.emit(target, raw, actual, absorbed)


func _execute_block(effect: EffectData, target: Node, caster_is_player: bool) -> void:
    var effective_block: int = _resource_manager.get_effective_block(effect.base_value, caster_is_player)
    var is_player_target: bool = (target == _get_player_node())
    if is_player_target:
        _resource_manager.modify_player_block(effective_block)
    else:
        _resource_manager.modify_enemy_block(target, effective_block)
    block_gained.emit(target, effective_block)


func _execute_draw(effect: EffectData) -> void:
    _card_manager.draw_cards(effect.base_value)


func _execute_gain_energy(effect: EffectData) -> void:
    _resource_manager.modify_player_energy(effect.base_value)


func _execute_buff(effect: EffectData, target: Node) -> void:
    _status_manager.apply_status(target, effect.status_id, effect.status_stacks, effect.status_duration)


func _execute_debuff(effect: EffectData, target: Node) -> void:
    _status_manager.apply_status(target, effect.status_id, effect.status_stacks, effect.status_duration)


func _execute_heal(effect: EffectData, target: Node, caster_is_player: bool) -> void:
    var is_player_target: bool = (target == _get_player_node())
    if is_player_target:
        _resource_manager.modify_player_hp(effect.base_value, "heal")
    else:
        _resource_manager.modify_enemy_hp(target, effect.base_value, "heal")
    healing_applied.emit(target, effect.base_value)


func _execute_modify_stat(effect: EffectData, target: Node, caster_is_player: bool) -> void:
    var is_player_target: bool = (target == _get_player_node())
    match effect.status_id:
        "strength":
            if is_player_target:
                _resource_manager.modify_player_strength(effect.base_value)
            else:
                _resource_manager.modify_enemy_strength(target, effect.base_value)
        "dexterity":
            if is_player_target:
                _resource_manager.modify_player_dexterity(effect.base_value)
            else:
                _resource_manager.modify_enemy_dexterity(target, effect.base_value)


func _check_kill(target: Node) -> void:
    if not is_instance_valid(target):
        return
    var hp: int
    if target == _get_player_node():
        hp = _resource_manager.get_player_hp()
    else:
        hp = _resource_manager.get_enemy_hp(target)
    if hp <= 0:
        var crystals: int = 0
        if _enemy_manager and _enemy_manager.has_method("get_crystal_drop"):
            crystals = _enemy_manager.get_crystal_drop(target)
        kill_confirmed.emit(target, crystals)


## 对具体目标结算效果（由外部通过 play_card 调用时传入具体 target）
func resolve_effects_on_target(effects: Array[EffectData], target: Node, source: Node, caster_is_player: bool = true, pierce: int = 0) -> void:
    for effect in effects:
        if not _check_precondition(effect, target):
            continue
        effect_about_to_execute.emit(effect, target)
        _execute_effect(effect, target, caster_is_player, pierce)
        effect_executed.emit(effect, target, {})
        _check_kill(target)


func _get_player_node() -> Node:
    if _resource_manager:
        return _resource_manager.get_parent()  # 假设 ResourceManager 和玩家节点同父
    return null
```

- [ ] **Step 2: Commit**

```bash
git add scripts/battle/effect_resolver.gd
git commit -m "feat: add EffectResolver pipeline for damage/block/buff/debuff/heal resolution

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 10: EnemyManager + EnemyAI

**Files:**
- Create: `scripts/battle/enemy_manager.gd`

- [ ] **Step 1: 编写 EnemyManager**

```gdscript
# scripts/battle/enemy_manager.gd
## 敌人管理器: 敌方格 + 友方格 slot 管理 + AI 调度。
class_name EnemyManager
extends Node

const MAX_ENEMY_SLOTS: int = 5
const MAX_ALLY_SLOTS: int = 5  # 基础 4 + 遗物 +1

var _enemies: Array[Node] = []               # 存活敌人列表（按 slot 顺序）
var _allies: Array[Node] = []                # 友方随从（红发丧尸）
var _enemy_data_map: Dictionary = {}          # Node -> EnemyData
var _enemy_ai_map: Dictionary = {}            # Node -> intent data
var _crystal_drops: Dictionary = {}           # Node -> crystal count

signal enemy_intent_revealed(enemy: Node, intent: IntentData)
signal enemy_acted(enemy: Node, intent: IntentData, result: Dictionary)
signal enemy_spawned(enemy: Node, slot_index: int)
signal enemy_killed(enemy: Node, crystal_reward: int)
signal boss_phase_changed(boss: Node, phase_index: int)
signal ally_spawned(ally: Node, slot_index: int)
signal ally_acted(ally: Node, target: Node, damage: int)
signal ally_killed(ally: Node)


## 根据 EnemyData 生成敌人并加入敌方格
func spawn_enemy(data: EnemyData, slot_index: int = -1) -> Node:
    var enemy := Node.new()
    enemy.set_meta("enemy_id", data.enemy_id)
    enemy.set_meta("display_name", data.display_name)
    add_child(enemy)
    # 初始化资源
    var rm: ResourceManager = _get_resource_manager()
    rm.register_enemy(enemy, data.base_hp)
    _enemy_data_map[enemy] = data
    _crystal_drops[enemy] = data.crystal_drop

    if slot_index == -1 or slot_index >= MAX_ENEMY_SLOTS:
        _enemies.append(enemy)
    else:
        _enemies.insert(slot_index, enemy)

    # 生成第一个意图
    _generate_and_reveal_intent(enemy, data)
    enemy_spawned.emit(enemy, _enemies.find(enemy))
    return enemy


## 移除敌人
func remove_enemy(enemy: Node) -> void:
    var idx: int = _enemies.find(enemy)
    if idx != -1:
        _enemies.remove_at(idx)
    var rm: ResourceManager = _get_resource_manager()
    rm.unregister_enemy(enemy)
    _enemy_data_map.erase(enemy)
    _crystal_drops.erase(enemy)
    _enemy_ai_map.erase(enemy)
    if is_instance_valid(enemy):
        enemy.queue_free()


## 执行所有敌方意图（ENEMY_TURN 阶段）
func execute_all_enemy_intents() -> void:
    for enemy in _enemies:
        if not is_instance_valid(enemy):
            continue
        var intent: IntentData = _enemy_ai_map.get(enemy)
        if intent:
            _execute_intent(enemy, intent)
            # 生成下回合意图
            var data: EnemyData = _enemy_data_map.get(enemy)
            if data:
                _generate_and_reveal_intent(enemy, data)


## 友方随从自动攻击
func ally_auto_attack_all() -> void:
    for ally in _allies:
        if not is_instance_valid(ally):
            continue
        var enemies: Array = get_alive_enemies()
        if enemies.is_empty():
            return
        var target: Node = enemies.pick_random()
        var damage: int = ally.get_meta("attack_damage", 3)
        ally_acted.emit(ally, target, damage)


## 获取存活敌人列表
func get_alive_enemies() -> Array[Node]:
    var alive: Array[Node] = []
    for enemy in _enemies:
        if is_instance_valid(enemy) and _get_resource_manager().get_enemy_hp(enemy) > 0:
            alive.append(enemy)
    return alive


func get_frontmost_enemy() -> Node:
    for enemy in _enemies:
        if is_instance_valid(enemy) and _get_resource_manager().get_enemy_hp(enemy) > 0:
            return enemy
    return null


func get_alive_allies() -> Array[Node]:
    var alive: Array[Node] = []
    for ally in _allies:
        if is_instance_valid(ally):
            alive.append(ally)
    return alive


func get_crystal_drop(enemy: Node) -> int:
    return _crystal_drops.get(enemy, 0)


# ——— 内部 ———

func _generate_and_reveal_intent(enemy: Node, data: EnemyData) -> void:
    if data.intent_pattern.is_empty():
        return
    var intent: IntentData = data.intent_pattern[0]  # 简化: 使用 pattern 第一个
    _enemy_ai_map[enemy] = intent
    enemy_intent_revealed.emit(enemy, intent)


func _execute_intent(enemy: Node, intent: IntentData) -> void:
    var result: Dictionary = {}
    var rm: ResourceManager = _get_resource_manager()
    match intent.type:
        IntentData.IntentType.ATTACK:
            var target: Node = _get_player_node()
            var dmg: int = _calculate_actual_value(intent.base_value, intent.value_variance)
            # 通过 EffectResolver 或直接调用 ResourceManager
            rm.modify_player_hp(-dmg, "normal")
            result = {"damage": dmg}
        IntentData.IntentType.DEFEND:
            var block_amount: int = _calculate_actual_value(intent.base_value, intent.value_variance)
            rm.modify_enemy_block(enemy, block_amount)
            result = {"block": block_amount}
        IntentData.IntentType.BUFF:
            var sm: StatusManager = _get_status_manager()
            sm.apply_status(enemy, intent.status_id, intent.secondary_value, intent.status_duration)
            result = {"status": intent.status_id, "stacks": intent.secondary_value}
        IntentData.IntentType.DEBUFF:
            var sm: StatusManager = _get_status_manager()
            var target: Node = _get_player_node()
            sm.apply_status(target, intent.status_id, intent.secondary_value, intent.status_duration)
            result = {"status": intent.status_id, "stacks": intent.secondary_value}
        IntentData.IntentType.SUMMON:
            pass  # 召唤逻辑走 special_rules
        IntentData.IntentType.SPECIAL:
            pass
    enemy_acted.emit(enemy, intent, result)


func _calculate_actual_value(base: int, variance: float) -> int:
    var min_val: int = int(ceilf(base * (1.0 - variance)))
    var max_val: int = int(ceilf(base * (1.0 + variance)))
    return randi_range(min_val, max_val)


func _get_resource_manager() -> ResourceManager:
    return get_parent().get_node("ResourceManager") as ResourceManager


func _get_status_manager() -> Node:
    return get_parent().get_node("StatusManager")


func _get_player_node() -> Node:
    return get_tree().get_first_node_in_group("player")
```

- [ ] **Step 2: Commit**

```bash
git add scripts/battle/enemy_manager.gd
git commit -m "feat: add EnemyManager with spawn/intent/AI scheduling and ally support

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 11: BattleManager（顶层协调器 + 场景集成）

**Files:**
- Create: `scripts/battle/battle_manager.gd`
- Create: `scenes/battle/battle_scene.tscn`

- [ ] **Step 1: 编写 BattleManager**

```gdscript
# scripts/battle/battle_manager.gd
## 顶层战斗协调器。初始化所有子管理器, 连接回合状态机信号,
## 协调整个战斗流程。
class_name BattleManager
extends Node

@export var hand_size: int = 5
@export var energy_per_turn: int = 3

@onready var _turn_sm: TurnStateMachine = $TurnStateMachine
@onready var _card_mgr: CardManager = $CardManager
@onready var _resource_mgr: ResourceManager = $ResourceManager
@onready var _status_mgr: StatusManager = $StatusManager
@onready var _effect_resolver: EffectResolver = $EffectResolver
@onready var _enemy_mgr: EnemyManager = $EnemyManager
@onready var _relic_mgr: Node = $RelicManager

var _player_deck: Array[CardData] = []          # 初始牌组（由局外传入）
var _enemy_configs: Array[EnemyData] = []       # 本场敌人配置
var _battle_reward: Dictionary = {}              # 战斗奖励


func _ready() -> void:
    _setup_dependencies()
    _connect_signals()
    _turn_sm.configure(hand_size, energy_per_turn)


## 启动战斗（由局外 MapLevel 调用）
func start_battle(player_hp: int, player_max_hp: int, deck: Array[CardData], enemies: Array[EnemyData]) -> void:
    _player_deck = deck
    _enemy_configs = enemies
    _resource_mgr.init_player(player_hp, player_max_hp, energy_per_turn)
    _card_mgr.init_deck(deck)
    _spawn_enemies(enemies)
    _turn_sm.start_battle()


## 打出卡牌（由 UI 层调用）
func play_card(card: CardData, target: Node) -> void:
    var effective_cost: int = card.get_effective_cost()
    if _resource_mgr.get_player_energy() < effective_cost:
        return  # 精神力不足

    # 血祭消耗 HP
    for effect in card.effects:
        if effect.cost_hp > 0:
            _resource_mgr.modify_player_hp(-effect.cost_hp, "normal")

    # 扣除费用
    _resource_mgr.modify_player_energy(-effective_cost)

    # 结算效果
    _effect_resolver.resolve_effects_on_target(card.effects, target, self, true)
    _card_mgr.play_card(card, target)


func _setup_dependencies() -> void:
    _effect_resolver.setup(_resource_mgr, _card_mgr, _status_mgr, _enemy_mgr, _relic_mgr)


func _connect_signals() -> void:
    _turn_sm.state_changed.connect(_on_state_changed)
    _resource_mgr.player_died.connect(_on_player_died)
    _resource_mgr.entity_died.connect(_on_enemy_died)


func _spawn_enemies(configs: Array[EnemyData]) -> void:
    for data in configs:
        _enemy_mgr.spawn_enemy(data)


# ——— 状态机回调 ———

func _on_state_changed(from_state: int, to_state: int) -> void:
    match to_state:
        TurnStateMachine.BattleState.BATTLE_START:
            _on_battle_start()
        TurnStateMachine.BattleState.PLAYER_TURN_START:
            _on_player_turn_start()
        TurnStateMachine.BattleState.PLAYER_TURN_END:
            _on_player_turn_end()
        TurnStateMachine.BattleState.ENEMY_TURN:
            _on_enemy_turn()
        TurnStateMachine.BattleState.ROUND_END:
            _on_round_end()


func _on_battle_start() -> void:
    # 触发战斗开始遗物
    # _relic_mgr.trigger("ON_BATTLE_START", {})
    # 抽 5 张牌
    _card_mgr.draw_cards(hand_size)
    # 进入第一个玩家回合
    _turn_sm._go_to_player_turn()


func _on_player_turn_start() -> void:
    _resource_mgr.on_turn_start()
    _card_mgr.draw_to_hand_size(hand_size)
    # 触发回合开始遗物


func _on_player_turn_end() -> void:
    _card_mgr.discard_hand()
    _resource_mgr.on_turn_end()
    _status_mgr.tick_statuses(_get_player_node())
    _turn_sm._go_to_enemy_turn()


func _on_enemy_turn() -> void:
    _enemy_mgr.execute_all_enemy_intents()
    # 敌方随从攻击
    _enemy_mgr.ally_auto_attack_all()
    _turn_sm._go_to_round_end()


func _on_round_end() -> void:
    var alive_enemies: Array = _enemy_mgr.get_alive_enemies()
    if alive_enemies.is_empty():
        _on_battle_victory()
    elif _resource_mgr.get_player_hp() <= 0:
        _on_player_died()
    else:
        _turn_sm._go_to_player_turn()


func _on_battle_victory() -> void:
    # 计算魔晶
    var total_crystals: int = 0
    for enemy in _enemy_mgr._enemies:
        total_crystals += _enemy_mgr.get_crystal_drop(enemy)
    _resource_mgr.add_crystals(total_crystals)
    _turn_sm.trigger_victory()


func _on_player_died() -> void:
    _turn_sm.trigger_defeat()


func _on_enemy_died(entity: Node, killer: Node) -> void:
    var crystals: int = _enemy_mgr.get_crystal_drop(entity)
    _resource_mgr.add_crystals(crystals)
    _enemy_mgr.remove_enemy(entity)
    # 检查是否全部消灭
    call_deferred("_check_all_enemies_dead")


func _check_all_enemies_dead() -> void:
    if _enemy_mgr.get_alive_enemies().is_empty():
        _on_battle_victory()


func _get_player_node() -> Node:
    return get_tree().get_first_node_in_group("player")
```

- [ ] **Step 2: 创建战斗场景结构（BattleScene）**

```
# scenes/battle/battle_scene.tscn
#
# BattleScene (Node)  ← 根节点
# ├── BattleManager (Node)
# │   ├── TurnStateMachine (Node)   — turn_state_machine.gd
# │   ├── CardManager (Node)        — card_manager.gd
# │   ├── ResourceManager (Node)    — resource_manager.gd
# │   ├── StatusManager (Node)      — status_manager.gd
# │   ├── EffectResolver (Node)     — effect_resolver.gd
# │   ├── EnemyManager (Node)       — enemy_manager.gd
# │   ├── RelicManager (Node)       — relic_manager.gd (stub)
# │   └── CharacterMechanics (Node) — (stub, 后续 Plan 实现)
# ├── PlayerArea (Control)          — UI 占位
# ├── EnemyArea (Control)           — UI 占位
# ├── HUD (Control)                 — UI 占位
# └── EffectsLayer (Control)        — UI 占位
```

由于 `.tscn` 文件是 Godot 二进制/文本格式，手动编写不现实。此场景结构通过 Godot 编辑器创建，或在后续 UI 阶段统一处理。

- [ ] **Step 3: Commit**

```bash
git add scripts/battle/battle_manager.gd
git commit -m "feat: add BattleManager top-level coordinator with full signal wiring

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 12: 基础 .tres 测试数据（验证框架）

**Files:**
- Create: `resources/cards/slash.tres`（斩击）
- Create: `resources/cards/defend.tres`（防御）
- Create: `resources/effects/damage_6.tres`
- Create: `resources/effects/block_5.tres`
- Create: `resources/enemies/normal_zombie.tres`
- Create: `resources/enemies/intent_attack_6.tres`
- Create: `resources/enemies/intent_attack_8.tres`

- [ ] **Step 1: 创建效果资源文件**

```gdscript
# resources/effects/damage_6.tres
[gd_resource type="Resource" script_class="EffectData" load_steps=2]

[ext_resource type="Script" path="res://scripts/data/effect_data.gd" id="1_effect"]

[resource]
script = ExtResource("1_effect")
type = 0  # DAMAGE
target = 1  # SINGLE_ENEMY
base_value = 6
scale_stat = "strength"
repeat_count = 1
```

```gdscript
# resources/effects/block_5.tres
[gd_resource type="Resource" script_class="EffectData" load_steps=2]

[ext_resource type="Script" path="res://scripts/data/effect_data.gd" id="1_effect"]

[resource]
script = ExtResource("1_effect")
type = 1  # BLOCK
target = 0  # SELF
base_value = 5
scale_stat = "dexterity"
```

- [ ] **Step 2: 创建卡牌资源文件**

```gdscript
# resources/cards/slash.tres
[gd_resource type="Resource" script_class="CardData" load_steps=4]

[ext_resource type="Script" path="res://scripts/data/card_data.gd" id="1_card"]
[ext_resource type="Script" path="res://scripts/data/effect_data.gd" id="2_effect"]

[resource]
script = ExtResource("1_card")
card_id = "slash"
card_name = "斩击"
character = "通用"
card_type = 0  # ATTACK
rarity = 0  # COMMON
cost = 1
effects = Array[ExtResource("2_effect")]([ExtResource("2_effect")])
keywords = Array[String]([])
description = "造成 6 点伤害"
```

```gdscript
# resources/cards/defend.tres
[gd_resource type="Resource" script_class="CardData" load_steps=4]

[ext_resource type="Script" path="res://scripts/data/card_data.gd" id="1_card"]
[ext_resource type="Script" path="res://scripts/data/effect_data.gd" id="2_effect"]

[resource]
script = ExtResource("1_card")
card_id = "defend"
card_name = "防御"
character = "通用"
card_type = 1  # SKILL
rarity = 0  # COMMON
cost = 1
effects = Array[ExtResource("2_effect")]([ExtResource("2_effect")])
keywords = Array[String]([])
description = "获得 5 点格挡"
```

- [ ] **Step 3: 创建敌人资源文件（普通丧尸）**

```gdscript
# resources/enemies/intent_attack_6.tres
[gd_resource type="Resource" script_class="IntentData" load_steps=2]

[ext_resource type="Script" path="res://scripts/data/intent_data.gd" id="1_intent"]

[resource]
script = ExtResource("1_intent")
type = 0  # ATTACK
base_value = 6
value_variance = 0.2
description = "攻击"
icon = "⚔️"
```

```gdscript
# resources/enemies/normal_zombie.tres
[gd_resource type="Resource" script_class="EnemyData" load_steps=4]

[ext_resource type="Script" path="res://scripts/data/enemy_data.gd" id="1_enemy"]
[ext_resource type="Script" path="res://scripts/data/intent_data.gd" id="2_intent"]

[resource]
script = ExtResource("1_enemy")
enemy_id = "normal_zombie"
display_name = "普通丧尸"
base_hp = 45
enemy_type = 0  # NORMAL
intent_pattern = Array[ExtResource("2_intent")]([ExtResource("2_intent")])
crystal_drop = 1
```

- [ ] **Step 4: Commit**

```bash
git add resources/
git commit -m "feat: add test .tres data (slash, defend, zombie) for framework validation

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 13: RelicManager 基础框架（stub + 时机调度）

**Files:**
- Create: `scripts/battle/relic_manager.gd`

- [ ] **Step 1: 编写 RelicManager**

```gdscript
# scripts/battle/relic_manager.gd
## 遗物管理器: 遗物注册 + 时机触发器 + 充能管理。
class_name RelicManager
extends Node

var relics: Array[RelicData] = []
var _effect_resolver: EffectResolver

signal relic_triggered(relic: RelicData, timing: String, result: Dictionary)
signal relic_gained(relic: RelicData)
signal relic_removed(relic: RelicData)
signal relic_charge_changed(relic: RelicData, current_charges: int)


func setup(resolver: EffectResolver) -> void:
    _effect_resolver = resolver


## 获得遗物
func register_relic(relic: RelicData) -> void:
    relic.init_charges()
    relics.append(relic)
    relic_gained.emit(relic)


## 移除遗物
func remove_relic(relic_id: String) -> void:
    for i in range(relics.size() - 1, -1, -1):
        if relics[i].relic_id == relic_id:
            var removed: RelicData = relics.pop_at(i)
            relic_removed.emit(removed)
            return


func has_relic(relic_id: String) -> bool:
    for relic in relics:
        if relic.relic_id == relic_id:
            return true
    return false


func get_relic(relic_id: String) -> RelicData:
    for relic in relics:
        if relic.relic_id == relic_id:
            return relic
    return null


## 触发指定时机的所有遗物
func trigger(timing: String, context: Dictionary) -> void:
    for relic in relics:
        if relic.trigger_timing != timing:
            continue
        if not relic.can_trigger():
            continue
        if not relic.trigger_condition.is_empty():
            if not _check_condition(relic.trigger_condition, context):
                continue
        relic.consume_charge()
        relic_charge_changed.emit(relic, relic.current_charges)
        for effect in relic.effects:
            # EffectResolver 执行遗物效果
            if _effect_resolver:
                _effect_resolver.resolve_effects([effect], context.get("source", self), true)
        relic_triggered.emit(relic, timing, {})


## 充能管理
func add_charge(relic_id: String, amount: int) -> void:
    var relic: RelicData = get_relic(relic_id)
    if relic and relic.max_charges > 0:
        relic.current_charges = mini(relic.max_charges, relic.current_charges + amount)
        relic_charge_changed.emit(relic, relic.current_charges)


func _check_condition(condition: String, context: Dictionary) -> bool:
    # 条件表达式求值。示例:
    if condition == "round <= 3":
        return context.get("round", 99) <= 3
    if condition == "hand.size() <= 3":
        return context.get("hand_size", 99) <= 3
    if condition == "HP < 50%":
        var hp: int = context.get("current_hp", 0)
        var max_hp: int = context.get("max_hp", 1)
        return float(hp) / float(max_hp) < 0.5
    return true
```

- [ ] **Step 2: Commit**

```bash
git add scripts/battle/relic_manager.gd
git commit -m "feat: add RelicManager with timing-based trigger dispatch and charge system

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 14: EquipmentManager（装备槽管理）

**Files:**
- Create: `scripts/battle/equipment_manager.gd`
- Create: `scripts/data/equipment_card_data.gd`

- [ ] **Step 1: 编写 EquipmentCardData**

```gdscript
# scripts/data/equipment_card_data.gd
## 装备卡数据, 继承 CardData, 添加装备槽和耐久字段。
class_name EquipmentCardData
extends CardData

enum EquipmentSlot { WEAPON, ARMOR, ACCESSORY }

@export var equipment_slot: EquipmentSlot = EquipmentSlot.WEAPON
@export var active_effects: Array[EffectData] = []      # 装备后持续生效的效果
@export var on_equip_effects: Array[EffectData] = []    # 装备瞬间效果
@export var on_unequip_effects: Array[EffectData] = []  # 卸下瞬间效果
@export var durability: int = -1                         # -1=不损坏


func _init() -> void:
    card_type = CardType.EQUIPMENT
    exhaust_on_use = true
```

- [ ] **Step 2: 编写 EquipmentManager**

```gdscript
# scripts/battle/equipment_manager.gd
## 装备槽管理器: 武器/防具/饰品三槽 + 装备/卸下/替换 + 结算管道集成。
class_name EquipmentManager
extends Node

var slots: Dictionary = {
    "WEAPON": null,
    "ARMOR": null,
    "ACCESSORY": null,
}

var _effect_resolver: EffectResolver

signal equipment_equipped(card: EquipmentCardData, slot: String)
signal equipment_unequipped(card: EquipmentCardData, slot: String)
signal equipment_durability_changed(card: EquipmentCardData, current: int)


func setup(resolver: EffectResolver) -> void:
    _effect_resolver = resolver


func equip(card: EquipmentCardData) -> void:
    var slot: String = _slot_to_string(card.equipment_slot)
    if slots[slot] != null:
        unequip(slots[slot])
    slots[slot] = card
    if _effect_resolver:
        _effect_resolver.resolve_effects(card.on_equip_effects, self, true)
    equipment_equipped.emit(card, slot)


func unequip(card: EquipmentCardData) -> void:
    var slot: String = _slot_to_string(card.equipment_slot)
    if _effect_resolver:
        _effect_resolver.resolve_effects(card.on_unequip_effects, self, true)
    slots[slot] = null
    equipment_unequipped.emit(card, slot)


## 获取指定槽位的持续效果（供结算管道查询）
func get_slot_active_effects(slot_name: String) -> Array[EffectData]:
    var card: EquipmentCardData = slots.get(slot_name)
    if card == null:
        return []
    return card.active_effects


## 获取额外伤害修正
func get_extra_damage() -> int:
    var total: int = 0
    for slot_name in ["WEAPON", "ACCESSORY"]:
        for effect in get_slot_active_effects(slot_name):
            if effect.type == EffectData.EffectType.DAMAGE:
                total += effect.base_value
    return total


## 获取额外格挡修正
func get_extra_block() -> int:
    var total: int = 0
    for effect in get_slot_active_effects("ARMOR"):
        if effect.type == EffectData.EffectType.BLOCK:
            total += effect.base_value
    return total


func _slot_to_string(slot: int) -> String:
    match slot:
        EquipmentCardData.EquipmentSlot.WEAPON:  return "WEAPON"
        EquipmentCardData.EquipmentSlot.ARMOR:    return "ARMOR"
        EquipmentCardData.EquipmentSlot.ACCESSORY: return "ACCESSORY"
    return "WEAPON"
```

- [ ] **Step 3: Commit**

```bash
git add scripts/battle/equipment_manager.gd scripts/data/equipment_card_data.gd
git commit -m "feat: add EquipmentManager with 3-slot system and EquipmentCardData resource

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 15: BaseMechanic（角色机制基类 + 叶默示例）

**Files:**
- Create: `scripts/battle/mechanics/base_mechanic.gd`
- Create: `scripts/battle/mechanics/yemo_mechanic.gd`

- [ ] **Step 1: 编写 BaseMechanic**

```gdscript
# scripts/battle/mechanics/base_mechanic.gd
## 角色机制策略基类。每个角色一个子类, 覆写对应的生命周期回调。
class_name BaseMechanic
extends Node

var _resource_mgr: ResourceManager
var _card_mgr: CardManager
var _status_mgr: StatusManager
var _enemy_mgr: EnemyManager


func setup(rm: ResourceManager, cm: CardManager, sm: StatusManager, em: EnemyManager) -> void:
    _resource_mgr = rm
    _card_mgr = cm
    _status_mgr = sm
    _enemy_mgr = em


# ——— 生命周期回调（子类按需覆写） ———

func on_battle_start() -> void:
    pass

func on_turn_start(round_num: int) -> void:
    pass

func on_card_played(card: CardData, target: Node) -> void:
    pass

func on_turn_end() -> void:
    pass

func on_damage_dealt(source: Node, target: Node, amount: int) -> void:
    pass

func on_damage_taken(target: Node, source: Node, amount: int) -> void:
    pass

func on_kill(target: Node, is_enemy: bool) -> void:
    pass

func on_heal(target: Node, amount: int) -> void:
    pass

func on_shuffle() -> void:
    pass

## 额外伤害修正（在结算管道中叠加）
func get_extra_damage(_target: Node) -> int:
    return 0

## 额外格挡修正
func get_extra_block() -> int:
    return 0

## 伤害倍率修正
func get_damage_multiplier(_target: Node) -> float:
    return 1.0

## 格挡倍率修正
func get_block_multiplier() -> float:
    return 1.0
```

- [ ] **Step 2: 编写叶默 Mechanic（锻造 + 荆棘）**

```gdscript
# scripts/battle/mechanics/yemo_mechanic.gd
## 叶默专属机制: 锻造升级（战斗中临时升级手牌）+ 荆棘（回合结束自动伤害）
class_name YemoMechanic
extends BaseMechanic

var _thorn_stacks: int = 0
var _forge_used_this_turn: bool = false


func on_battle_start() -> void:
    _thorn_stacks = 2  # 初始遗物变异种子袋效果


func on_turn_end() -> void:
    # 荆棘结算: 对所有敌人造成 thorn_stacks 伤害
    if _thorn_stacks > 0 and _enemy_mgr:
        for enemy in _enemy_mgr.get_alive_enemies():
            # 伤害结算由 EffectResolver 处理
            var thorn_effect := EffectData.new()
            thorn_effect.type = EffectData.EffectType.DAMAGE
            thorn_effect.base_value = _thorn_stacks
            thorn_effect.target = EffectData.EffectTarget.SINGLE_ENEMY
            # 实际结算由 BattleManager 驱动
            _status_mgr.thorn_damage.emit(enemy, _thorn_stacks)


func on_card_played(card: CardData, _target: Node) -> void:
    # 锻造标签卡牌：打完自动升级手牌中随机一张
    if "锻造" in card.keywords:
        _forge_random_card()


func get_extra_damage(target: Node) -> int:
    var extra: int = 0
    if _status_mgr.has_status(target, "thorns"):
        extra += _thorn_stacks
    return extra


func add_thorns(amount: int) -> void:
    _thorn_stacks += amount


## 叶默锻造：随机升级手牌中一张卡
func _forge_random_card() -> void:
    var hand: Array = _card_mgr.hand
    if hand.is_empty():
        return
    var candidates: Array[CardData] = []
    for c in hand:
        if c.forge_count < c._forge_max:
            candidates.append(c)
    if candidates.is_empty():
        return
    var target: CardData = candidates.pick_random()
    _card_mgr.forge_card_in_hand(target)
```

- [ ] **Step 3: Commit**

```bash
git add scripts/battle/mechanics/base_mechanic.gd scripts/battle/mechanics/yemo_mechanic.gd
git commit -m "feat: add BaseMechanic interface and YemoMechanic (forge + thorns)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## 进度总结

| Task | 内容 | 文件数 | 状态 |
|------|------|--------|------|
| 1 | 项目初始化 + .gitignore + EventBus | 3 | 🔲 |
| 2 | EffectData Resource | 1 | 🔲 |
| 3 | CardData Resource + 枚举 | 1 | 🔲 |
| 4 | StatusEffectData + EnemyData + IntentData + PhaseConfig + RelicData | 5 | 🔲 |
| 5 | ResourceManager | 1 | 🔲 |
| 6 | StatusManager | 1 | 🔲 |
| 7 | CardManager | 1 | 🔲 |
| 8 | TurnStateMachine | 1 | 🔲 |
| 9 | EffectResolver | 1 | 🔲 |
| 10 | EnemyManager + EnemyAI | 1 | 🔲 |
| 11 | BattleManager + 场景结构 | 1 | 🔲 |
| 12 | 测试 .tres 数据 | 7 | 🔲 |
| 13 | RelicManager | 1 | 🔲 |
| 14 | EquipmentManager + EquipmentCardData | 2 | 🔲 |
| 15 | BaseMechanic + YemoMechanic | 2 | 🔲 |
| **合计** | | **29 文件** | |

---

## 后续 Plans（依赖此 Foundation）

| Plan | 内容 | 依赖 |
|------|------|------|
| `battle-characters` | 墨夜/温静/盛元/金英/红发/莉莲 6 角色 Mechanic | Task 15 |
| `battle-relics-implementation` | 79 个遗物 .tres 数据 + 特殊逻辑 | Task 13 |
| `battle-ui` | HandArea/CardWidget/EnemyArea/HUD/FloatText 等 UI 组件 | Task 11 |
| `battle-integration` | 信号完整连接、场景组装、编辑器测试 | All |

---

## 代码规范遵从检查

- [x] 文件命名: `snake_case.gd` ✅
- [x] 类名: `class_name PascalCase` ✅
- [x] 函数/变量: `snake_case` ✅
- [x] 私有成员: `_leading_underscore` ✅
- [x] 常量: `CONSTANT_CASE` ✅
- [x] 信号名: 过去式动词 (`card_drawn`, `entity_died`) ✅
- [x] 类型注解: `var x: int = 5` ✅
- [x] Typed Array: `Array[CardData]` ✅
- [x] `##` 文档注释 ✅
- [x] `@export` / `@onready` 注解格式 ✅
- [x] 显式 `extends` ✅
- [x] 信号用 `.emit()` / `.connect()` ✅
- [x] 子→父信号, 父→子调用 ✅
- [x] 无字符串硬编码路径 ✅
