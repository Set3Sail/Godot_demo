# 04 - 资源与文件管理

> 基于 Godot 官方文档关于脚本、资源和最佳实践的内容 — 对抗性验证通过 (2-1 ~ 3-0)

## 1. 脚本的本质：一种 Resource

### 1.1 GDScript 是 Resource，不是传统的 Class

```gdscript
# Godot 内部继承链:
# Object → Resource → RefCounted → Script → GDScript

# 脚本本质上是一个 Resource 文件，
# 定义了对引擎内置类的一系列初始化操作。
```

> 📌 **关键理解**: GDScript 脚本在技术实现上不是传统 OOP 中的"类"——它是定义了一系列引擎类初始化的 Resource。但在日常开发中，你应该像使用类一样使用它。

### 1.2 extends 关键字的重要性

```gdscript
# ✅ 挂载到节点的脚本必须显式 extends
extends Node          # 或 Node2D, Node3D, Control 等

# ❌ 没有 extends 的脚本无法挂载到节点
# 无 extends 的脚本隐式继承 RefCounted
# RefCounted 和 Node 是 Object 下的同级分支
```

```gdscript
# 正确的继承选择:
extends Node           # 通用节点
extends Node2D         # 2D 游戏对象
extends Node3D         # 3D 游戏对象
extends Control        # UI 控件
extends CharacterBody2D # 2D 物理角色
extends Area2D         # 2D 检测区域
extends Resource       # 自定义数据资源
extends RefCounted     # 纯数据对象（不挂载到节点）
```

### 1.3 类注册（class_name）

```gdscript
# player.gd
class_name Player
extends CharacterBody2D

# 注册后，Player 成为全局可用的类型名
var player: Player = Player.new()
var players: Array[Player] = []
```

> 📌 `class_name` 在项目中全局注册。避免与引擎类或第三方插件的类名冲突。

## 2. 文件结构约定

### 2.1 推荐的项目目录结构

```
res://
├── assets/              # 原始资源文件
│   ├── sprites/         # 精灵/纹理
│   ├── sounds/          # 音频
│   ├── music/           # 音乐
│   ├── fonts/           # 字体
│   └── models/          # 3D 模型
│
├── scenes/              # 场景文件 (.tscn)
│   ├── levels/          # 关卡场景
│   ├── characters/      # 角色场景
│   ├── ui/              # UI 场景
│   └── props/           # 道具/物体场景
│
├── scripts/             # 脚本文件 (.gd)
│   ├── characters/      # 角色脚本
│   ├── ui/              # UI 脚本
│   ├── systems/         # 系统脚本
│   └── utilities/       # 工具脚本
│
├── resources/           # Godot 资源文件 (.tres, .res)
│   ├── materials/       # 材质
│   ├── items/           # 物品数据
│   └── themes/          # UI 主题
│
├── autoload/            # Autoload 脚本
│   ├── game_manager.gd
│   └── event_bus.gd
│
└── shaders/             # 着色器
    └── ...
```

### 2.2 文件命名规范

```gdscript
# 脚本文件: snake_case.gd
player_controller.gd
enemy_ai.gd
health_component.gd

# 场景文件: snake_case.tscn
main_menu.tscn
level_01.tscn

# 资源文件: snake_case.tres / snake_case.res
player_stats.tres
iron_sword.tres

# 目录: snake_case
scripts/characters/
assets/sprites/player/
```

## 3. preload vs load

### 3.1 核心区别

```gdscript
# preload: 脚本加载时执行（编译时/解析时）
const PlayerScene := preload("res://scenes/player/player.tscn")

# load: 执行到该行时加载（运行时）
var scene = load("res://scenes/player/player.tscn")
```

| 特性 | preload | load |
|------|---------|------|
| 加载时机 | 脚本解析时 | 运行时执行到该行时 |
| 适用场景 | 已知的、始终需要的资源 | 动态的、可选的资源 |
| 内存管理 | 常量，脚本卸载时才释放 | 变量，可设为 null 触发释放 |
| 可用位置 | 常量声明 | 任意位置 |
| 用于 const | ✅ | ❌（const 需要编译时值） |

### 3.2 何时使用 preload

```gdscript
# ✅ 适合 preload 的场景:
const BULLET_SCENE := preload("res://scenes/bullet.tscn")     # 频繁实例化
const PLAYER_SCRIPT := preload("res://scripts/player.gd")     # 类型引用
const GAME_DATA := preload("res://resources/game_data.tres")  # 始终需要的数据

# ❌ 不适合 preload 的场景:
# 1. 可能被 @export 覆盖的资源（preload 是常量，无法覆盖）
# 2. 大量大资源（preload 常量只有卸载整个脚本才能释放）
# 3. 不确定是否会使用的资源（浪费内存）
# 4. 脚本自身加载时时机不可控的情况
```

