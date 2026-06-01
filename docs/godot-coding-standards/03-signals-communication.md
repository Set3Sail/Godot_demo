# 03 - 信号与通信模式

> 基于 Godot 官方信号文档 — 对抗性验证通过 (3-0)

## 1. 信号基础

### 1.1 信号 = 观察者模式

Godot 信号实现了**观察者模式**，允许节点之间解耦通信：

> 官方定义: "Signals are Godot's version of the observer pattern. They allow a game object to react to a change in another without them referencing one another."

```gdscript
# 声明信号
signal health_changed(new_health: int)
signal door_opened
signal item_collected(item_type: String, quantity: int)

# 发射信号
func take_damage(amount: int) -> void:
    health -= amount
    health_changed.emit(health)  # 通知所有观察者

# 连接信号
func _ready() -> void:
    player.health_changed.connect(_on_health_changed)

func _on_health_changed(new_health: int) -> void:
    health_bar.value = new_health
```

### 1.2 Godot 4.x 信号语法（重要变化）

```gdscript
# Godot 3.x (已废弃)
signal my_signal()
emit_signal("my_signal")
connect("my_signal", self, "_on_my_signal")

# Godot 4.x (新语法)
signal my_signal
my_signal.emit()
my_signal.connect(_on_my_signal)
```

> ⚠️ Godot 4.x 中，信号是 `Signal` 类型的对象，使用 `.emit()` 和 `.connect()` 方法。

## 2. 信号命名规范

### 2.1 强制规则：过去式动词

```gdscript
# ✅ 正确：描述已发生的事件
signal player_died
signal door_opened
signal health_changed(new_value: int)
signal item_collected(item: Item)
signal level_completed
signal animation_finished
signal button_pressed        # 引擎自带信号的标准命名

# ❌ 错误：描述正在发生或将要发生的事件
signal player_die            # 现在时
signal door_open             # 现在时
signal health_change(...)    # 名词
signal on_health_changed(...) # on_ 前缀
signal collect_item(...)     # 动词原形（命令式）
```

### 2.2 信号参数

```gdscript
# 无参数信号
signal game_over

# 带参数信号（类型提示推荐）
signal health_changed(new_health: int)
signal damage_taken(amount: float, source: Node)
signal item_collected(item_data: Dictionary)

# 旧风格（仍可用但不推荐）
signal health_changed(new_health)
```

## 3. 连接信号的方式

### 3.1 代码连接

```gdscript
# 方式1: 显式 connect
func _ready() -> void:
    $Timer.timeout.connect(_on_timer_timeout)
    player.health_changed.connect(_on_health_changed)

func _on_timer_timeout() -> void:
    pass

func _on_health_changed(new_health: int) -> void:
    pass

# 方式2: connect 带绑定参数
func _ready() -> void:
    $Button.pressed.connect(_on_button_pressed.bind("start_game"))

func _on_button_pressed(action: String) -> void:
    match action:
        "start_game":
            start_game()

# 方式3: 匿名函数（lambda）
func _ready() -> void:
    $Button.pressed.connect(func():
        print("按钮被点击了")
        start_game()
    )
```

### 3.2 编辑器连接（推荐用于静态连接）

在编辑器中：
1. 选择发送信号的节点
2. 切换到"节点"（Node）面板 → "信号"（Signals）选项卡
3. 双击目标信号
4. 选择接收节点和方法

> 📌 编辑器连接的优势：无需手动写 `connect` 代码，减少内存泄漏风险。

### 3.3 何时用代码连接 vs 编辑器连接

| 场景 | 编辑器连接 | 代码连接 |
|------|:--------:|:------:|
| 静态场景内节点连接 | ✅ 推荐 | ❌ |
| 动态生成的节点 | ❌ | ✅ 唯一方式 |
| 跨场景连接 | ❌ | ✅ 唯一方式 |
| 条件性连接 | ❌ | ✅ 唯一方式 |
| UI 信号到逻辑 | ✅ 推荐 | 可用 |

## 4. 断开信号

### 4.1 手动断开

```gdscript
# 断开特定连接
player.health_changed.disconnect(_on_health_changed)

# 断开所有连接
player.health_changed.disconnect_all()
```

### 4.2 自动断开

```gdscript
# 当节点被释放时，其信号连接自动断开
enemy.queue_free()  # 所有与该 enemy 的信号连接自动清理
```

> ⚠️ **注意**: 但如果监听者是 `RefCounted` 对象（非 `Node`），且发送者持有对监听者的引用，则监听者不会自动销毁。这种情况下需要手动断开。

## 5. 信号通信模式

