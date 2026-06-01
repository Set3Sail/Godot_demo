# 05 - 性能优化与反模式

> 基于 Godot 官方最佳实践文档和社区验证来源整合

## 1. 性能基准：先测量，再优化

### 1.1 使用 Godot Profiler

```
编辑器 → 调试器 → 性能分析器 (Profiler)
- 帧时间 (Frame Time)
- 物理时间 (Physics Time)
- 脚本调用计数
- 信号发射计数
```

> ⚠️ **黄金法则**: 在优化前先 Profile。凭直觉优化通常浪费精力在错误的地方。

### 1.2 常见性能瓶颈优先级

1. **渲染** (draw calls, overdraw) → 使用 SpriteFrames/Atlas
2. **物理** (碰撞体数量) → 简化碰撞形状
3. **脚本** (GDScript 循环) → 减少不必要计算
4. **信号** (过度发射) → 合并/节流信号

## 2. GDScript 性能优化

### 2.1 类型注解提升性能

```gdscript
# ❌ 慢: 无类型，运行时动态类型检查
var health = 100
func process_enemies(enemies):
    for enemy in enemies:
        enemy.take_damage(10)

# ✅ 快: 使用类型注解，编译器可生成优化指令
var health: int = 100
func process_enemies(enemies: Array[Enemy]) -> void:
    for enemy: Enemy in enemies:
        enemy.take_damage(10)
```

> 📌 类型化的 GDScript 使用优化的操作码（opcodes），因为操作数/参数类型在编译时已知。官方确认 typed GDScript 性能更好。

### 2.2 使用类型化全局方法

```gdscript
# ❌ 慢: 无类型的全局方法
var x = abs(-5)
var y = floor(3.7)
var z = lerp(0, 100, 0.5)
var r = round(3.14)

# ✅ 快: 类型化的全局方法
var x: float = absf(-5.0)
var y: float = floorf(3.7)
var z: float = lerpf(0.0, 100.0, 0.5)
var r: float = roundf(3.14)
```

> 📌 类型化方法映射: `absf/absi`, `ceilf/ceili`, `clampf/clampi`, `floorf/floori`, `lerpf`, `roundf/roundi`, `signf/signi`, `snappedf/snappedi`。

### 2.3 节点属性初始化

```gdscript
# ❌ 慢: 节点加入场景树后再修改属性
func spawn_enemy() -> void:
    var enemy = enemy_scene.instantiate()
    add_child(enemy)           # 先加入树
    enemy.position = Vector2(100, 200)  # 后修改 → 触发多次通知
    enemy.health = 50

# ✅ 快: 先设置属性，再加入场景树
func spawn_enemy() -> void:
    var enemy = enemy_scene.instantiate()
    enemy.position = Vector2(100, 200)  # 先设置
    enemy.health = 50
    add_child(enemy)           # 后加入树 → 一次性通知
```

> ⚠️ **关键优化**: 在节点加入场景树**之前**修改属性。某些属性的 setter 会触发级联更新，在程序化生成等场景中这可能导致严重性能问题。

### 2.4 缓存节点引用

```gdscript
# ❌ 慢: 每帧调用 get_node / $
func _process(delta: float) -> void:
    $UI/HealthBar.value = health
    $UI/ScoreLabel.text = str(score)
    $UI/ManaBar.value = mana

# ✅ 快: 用 @onready 缓存引用
@onready var health_bar: ProgressBar = $UI/HealthBar
@onready var score_label: Label = $UI/ScoreLabel
@onready var mana_bar: ProgressBar = $UI/ManaBar

func _process(delta: float) -> void:
    health_bar.value = health
    score_label.text = str(score)
    mana_bar.value = mana
```

### 2.5 避免 _process 中的不必要计算

```gdscript
# ❌ 坏: 每帧执行不必要的计算
func _process(delta: float) -> void:
    # 每帧遍历所有敌人（即使没有变化）
    var nearest = _find_nearest_enemy()  # 昂贵的距离计算
    update_ui()  # 每帧更新 UI（即使值没变）

# ✅ 好: 只在需要时计算
var _update_interval: float = 0.1  # 100ms 间隔
var _update_timer: float = 0.0

func _process(delta: float) -> void:
    _update_timer += delta
    if _update_timer >= _update_interval:
        _update_timer = 0.0
        var nearest = _find_nearest_enemy()
        update_ui()
```

## 3. 反模式（Anti-Patterns）

### 3.1 反模式1: 巨型单例/God Object

```gdscript
# ❌ 坏: GameManager 管理一切
# GameManager.gd (Autoload)
extends Node

var player_health: int
var player_score: int
var current_level: int
var inventory: Array
var quests: Array
var settings: Dictionary
var audio_volume: float
var enemy_difficulty: float
# ... 50+ 个全局变量和函数
# 任何地方都可以读取/修改，调试极其困难

# ✅ 好: 职责分离
# PlayerData.gd (Autoload) — 只管理玩家数据
# QuestSystem.gd (Autoload) — 只管理任务
# SettingsManager.gd (Autoload) — 只管理设置
# AudioManager.gd (Autoload) — 只管理音频
```

### 3.2 反模式2: 信号链式调用

```gdscript
# ❌ 坏: A 发信号给 B, B 发信号给 C, C 发信号给 D...
func _on_button_pressed():
    emit_signal("ui_updated")  # → 触发 _on_ui_updated
func _on_ui_updated():
    emit_signal("data_changed")  # → 触发 _on_data_changed
func _on_data_changed():
    emit_signal("save_requested")  # → 触发 _on_save_requested
# 调试时无法追踪执行流

# ✅ 好: 在一个方法中完成调用链
func _on_button_pressed():
    update_ui()
    update_data()
    save_game()
```

