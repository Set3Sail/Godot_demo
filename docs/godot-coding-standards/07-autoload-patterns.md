# 07 - Autoload 与单例模式

> 基于 Godot 官方单例/Autoload 文档和 Autoload vs Internal Nodes 最佳实践

## 1. Autoload 基础

### 1.1 什么是 Autoload

Autoload 是在项目启动时自动加载到场景树根节点的节点或脚本。它们在整个游戏生命周期中持续存在，不随场景切换而销毁。

```
场景树根节点:
Root (Viewport)
├── GameManager       ← Autoload（始终存在）
├── AudioManager      ← Autoload（始终存在）
├── EventBus          ← Autoload（始终存在）
└── CurrentScene      ← 最后一个子节点 = 当前加载的场景
    ├── World
    └── UI
```

> 📌 **关键属性**: Autoload 节点始终在根视口的 children 列表中排在已加载场景**之前**。最后一个孩子始终是当前活跃场景。

### 1.2 配置 Autoload

```
项目 → 项目设置 → Autoload 标签页
1. 在 Path 中选择 .gd 脚本或 .tscn 场景
2. 在 Name 中输入节点名称（成为访问键）
3. 勾选 Enable 以允许全局直接访问
4. 点击 Add
```

```gdscript
# 如果节点名为 "GameManager" 且 Enable 勾选:
GameManager.start_game()         # 直接通过名称访问
var gm = get_node("/root/GameManager")  # 或通过路径

# 如果 Enable 不勾选:
var gm = get_node("/root/GameManager")  # 只能通过路径访问
```

### 1.3 Autoload 脚本 vs Autoload 场景

```gdscript
# Autoload 脚本: 引擎自动创建 Node 并附加脚本
# global.gd
extends Node

func do_something() -> void:
    pass

# Autoload 场景: 直接加载整个场景
# audio_manager.tscn (可能包含 AudioStreamPlayer 子节点)
# AudioManager → AudioStreamPlayer (BGM)
#             → AudioStreamPlayer (SFX)
```

## 2. Autoload 适用场景

### 2.1 推荐使用 Autoload 的情况

```gdscript
# ✅ 1. 跨场景持久数据
# PlayerData.gd
extends Node

var health: int = 100
var score: int = 0
var current_level: int = 1
var inventory: Array[ItemData] = []

# ✅ 2. 场景管理与转场
# SceneManager.gd
extends Node

func switch_scene(scene_path: String) -> void:
    # 使用 call_deferred 避免在信号回调中删除当前场景
    call_deferred("_deferred_switch", scene_path)

func _deferred_switch(scene_path: String) -> void:
    get_tree().change_scene_to_file(scene_path)

# ✅ 3. 事件总线（谨慎使用）
# EventBus.gd
extends Node

signal player_died
signal score_changed(new_score: int)
signal level_completed(level_num: int)

# ✅ 4. 宽域系统（管理自己数据、不侵入其他对象）
# QuestSystem.gd
extends Node

var active_quests: Array[Quest] = []
var completed_quests: Array[Quest] = []

func accept_quest(quest_id: String) -> void:
    pass

func complete_quest(quest_id: String) -> void:
    pass

# ✅ 5. 对话系统
# DialogManager.gd
extends Node

func show_dialog(dialog_resource: DialogResource) -> void:
    pass
```

### 2.2 不推荐使用 Autoload 的情况

```gdscript
# ❌ 只有一个场景需要的数据
# 如果某个数据仅在战斗场景中使用，不应放入 Autoload

# ❌ 需要随场景卸载的数据
# 战斗结束应该清理的战斗状态数据

# ❌ 可以用静态方法替代的工具函数
# 无需状态管理的纯函数应该用 static func

# ❌ 可以用场景内节点实现的功能
# 如果功能只在当前场景内使用，用普通子节点即可
```

## 3. Autoload 的重要注意事项

### 3.1 不是真正的单例

```gdscript
# ⚠️ Godot 不会保证 Autoload 是"唯一"实例
# 你仍然可以手动实例化
var another_manager = GameManager.new()  # 是允许的！
add_child(another_manager)

# 不要依赖"只有一个实例"的假设来设计架构
```

