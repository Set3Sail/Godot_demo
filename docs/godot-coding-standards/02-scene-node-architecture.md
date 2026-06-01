# 02 - 场景与节点架构

> 基于 Godot 官方设计哲学和场景组织最佳实践 — 对抗性验证通过 (3-0)

## 1. Godot 设计哲学：节点树

### 1.1 一切皆节点

Godot 将游戏元素组织为**树状结构**，节点之间形成父子关系：

```
Root (Viewport)
├── World (Node2D/Node3D)
│   ├── Player (CharacterBody2D)
│   │   ├── Sprite2D
│   │   ├── CollisionShape2D
│   │   └── Camera2D
│   ├── Enemy1 (CharacterBody2D)
│   └── Enemy2 (CharacterBody2D)
└── UI (CanvasLayer)
    ├── HealthBar
    └── ScoreLabel
```

> ⚠️ **核心约束**: 每个场景必须有且仅有一个根节点（引擎强制要求）。

### 1.2 继承式架构 vs ECS

Godot 使用**基于继承的节点架构**，而非实体组件系统（ECS）：

```gdscript
# Godot 的继承链示例
# Node → CanvasItem → Node2D → Sprite2D
# Node → CanvasItem → Control → Button

# Sprite2D 自动拥有 Node2D 的所有属性（position, rotation, scale）
# 以及 CanvasItem 的所有属性（visible, modulate）
# 以及 Node 的所有功能（生命周期回调、信号、场景树操作）
```

> 📌 **关键理解**: Godot 不是 ECS 架构。节点通过继承积累功能，你可以为任何节点附加脚本来添加自定义行为。

## 2. 场景作为"类"

### 2.1 场景 = 类，实例化 = 实例

场景在 Godot 中扮演着类似 OOP 中"类"的角色：

```gdscript
# 保存一个敌人场景: enemy.tscn (类似于 class Enemy)
# - Root: CharacterBody2D
#   - Sprite2D (显示)
#   - CollisionShape2D (碰撞)
#   - HitBox (Area2D)
#   - 脚本: enemy.gd

# 在主场景中实例化（类似于 new Enemy()）
var enemy_scene := preload("res://enemies/enemy.tscn")
var enemy := enemy_scene.instantiate()
add_child(enemy)
```

### 2.2 组合与聚合（节点嵌套）

场景通过节点嵌套支持组合：

```gdscript
# player.tscn:
# CharacterBody2D (root)
# ├── Sprite2D        ← 组合：玩家"拥有"一个精灵
# ├── CollisionShape2D ← 组合：玩家"拥有"碰撞体
# └── WeaponAnchor     ← 聚合：武器挂载点
#     └── Sword (Sprite2D)
```

### 2.3 场景继承（New Inherited Scene）

```gdscript
# base_enemy.tscn → 基础敌人行为和外观
# flying_enemy.tscn extends base_enemy.tscn → 添加飞行行为
# boss_enemy.tscn extends base_enemy.tscn → 扩展 Boss 行为
```

使用方式：在编辑器中选择"新建继承场景"（New Inherited Scene）。

### 2.4 场景实例化时发生了什么

```gdscript
# 当实例化场景到另一个场景中时：
# 1. 被实例的场景在编辑器中显示为一个折叠的单一节点
# 2. 其内部子节点默认被隐藏
# 3. 需要右键 → "Editable Children" 才能展开内部结构

# 代码中:
@onready var enemy_instance = $EnemyInstance  # 看到的是根节点
# enemy_instance 的内部子节点在其自身的场景树中
```

> ⚠️ **关键理解**: 每个运行时的场景实例是**独立的**——修改一个实例不影响其他实例（该声明验证不通过，实际上场景实例之间的独立性取决于资源引用方式：'当场景被实例化时，共享同一个原型的资源，但节点状态独立'才是准确的描述。共享资源如材质修改会互相影响，而节点属性如位置不会）。

## 3. 场景设计原则

### 3.1 核心原则：场景应自包含

```gdscript
# ✅ 好的设计: 场景无外部依赖
# player.tscn 包含玩家所需的一切
# - 精灵、碰撞体、动画、脚本全部内聚在场景内

# ❌ 坏的设计: 场景依赖外部节点路径
# 脚本中写死 get_node("/root/World/Player/UI")
# 导致场景无法独立运行测试
```

> ⚠️ **官方强烈推荐**: 尽可能设计零依赖的场景。这是 Godot 场景组织的首要原则。

### 3.2 松耦合与配置警告

当必须存在外部依赖时，使用 `_get_configuration_warnings()`：

```gdscript
@export var target_node: NodePath

func _get_configuration_warnings() -> PackedStringArray:
    var warnings := PackedStringArray()

    if not target_node:
        warnings.append("需要设置 target_node 属性以正常工作。")

    return warnings
```