### 5.1 模式1: 子→父 通知（最常用）

```gdscript
# Child.gd
extends Area2D
signal item_collected(item_data: Dictionary)

func _on_body_entered(body: Node2D) -> void:
    item_collected.emit({"type": "coin", "value": 10})
    queue_free()

# Parent.gd
extends Node2D

func _ready() -> void:
    # 对所有动态生成的子节点统一连接
    for child in get_children():
        if child is Area2D:
            child.item_collected.connect(_on_item_collected)

func _on_item_collected(data: Dictionary) -> void:
    score += data.value
```

### 5.2 模式2: 跨层级通信（事件总线）

```gdscript
# EventBus.gd (Autoload)
extends Node

signal player_died
signal score_changed(new_score: int)
signal game_state_changed(new_state: String)

# 任何地方都可以发射
# Enemy.gd
func _on_player_detected() -> void:
    EventBus.game_state_changed.emit("alert")

# 任何地方都可以监听
# HUD.gd
func _ready() -> void:
    EventBus.score_changed.connect(_on_score_changed)

func _on_score_changed(new_score: int) -> void:
    score_label.text = str(new_score)
```

> ⚠️ **事件总线风险**: 全局信号让调试变得困难——任何地方都可能发射或监听。仅在确实需要跨层级通信时使用，不要滥用。

### 5.3 模式3: 组件间通信

```gdscript
# HealthComponent.gd
class_name HealthComponent
extends Node

signal health_changed(new_health: float)
signal health_depleted

@export var max_health: float = 100.0
var current_health: float = max_health

func take_damage(amount: float) -> void:
    current_health = max(0, current_health - amount)
    health_changed.emit(current_health)

    if current_health <= 0:
        health_depleted.emit()

# 使用 HealthComponent 的场景
# Player.gd
@onready var health_component: HealthComponent = $HealthComponent

func _ready() -> void:
    health_component.health_changed.connect(_update_health_bar)
    health_component.health_depleted.connect(_die)
```

### 5.4 模式4: 信号链（Signal Chain）

```gdscript
# 信号可以在节点间传递，形成链式通知
# HealthComponent → Player → World → SaveSystem

# HealthComponent.gd
signal health_depleted

# Player.gd
@onready var health_component: HealthComponent = $HealthComponent
signal player_died

func _ready() -> void:
    health_component.health_depleted.connect(func():
        player_died.emit()
    )

# World.gd
signal game_over

func _on_player_died() -> void:
    game_over.emit()
```

## 6. 信号 vs 直接调用：决策树

```
你需要让一个对象通知另一个对象某事件发生了？

    ├── 调用方是父节点，被调用方是子节点？
    │   └── → 直接调用（父调用子方法）
    │
    ├── 调用方是子节点，被调用方是父节点？
    │   └── → 使用信号（子发信号通知父）
    │
    ├── 两个节点在不同分支中，没有直接的父子关系？
    │   └── → 使用信号（或通过共同祖先转发）
    │
    ├── 一个事件需要通知多个监听者？
    │   └── → 使用信号（一对多广播）
    │
    ├── 需要返回值？
    │   └── → 直接调用（信号不支持返回值）
    │
    └── 只是查询状态（非事件通知）？
        └── → 直接调用
```

## 7. 信号最佳实践清单

- [ ] 信号名使用过去式动词（`door_opened`, `health_changed`）
- [ ] 信号声明添加参数类型提示
- [ ] 子→父通信用信号，父→子通信用直接调用
- [ ] 跨层级通信优先考虑通过共同祖先转发，而非直接使用事件总线
- [ ] 动态创建的节点在 `_ready()` 中连接信号
- [ ] 节点销毁前无需手动断开（引擎自动处理 Node 类型）
- [ ] 如果使用 RefCounted 对象作为信号监听者，确保断开连接
- [ ] 避免在信号回调中执行耗时操作
- [ ] 复杂信号参数使用自定义 Resource 类型而非 Dictionary

## 8. 常见错误

### 8.1 信号名不规范

```gdscript
# ❌
signal on_click
signal update_ui

# ✅
signal button_clicked
signal ui_needs_update
```

### 8.2 信号回调中直接删除节点

```gdscript
# ❌ 危险: 在信号回调中直接 free 当前场景
func _on_button_pressed() -> void:
    get_tree().current_scene.free()  # 可能崩溃！

# ✅ 安全: 使用 call_deferred
func _on_button_pressed() -> void:
    call_deferred("_switch_scene")

func _switch_scene() -> void:
    get_tree().change_scene_to_file("res://scenes/game.tscn")
```