### 3.3 反模式3: 字符串路径查询节点

```gdscript
# ❌ 坏: 硬编码节点路径 + 字符串查找
func _ready() -> void:
    var player = get_node("/root/Main/World/Level1/Player")
    var health = get_node("../../UI/HealthBar") as ProgressBar

# ❌ 更糟: 每帧都查找
func _process(delta: float) -> void:
    get_node("/root/Main/World/Player").take_damage(1)

# ✅ 好: 使用 @export 或依赖注入
@export var player: Player
@onready var health_bar: ProgressBar = $UI/HealthBar
```

### 3.4 反模式4: _ready 中做太多事

```gdscript
# ❌ 坏: _ready 中加载大文件、初始化复杂系统
func _ready() -> void:
    var data = load("res://huge_data_file.res")
    process_large_dataset(data)
    connect_to_server()
    load_all_assets()
    # ... 导致场景加载卡顿数秒

# ✅ 好: 延迟加载、分帧处理
func _ready() -> void:
    # 只做必要的初始化
    call_deferred("_lazy_init")

func _lazy_init() -> void:
    # 在第一帧空闲时加载
    var data = load("res://huge_data_file.res")
    process_data_async(data)
```

### 3.5 反模式5: 过度使用 process 模式

```gdscript
# ❌ 坏: _process 做物理相关计算
func _process(delta: float) -> void:
    velocity = calculate_physics(delta)
    move_and_slide()

# ✅ 好: 物理计算放在 _physics_process
func _physics_process(delta: float) -> void:
    velocity = calculate_physics(delta)
    move_and_slide()

# ✅ 好: 用 Timer 替代轮询
@onready var check_timer: Timer = $CheckTimer

func _ready() -> void:
    check_timer.timeout.connect(_check_condition)
    check_timer.start(0.5)  # 每 0.5 秒检查一次

func _check_condition() -> void:
    # 不需要每帧检查的条件
    pass
```

## 4. 内存管理

### 4.1 RefCounted 与手动管理

```gdscript
# Node 类型: 手动管理（queue_free）
var enemy = enemy_scene.instantiate()
add_child(enemy)
enemy.queue_free()  # 显式销毁

# RefCounted/Resource: 引用计数自动管理
var data = MyDataClass.new()
# 当没有引用指向 data 时，自动释放
data = null  # 手动断开引用以触发释放
```

### 4.2 资源释放

```gdscript
# preload 常量在脚本卸载时才释放
const HUGE_DATA = preload("res://large_file.res")
# → 无法手动释放

# 使用 load 或 @export 可以释放
var huge_data = load("res://large_file.res")
# ... 使用 ...
huge_data = null  # 引用计数归零，自动释放
```

### 4.3 子节点清理

```gdscript
# 释放节点时，其所有子节点也会被释放
var container = $EnemyContainer
for child in container.get_children():
    child.queue_free()
# 或者
container.queue_free()  # 子节点自动释放

# ⚠️ 注意: 在大批量销毁时，逐个子节点 free 可能造成性能尖峰
# 考虑使用对象池（Object Pool）模式
```

## 5. 对象池模式

```gdscript
# 简单的对象池实现
class_name ObjectPool
extends Node

@export var scene: PackedScene
@export var pool_size: int = 10

var _pool: Array[Node] = []

func _ready() -> void:
    for i in range(pool_size):
        var obj = scene.instantiate()
        obj.visible = false
        obj.process_mode = Node.PROCESS_MODE_DISABLED
        add_child(obj)
        _pool.append(obj)

func get_object() -> Node:
    if _pool.is_empty():
        var obj = scene.instantiate()
        add_child(obj)
        return obj

    var obj = _pool.pop_back()
    obj.visible = true
    obj.process_mode = Node.PROCESS_MODE_INHERIT
    return obj

func return_object(obj: Node) -> void:
    obj.visible = false
    obj.process_mode = Node.PROCESS_MODE_DISABLED
    _pool.append(obj)
```

## 6. 性能检查清单

- [ ] 为所有变量和函数参数添加类型注解
- [ ] 使用类型化全局方法（`absf`, `lerpf` 等）
- [ ] 在节点加入场景树**之前**设置属性值
- [ ] 用 `@onready` 缓存频繁访问的节点引用
- [ ] 减少 `_process` 中的计算频率（使用 Timer 或间隔计数器）
- [ ] `_process` vs `_physics_process` 各司其职
- [ ] 避免字符串硬编码路径查找节点
- [ ] 大场景使用动态加载/卸载
- [ ] 频繁创建/销毁的对象使用对象池
- [ ] 共享资源修改前 `duplicate()`
- [ ] 避免在 `_ready()` 中执行阻塞操作
- [ ] 使用 Profiler 确认瓶颈再优化

## 7. 反模式清单

| 反模式 | 问题 | 解决方案 |
|--------|------|----------|
| God Object | 单例管理一切，不可维护 | 按职责拆分为多个 Autoload |
| 信号链 | 信号触发信号，难以调试 | 在一个方法中完成调用链 |
| 字符串路径 | 脆弱的节点引用 | @export / @onready / 依赖注入 |
| 繁忙 _ready | 场景加载卡顿 | call_deferred / 分帧加载 |
| 无类型代码 | 运行时性能差 | 添加类型注解 |
| 预加载一切 | 启动时大量内存占用 | 按需 load / 动态管理 |
| process 做物理 | 物理不稳定 | 移到 _physics_process |
| 修改共享资源 | 多个对象受影响 | duplicate() |
| 忽略 Profiler | 盲目优化 | 先 profile 再优化 |