> 官方原话: "Godot won't make an Autoload a 'true' singleton as per the singleton design pattern. It may still be instanced more than once by the user if desired."

### 3.2 不允许释放

```gdscript
# ❌ 绝对不允许！
GameManager.free()        # 引擎崩溃！
GameManager.queue_free()  # 引擎崩溃！

# Autoload 的生命周期 = 应用程序的生命周期
```

### 3.3 场景切换时的安全问题

```gdscript
# ❌ 危险: 在信号回调中直接 free 当前场景
func _on_start_button_pressed() -> void:
    get_tree().current_scene.free()  # 当前场景可能还在执行代码！
    var new_scene = load("res://scenes/game.tscn").instantiate()
    get_tree().root.add_child(new_scene)

# ✅ 安全: 使用 call_deferred
func _on_start_button_pressed() -> void:
    call_deferred("_switch_to_game")

func _switch_to_game() -> void:
    # 此时当前场景的代码已执行完毕
    get_tree().change_scene_to_file("res://scenes/game.tscn")
```

### 3.4 编写场景切换器

```gdscript
# SceneManager.gd (Autoload)
extends Node

func goto_scene(scene_path: String) -> void:
    # 一定使用 call_deferred
    call_deferred("_deferred_goto_scene", scene_path)

func _deferred_goto_scene(scene_path: String) -> void:
    # 显示加载画面（如果加载时间 < 3秒）
    # 可以在这里添加加载指示器

    # 释放当前场景
    get_tree().current_scene.free()

    # 加载新场景
    var new_scene_resource = load(scene_path)
    var new_scene = new_scene_resource.instantiate()

    # 添加到根节点
    get_tree().root.add_child(new_scene)

    # 设为当前场景（可选，保持 API 兼容性）
    get_tree().current_scene = new_scene

func get_current_scene() -> Node:
    var root = get_tree().root
    return root.get_child(root.get_child_count() - 1)
```

## 4. Autoload vs 场景内节点 vs 静态方法

### 4.1 对比

| 特性 | Autoload | 场景内节点 | static func/var |
|------|----------|-----------|-----------------|
| **生命周期** | 整个应用 | 场景存活期间 | 脚本级别 |
| **访问范围** | 全局 | 场景树内 | 全局（通过类名） |
| **场景切换** | 不销毁 | 随场景销毁 | 不销毁 |
| **可发信号** | ✅ | ✅ | ❌ |
| **可引用实例** | ✅（self） | ✅（self） | ❌ |
| **调试难度** | 较高（全局可见） | 低（局部作用域） | 中等 |
| **耦合度** | 高 | 低 | 低 |
| **内存占用** | 始终存在 | 按需存在 | 无实例 |

### 4.2 使用 static func 替代 Autoload

```gdscript
# math_utils.gd (不需要是 Autoload)
class_name MathUtils
extends RefCounted

static func lerp_angle(from: float, to: float, weight: float) -> float:
    var diff = fmod(to - from, TAU)
    var shortest = fmod(2.0 * diff, TAU) - diff
    return from + shortest * weight

static func approach(current: float, target: float, delta: float) -> float:
    if current < target:
        return min(current + delta, target)
    return max(current - delta, target)

# 使用: 无需实例化
var new_angle = MathUtils.lerp_angle(0.0, PI, 0.5)

# ⚠️ 限制: static func 不能访问成员变量、非静态方法、或 self
```

> 📌 Godot 4.1+ 支持 `static var`，可在不创建 Autoload 的情况下存储共享数据。

## 5. Autoload 最佳实践

### 5.1 职责单一

```gdscript
# ✅ 好: 每个 Autoload 职责单一
# AudioManager 只管音频
# SaveManager 只管存档
# SceneManager 只管场景切换

# ❌ 坏: God Object
# GameManager 管理一切 → 反模式
```

### 5.2 命名约定

```gdscript
# 推荐命名方式:
# - PascalCase（Godot 标准）
# - 描述性名称，能体现其职责

GameManager
AudioManager  
SceneManager
EventBus
PlayerData
QuestSystem
SaveManager
```

