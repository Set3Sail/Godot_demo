# 轮盘世界 · Godot 4.x 场景搭建指南

> **前置条件:** 项目已 clone，所有脚本和资源文件就位
> **目标:** 在 Godot 编辑器中搭建可运行的 BattleScene

---

## 目录

1. [打开项目](#1-打开项目)
2. [确认 Autoload](#2-确认-autoload)
3. [创建 BattleScene](#3-创建-battlescene)
4. [搭建 BattleManager 子节点](#4-搭建-battlemanager-子节点)
5. [搭建 UI 占位节点](#5-搭建-ui-占位节点)
6. [节点树总览](#6-节点树总览)
7. [验证脚本挂载](#7-验证脚本挂载)
8. [首次运行测试](#8-首次运行测试)
9. [后续开发路线](#9-后续开发路线)

---

## 1. 打开项目

```bash
# 启动 Godot 4.x 编辑器
godot --path /home/fangqihang2/claude-task/my_game_coding &
```

或通过 Godot 项目管理器：点击 **导入** → 选择 `project.godot` 文件。

打开后应看到文件系统面板中所有 `scripts/` 和 `resources/` 目录。

## 2. 确认 Autoload

菜单: **项目 → 项目设置 → Autoload** 标签页

确认 `EventBus` 已配置：

| 名称 | 路径 |
|------|------|
| EventBus | `*res://scripts/autoload/event_bus.gd` |

`*` 前缀表示全局可访问。点击 EventBus 行确认 Enable 已勾选。

## 3. 创建 BattleScene

1. 在文件系统面板右键 `scenes/battle/` → **新建场景**
2. 根节点选择: **Node** (通用节点)
3. 右键根节点 → **重命名** 为 `BattleScene`
4. 保存场景: `scenes/battle/battle_scene.tscn`（与 project.godot 中 `run/main_scene` 一致）

## 4. 搭建 BattleManager 子节点

### 4.1 创建 BattleManager

1. 右键 `BattleScene` → **添加子节点** → 搜索 `Node` → 创建
2. 重命名为 `BattleManager`
3. 在检查器面板中，点击脚本图标 → **快速加载** → 选择 `scripts/battle/battle_manager.gd`

### 4.2 创建核心管理器子节点

在 `BattleManager` 下依次添加以下子节点，每个都挂载对应脚本：

| 节点名 | 脚本文件 | 类型 |
|--------|----------|------|
| `TurnStateMachine` | `scripts/battle/turn_state_machine.gd` | Node |
| `CardManager` | `scripts/battle/card_manager.gd` | Node |
| `ResourceManager` | `scripts/battle/resource_manager.gd` | Node |
| `StatusManager` | `scripts/battle/status_manager.gd` | Node |
| `EffectResolver` | `scripts/battle/effect_resolver.gd` | Node |
| `EnemyManager` | `scripts/battle/enemy_manager.gd` | Node |
| `RelicManager` | `scripts/battle/relic_manager.gd` | Node |
| `EquipmentManager` | `scripts/battle/equipment_manager.gd` | Node |
| `CharacterMechanics` | *(空 Node，运行时动态加载 Mechanic)* | Node |

**操作步骤（每个节点重复）：**
1. 右键 `BattleManager` → **添加子节点** → 选 `Node`
2. 在场景树中双击节点名 → 重命名为上表名称
3. 在检查器中点击 `<空>` 脚本栏 → **快速加载** → 选对应 .gd 文件

**CharacterMechanics 特殊处理：**
- 不挂载脚本，作为空容器
- 运行时由 BattleManager 根据当前角色动态实例化 Mechanic 并 add_child

### 4.3 验证 @onready 路径

脚本中的 `@onready var _turn_sm: TurnStateMachine = $TurnStateMachine` 依赖节点名完全匹配。确保子节点名与 `$NodeName` 中的 `NodeName` 一致。

## 5. 搭建 UI 占位节点

在 `BattleScene` 根下（与 `BattleManager` 平级），添加 UI 区域：

### 5.1 HUD 区

```
右键 BattleScene → 添加子节点 → Control → 重命名 HUD
```

HUD 子节点（初步骨架，后续由 UI Plan 实现）：

| 节点 | 类型 | 位置 |
|------|------|------|
| `TopBar` | Control | 顶部 |
| `StatusPanel` | Control | 右侧 |

### 5.2 PlayerArea（手牌区）

```
右键 BattleScene → 添加子节点 → Control → 重命名 PlayerArea
```

子节点：
| 节点 | 类型 | 说明 |
|------|------|------|
| `HandArea` | HBoxContainer | 卡牌水平排列容器 |

### 5.3 EnemyArea（敌人区）

```
右键 BattleScene → 添加子节点 → Control → 重命名 EnemyArea
```

子节点：
| 节点 | 类型 | 说明 |
|------|------|------|
| `EnemySlots` | HBoxContainer | 敌人 slot 水平排列 |
| `AllySlots` | HBoxContainer | 友方随从 slot |

### 5.4 EffectsLayer（特效层）

```
右键 BattleScene → 添加子节点 → Control → 重命名 EffectsLayer
```

此层用于 FloatText 飘字和粒子特效，渲染在所有 UI 之上。

**关键设置：**
- Mouse → Filter: **Ignore**（让点击穿透到下方卡片/敌人）

## 6. 节点树总览

完成后场景树应为：

```
BattleScene (Node)                              ← battle_scene.tscn
├── BattleManager (Node)                        ← battle_manager.gd
│   ├── TurnStateMachine (Node)                 ← turn_state_machine.gd
│   ├── CardManager (Node)                      ← card_manager.gd
│   ├── ResourceManager (Node)                  ← resource_manager.gd
│   ├── StatusManager (Node)                    ← status_manager.gd
│   ├── EffectResolver (Node)                   ← effect_resolver.gd
│   ├── EnemyManager (Node)                     ← enemy_manager.gd
│   ├── RelicManager (Node)                     ← relic_manager.gd
│   ├── EquipmentManager (Node)                 ← equipment_manager.gd
│   └── CharacterMechanics (Node)               ← (空容器)
├── HUD (Control)
│   ├── TopBar (Control)
│   └── StatusPanel (Control)
├── PlayerArea (Control)
│   └── HandArea (HBoxContainer)
├── EnemyArea (Control)
│   ├── EnemySlots (HBoxContainer)
│   └── AllySlots (HBoxContainer)
└── EffectsLayer (Control)
```

### 在 EnemyArea 中添加 Player 标记

右键 `BattleScene` → **添加子节点** → Node → 重命名为 `Player`
在检查器中: **组** 标签 → 输入 `player` → 点击 **添加**

这确保 `get_tree().get_first_node_in_group("player")` 能正常工作。

## 7. 验证脚本挂载

场景搭建完成后，逐个检查：

### 7.1 脚本语法检查

打开任意 .gd 文件 → 查看脚本编辑器底部的错误面板：
- ✅ 无红色错误 = 类名引用正确
- ❌ 出现 `Could not find type` = 对应 class_name 脚本未正确加载。尝试关闭重开编辑器。

### 7.2 场景依赖检查

Godot 会自动检查 `@export` 和 `@onready` 引用：

1. 选中 `BattleManager` 节点
2. 在场景树中查看其子节点是否正确显示
3. 检查器面板中 `@onready` 变量应显示节点引用

### 7.3 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `$TurnStateMachine` 为 null | 子节点名不匹配 | 确认子节点名与脚本 `@onready var _xxx = $Name` 一致 |
| class_name 无法识别 | 脚本未加载 | 重新打开项目，确保所有 .gd 在 res:// 下 |
| BattleManager._ready 报错 | 子节点缺少脚本 | 检查所有子节点均已挂载对应 .gd |

## 8. 首次运行测试

### 8.1 创建测试脚本

在 `BattleScene` 根节点上挂载一个临时测试脚本 `scenes/battle/battle_test.gd`：

```gdscript
# scenes/battle/battle_test.gd
extends Node

@onready var battle_mgr: BattleManager = $BattleManager


func _ready() -> void:
    # 等待一帧让所有 _ready 完成
    await get_tree().process_frame

    # 加载测试数据
    var slash: CardData = load("res://resources/cards/slash.tres")
    var defend: CardData = load("res://resources/cards/defend.tres")
    var deck: Array[CardData] = [slash, slash, slash, slash, slash, defend, defend, defend, defend, defend, slash, defend]

    var zombie: EnemyData = load("res://resources/enemies/normal_zombie.tres")
    var enemies: Array[EnemyData] = [zombie]

    # 启动战斗
    battle_mgr.start_battle(75, 75, deck, enemies)
    print("Battle started! Round: ", battle_mgr._turn_sm.round_number)
```

### 8.2 运行

按 **F5** 或点击右上角 **播放** 按钮。

预期输出（控制台）:
```
Battle started! Round: 1
```

如果报错，检查错误信息定位问题节点。

### 8.3 战斗流程验证

在 `battle_test.gd` 的 `_ready` 末尾添加自动化测试：

```gdscript
    # 等待回合开始
    await get_tree().create_timer(0.5).timeout

    # 验证手牌
    var hand_size: int = battle_mgr._card_mgr.get_hand_size()
    print("Hand size: ", hand_size, " (expected 5)")

    # 打出第一张卡
    var card: CardData = battle_mgr._card_mgr.hand[0]
    var target: Node = battle_mgr._enemy_mgr.get_frontmost_enemy()
    if target:
        battle_mgr.play_card(card, target)
        print("Played: ", card.card_name, " -> Enemy HP: ", battle_mgr._resource_mgr.get_enemy_hp(target))

    # 结束回合
    battle_mgr._turn_sm.request_end_turn()
    await get_tree().create_timer(1.0).timeout
    print("Turn ended. New round: ", battle_mgr._turn_sm.round_number)
```

预期: 手牌=5、打出斩击后面板显示、回合结束后进入新回合。

## 9. 后续开发路线

| 步骤 | 内容 | 说明 |
|------|------|------|
| 1 | 完成场景搭建 | 本文档 §1-§8 |
| 2 | 实现 HandArea UI | 卡牌渲染 + 点击交互 + 拖拽 |
| 3 | 实现 EnemyArea UI | 敌人血条 + 意图图标 + 状态图标 |
| 4 | 实现 HUD | HP/精神力/格挡/魔晶/回合数显示 |
| 5 | 实现 FloatText | 伤害/格挡/治疗飘字 |
| 6 | 信号对接 | BattleManager ↔ UI 层信号连接 |
| 7 | 实现奖励界面 | 选卡 + 遗物掉落 |
| 8 | 实现死亡界面 | 重开/返回菜单 |
| 9 | 地图层 | MapLevel 场景 + 节点导航 |
| 10 | 局外系统 | 主菜单 + 角色选择 + 存档 |