> 📌 这样编辑器会在场景面板中显示警告图标，提示开发者配置缺失的依赖。

### 3.3 场景粒度

```gdscript
# ✅ 合理的拆分:
# player.tscn      — 玩家角色
# enemy.tscn       — 敌人基类
# health_bar.tscn  — 可复用的血条组件
# main_menu.tscn   — 主菜单
# world.tscn       — 游戏世界（组合以上场景）

# ❌ 过度拆分或不够拆分:
# 一个巨大的 main.tscn 包含所有游戏逻辑
# 每个小 UI 元素都独立为一个场景（过度工程）
```

## 4. 父→子 与 子→父 通信规则

### 4.1 黄金法则

```
父节点 → 子节点:  使用直接方法调用
子节点 → 父节点:  使用信号（signal）

向下调用，向上通知
```

### 4.2 父节点调用子节点

```gdscript
# 父节点脚本（如 World.gd）
extends Node2D

@onready var player: Player = $Player

func _input(event: InputEvent) -> void:
    if event.is_action_pressed("jump"):
        player.jump()  # ✅ 直接调用

func deal_damage_to_player(amount: float) -> void:
    player.take_damage(amount)  # ✅ 直接调用
```

### 4.3 子节点通知父节点

```gdscript
# 子节点脚本（如 Player.gd）
extends CharacterBody2D

signal health_changed(new_health: int)
signal player_died

func take_damage(amount: int) -> void:
    health -= amount
    health_changed.emit(health)  # ✅ 用信号通知父节点

    if health <= 0:
        player_died.emit()  # ✅ 用信号通知父节点
```

> 📌 信号实现了观察者模式——子节点不需要知道谁在监听，父节点不需要轮询子节点状态。

### 4.4 何时用信号、何时用调用

| 场景 | 信号 | 直接调用 |
|------|:----:|:-------:|
| 子节点通知父节点 | ✅ | ❌ |
| 父节点控制子节点 | ❌ | ✅ |
| 跨分支节点通信 | ✅ | ❌ |
| UI 更新响应数据变化 | ✅ | ❌ |
| 单次配置/初始化 | ❌ | ✅ |
| 持续的状态查询 | ❌ | ✅ |

## 5. 场景组织建议

### 5.1 项目场景目录结构

```
res://
├── scenes/
│   ├── levels/
│   │   ├── level_1.tscn
│   │   └── level_2.tscn
│   ├── characters/
│   │   ├── player/
│   │   │   ├── player.tscn
│   │   │   └── player.gd
│   │   └── enemies/
│   │       ├── base_enemy.tscn
│   │       ├── base_enemy.gd
│   │       ├── slime.tscn
│   │       └── slime.gd
│   ├── ui/
│   │   ├── main_menu.tscn
│   │   ├── hud.tscn
│   │   └── pause_menu.tscn
│   └── props/
│       ├── chest.tscn
│       └── door.tscn
├── scripts/
│   ├── autoload/
│   │   └── game_manager.gd
│   └── utilities/
│       └── math_utils.gd
├── assets/
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
└── resources/
    ├── items/
    └── dialogs/
```

### 5.2 典型根场景结构

```gdscript
# main.tscn (游戏根场景)
# Node (root)
# ├── GameManager (Autoload, 自动添加)
# ├── AudioManager (Autoload, 自动添加)
# └── CurrentScene (由场景切换器加载)
#     ├── World (Node2D/Node3D)
#     └── UI (CanvasLayer)
```

> 📌 注意：Autoload 节点始终在根视口的 children 列表中排在已加载场景之前。

## 6. 常见错误

### 6.1 过度依赖全局路径

```gdscript
# ❌ 坏: 硬编码绝对路径
var player = get_node("/root/World/Level1/Player")
var ui = get_node("/root/World/UI/HealthBar")

# ✅ 好: 使用信号或依赖注入
@export var player: Player
signal health_changed(new_health: int)
```

### 6.2 场景与脚本耦合过紧

```gdscript
# ❌ 坏: 假设固定的子节点结构
func _ready() -> void:
    $Sprite2D.texture = load("...")  # 假设一定有 Sprite2D
    $CollisionShape2D.shape = ...     # 假设一定有 CollisionShape2D

# ✅ 好: 使用 @export 引用或检查存在
@export var sprite: Sprite2D
@export var collision_shape: CollisionShape2D

func _ready() -> void:
    if sprite:
        sprite.texture = load("...")
```

### 6.3 场景层次过深

```gdscript
# ❌ 坏: 过深的嵌套
# A → B → C → D → E → F → G (7层)

# ✅ 好: 扁平的层次结构
# A
# ├── B
# ├── C
# └── D (最多3-4层)
```