### 3.3 何时使用 load

```gdscript
# ✅ 适合 load 的场景:
func load_level(level_name: String) -> void:
    var path = "res://scenes/levels/%s.tscn" % level_name
    var scene = load(path)  # 动态路径
    get_tree().change_scene_to_packed(scene)

# ✅ 可释放的加载
func load_large_asset() -> void:
    var data = load("res://assets/large_data.res")
    # ... 使用 data ...
    data = null  # 允许 RefCounted 回收内存

# ✅ 条件性加载
func get_weapon_scene(weapon_type: String) -> PackedScene:
    match weapon_type:
        "sword":
            return load("res://scenes/weapons/sword.tscn")
        "bow":
            return load("res://scenes/weapons/bow.tscn")
    return null
```

### 3.4 @export 替代 preload（推荐模式）

```gdscript
# ✅ 推荐: 使用 @export 允许灵活替换
@export var bullet_scene: PackedScene
@export var explosion_effect: PackedScene
@export var hit_sound: AudioStream

# 在编辑器中可以拖入不同的场景/资源
# 比 preload 常量更灵活

# ❌ 不灵活: 写死的 preload
const BULLET_SCENE := preload("res://scenes/bullet.tscn")
# 无法在编辑器中替换为其他场景
```

## 4. 资源管理

### 4.1 自定义 Resource 类型

```gdscript
# item_data.gd
class_name ItemData
extends Resource

@export var item_name: String = ""
@export var description: String = ""
@export var icon: Texture2D
@export var max_stack: int = 99
@export var weight: float = 0.0
@export var base_value: int = 0
```

创建后，可以在文件系统中右键 → 新建资源 → ItemData，创建 `.tres` 文件来定义具体物品。

### 4.2 资源引用 vs 资源复制

```gdscript
# 资源默认是引用（共享）
var material_a := load("res://materials/red.tres")
var material_b := load("res://materials/red.tres")
# material_a 和 material_b 指向同一个 Resource 对象

# 需要独立副本时使用 duplicate()
var unique_material = material_a.duplicate()
```

> ⚠️ **重要**: 修改共享资源会影响所有引用它的对象。这是常见的 Bug 来源。

### 4.3 资源子资源标记

```gdscript
# 标记资源为唯一（保存时复制，运行时独立）
@export var material: Material:
    set(value):
        material = value
        # 在场景保存时为每个实例创建独立副本
```

## 5. 场景文件与 UID

### 5.1 Godot 4.x UID 系统

```gdscript
# Godot 4.x 为每个文件生成唯一 UID
# 配置在 .godot/uid_cache.txt 中
# UID 使文件引用在文件被移动/重命名时仍然有效

# 资源路径写法:
const SCENE = preload("uid://c5w8y0k0b0v8x")  # 通过 UID 引用
const SCENE = preload("res://scenes/game.tscn") # 通过路径引用（也有效）
```

> 📌 优先使用文件路径（`res://`），UID 格式主要用于引擎内部和文件移动后的自动更新。

## 6. 编辑器文件系统注意事项

### 6.1 文件操作

- **永远在编辑器中移动/重命名文件**（而非操作系统的文件管理器）
- 编辑器的文件系统面板会自动更新所有引用
- 如果在编辑器外移动文件，依赖关系会断裂

### 6.2 .gdignore

```gdscript
# .gdignore 文件（放置在目录中）
# 该目录会被 Godot 忽略（不导入资源）
# 适用于: 测试文件、构建产物、大型原始数据
```

## 7. 常见错误

### 7.1 无 extends 挂载节点

```gdscript
# ❌ 错误: 忘记写 extends
# my_node.gd 的内容完全是变量和函数
var health = 100
# 无法挂载到场景中的节点！

# ✅ 正确
extends Node
var health: int = 100
```

### 7.2 修改共享资源

```gdscript
# ❌ 错误: 修改共享材质
$Sprite.material.color = Color.RED  # 所有使用此材质的精灵都变红！

# ✅ 正确: 使用 duplicate()
func _ready() -> void:
    $Sprite.material = $Sprite.material.duplicate()
    $Sprite.material.color = Color.RED  # 只影响当前精灵
```

### 7.3 preload 导致的不必要内存占用

```gdscript
# ❌ 错误: 预加载所有关卡
const LEVEL_1 = preload("res://scenes/level_1.tscn")
const LEVEL_2 = preload("res://scenes/level_2.tscn")
const LEVEL_3 = preload("res://scenes/level_3.tscn")
# ... 50 个关卡全部在脚本加载时加载到内存

# ✅ 正确: 按需加载
func load_level(level_num: int) -> void:
    var path = "res://scenes/levels/level_%d.tscn" % level_num
    var scene = load(path)
    get_tree().change_scene_to_packed(scene)
```