### 5.3 加载顺序管理

```gdscript
# Autoload 标签页中的顺序 = 加载顺序（从上到下）
# 1. EventBus       ← 最基础，不依赖其他
# 2. SaveManager    ← 不依赖其他
# 3. PlayerData     ← 可能依赖 SaveManager
# 4. GameManager    ← 可能依赖以上所有

# 在代码中，后加载的 Autoload 可以在 _ready 中安全访问先加载的：
# GameManager.gd
func _ready() -> void:
    # 安全: EventBus, SaveManager, PlayerData 的 _ready 已完成
    EventBus.game_started.connect(_on_game_started)
    player_data = PlayerData.get_data()
```

### 5.4 使用配置警告

```gdscript
# QuestSystem.gd (Autoload)
extends Node

@export var quest_data_path: String = ""

func _get_configuration_warnings() -> PackedStringArray:
    var warnings := PackedStringArray()
    if quest_data_path.is_empty():
        warnings.append("QuestSystem 需要设置 quest_data_path")
    return warnings
```

## 6. Autoload 的反模式

### 6.1 全局变量垃圾桶

```gdscript
# ❌ 坏: 用 Autoload 存储各种杂项全局变量
# Global.gd
extends Node

var player_health: int
var score: int
var current_level: int
var audio_volume: float
var screen_shake_intensity: float
var camera_offset: Vector2
var dialogue_speed: float
var particle_quality: int
var enemy_count: int
# ... 30+ 个不相关的变量

# ✅ 好: 按职责拆分
# PlayerStats.gd — 角色相关
# GameSettings.gd — 设置相关
# LevelData.gd — 关卡相关
```

### 6.2 循环依赖

```gdscript
# ❌ 坏: Autoload A 引用 Autoload B，B 也引用 A

# GameManager.gd
func _ready() -> void:
    AudioManager.set_game_manager(self)  # A → B

# AudioManager.gd  
func _ready() -> void:
    GameManager.register_audio(self)     # B → A

# ✅ 好: 单向依赖，通过信号解耦
# GameManager.gd
func _ready() -> void:
    game_started.connect(AudioManager._on_game_started)

# AudioManager.gd
func _on_game_started() -> void:
    play_bgm("game_theme")
```

### 6.3 过度使用事件总线

```gdscript
# ❌ 坏: 所有通信都通过 EventBus
EventBus.enemy_damaged.emit(data)
EventBus.ui_needs_update.emit()
EventBus.player_moved.emit(pos)
EventBus.item_picked_up.emit(item)
EventBus.door_opened.emit(door_id)
# ... 50+ 个信号，任何地方都能发射和监听

# ✅ 好: 本地通信用直接信号
# 只在真正需要跨层级通信时使用事件总线
```

## 7. 决策树：用 Autoload 还是场景内节点？

```
这个功能/数据需要跨多个场景存在？

    ├── 否 → 使用场景内节点
    │
    └── 是 → 需要全局访问？
        │
        ├── 否 → 可以通过场景参数传递？ → 传参（不用 Autoload）
        │
        ├── 是 → 需要存储状态？
        │   │
        │   ├── 否 → 需要信号通知？ → EventBus Autoload
        │   └── 是 → 数据量大且变化频繁？ → Autoload
        │
        └── 可以用 static func/var 实现？
            ├── 是 → 使用 static（轻量，无全局状态）
            └── 否 → 使用 Autoload
```

## 8. Autoload 检查清单

- [ ] Autoload 按依赖关系排序（先加载的不依赖后加载的）
- [ ] 每个 Autoload 职责单一
- [ ] Autoload 命名使用 PascalCase，名称描述职责
- [ ] 不在 Autoload 中存储只属于一个场景的数据
- [ ] 不使用 `free()` 或 `queue_free()` 销毁 Autoload
- [ ] 场景切换使用 `call_deferred`
- [ ] 考虑过使用 `static func`/`static var` 替代
- [ ] 避免 Autoload 之间的循环依赖
- [ ] 事件总线信号数量可控，不过度使用
- [ ] 使用 `_get_configuration_warnings()` 暴露配置问题
