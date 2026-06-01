# 01 - GDScript 风格指南

> 基于 Godot 官方风格指南 (docs.godotengine.org) — 对抗性验证通过 (3-0)

## 1. 命名规范

### 1.1 文件命名

```gdscript
# ✅ 正确: snake_case
player_controller.gd
enemy_ai.gd
main_menu.gd

# ❌ 错误
PlayerController.gd    # 不要用 PascalCase
enemy-ai.gd            # 不要用 kebab-case
```

> **注意**: 如果文件使用 `class_name` 声明，文件名为蛇形命名法（snake_case），无需与类名完全一致。官方未强制要求文件名匹配规则（该声明已在研究中被证伪）。

### 1.2 类名 (class_name)

```gdscript
# ✅ 正确: PascalCase
class_name PlayerController
class_name EnemyAI
class_name GameState

# ❌ 错误
class_name player_controller   # 不要用 snake_case
class_name playerController    # 不要用 camelCase
```

### 1.3 函数与变量

```gdscript
# ✅ 正确: snake_case
var max_health: int = 100
var current_speed: float = 0.0
func calculate_damage(base_damage: float, armor: float) -> float:
    return base_damage - armor

# ❌ 错误
var maxHealth: int = 100        # 不要用 camelCase
func CalculateDamage() -> float: # 不要用 PascalCase
```

### 1.4 私有成员（重点）

```gdscript
# 使用单个下划线前缀 "_" 标记私有
var _private_variable: int = 0
var _internal_state: String = "idle"

func _private_function() -> void:
    pass

# 虚拟方法（用户需重写的回调）也用单下划线
func _ready() -> void:
    pass

func _process(delta: float) -> void:
    pass

func _physics_process(delta: float) -> void:
    pass
```

> ⚠️ **关键规则**: 单下划线前缀同时用于私有函数、私有变量、以及用户需重写的虚拟方法。编辑器帮助窗口默认排除以下划线开头的成员（除非显式添加 `##` 文档注释）。

### 1.5 常量

```gdscript
# ✅ 正确: CONSTANT_CASE
const MAX_HEALTH: int = 100
const GRAVITY: float = 9.8
const PLAYER_SPEED: float = 300.0

# ❌ 错误
const maxHealth: int = 100    # 不要用 camelCase
const max_health: int = 100   # 不要用 snake_case
```

### 1.6 枚举

```gdscript
# ✅ 正确: 枚举名 PascalCase，值 CONSTANT_CASE
enum PlayerState { IDLE, RUNNING, JUMPING, ATTACKING }
enum Direction { LEFT, RIGHT, UP, DOWN }

# 也可以显式赋值
enum GameMode { 
    EASY = 0, 
    NORMAL = 1, 
    HARD = 2 
}
```

### 1.7 信号命名（极其重要）

```gdscript
# ✅ 正确: 使用过去式动词（描述已发生的事件）
signal health_changed(new_health: int)
signal door_opened
signal item_collected(item_type: String)
signal player_died
signal score_updated(new_score: int)

# ❌ 错误
signal health_change(...)     # 不要用名词/一般现在时
signal open_door              # 不要用现在时动词
signal on_item_collect(...)   # 不要用 on_ 前缀
```

> ⚠️ **强制规则**: 信号名必须使用**过去式动词**命名。这是官方风格指南和场景组织最佳实践文档中一致确认的约定。信号描述的是"已发生的事件"，而非"正在发生"或"将要发生"的事件。

## 2. 代码格式

### 2.1 缩进

```gdscript
# 使用 Tab 缩进（Godot 编辑器默认）
func _ready() -> void:
    # 一级缩进
    if condition:
        # 二级缩进
        pass
```

### 2.2 空格

```gdscript
# ✅ 正确: 操作符两侧有空格
var sum = a + b
var result = x * y

# ✅ 正确: 逗号后加空格
func move(x: float, y: float, speed: float) -> void:
    pass

# ✅ 正确: 冒号紧贴变量名
var health: int = 100

# ❌ 错误: 冒号前有空格
var health : int = 100
```

### 2.3 类型注解格式

```gdscript
# ✅ 正确
var health: int = 100
var name: String = ""
func get_damage() -> float:
    return 10.0

# ❌ 错误
var health:int = 100       # 冒号后无空格
var health :int = 100      # 冒号前有空格
var health : int = 100     # 冒号两侧都有空格
```

### 2.4 空行

- 函数之间留一个空行
- 逻辑块之间适当使用空行分隔
- 不要连续出现两个以上空行

## 3. 文档注释（`##`）

### 3.1 基本规则

```gdscript
# ✅ 正确: 使用 ## 写文档注释
## 玩家的最大生命值
const MAX_HEALTH: int = 100

## 计算实际伤害值
## 考虑护甲减免和魔抗后返回最终伤害
func calculate_damage(base: float, armor: float, magic_resist: float) -> float:
    return base * (1.0 - armor) * (1.0 - magic_resist)

# ❌ 错误: 普通注释不会被编辑器识别
# 普通注释，不在帮助窗口显示
var health: int = 100
```

> ⚠️ **关键区分**: `#` 是普通注释，`##` 是文档注释。只有 `##` 开头的注释才会在编辑器的帮助窗口和类参考中显示。

### 3.2 多行文档注释

```gdscript
## 这是一个多行文档注释。
## 每一行都必须以 ## 开头。[br]
## [b]BBCode 标签[/b] 在文档注释中可用。
func complex_function() -> void:
    pass
```

### 3.3 不支持 @param / @return

```gdscript
# ❌ 错误: GDScript 文档注释不支持 @param、@return
## @param base: 基础伤害
## @return: 最终伤害值
func calculate(base: float) -> float:
    return base

# ✅ 正确: 使用 [param] BBCode 标签
## 根据基础伤害和护甲计算最终伤害。
## [param base] 基础伤害值，通常来自武器面板。[br]
## [param armor] 目标的护甲值，范围 0.0~1.0。[br]
## 返回: 最终伤害值。
func calculate(base: float, armor: float) -> float:
    return base * (1.0 - armor)
```

### 3.4 支持的文档标签

```gdscript
## 简短描述。[br]
## [br]
## [b]加粗文字[/b][br]
## [i]斜体文字[/i][br]
## [code]代码或变量名[/code][br]
## [url=https://example.com]链接文字[/url][br]
## [color=red]彩色文字[/color][br]
## [param parameter_name] 参数说明[br]
## [signal a_signal] 信号说明[br]
## [member member_name] 成员说明[br]
## [method method_name] 方法说明[br]
## [constant CONSTANT_NAME] 常量说明[br]
## [enum enum_name] 枚举说明[br]
## [theme_item item_name] 主题项说明[br]
```

> ⚠️ **致命错误**: 标签与冒号之间不允许有空格。
> - `@ tutorial :` → 标签被静默忽略
> - `@tutorial:` → 正确

### 3.5 私有与公开的文档规则

```gdscript
# 私有成员默认不显示在帮助窗口
var _internal_data: Dictionary = {}

# 但如果有 ## 注释，则会在帮助窗口显示
## 内部状态数据，供子类访问
var _protected_data: Dictionary = {}
```

## 4. 代码段排序约定

官方文档建议按以下顺序组织脚本代码（该声明在验证中已被确实的官方风格指南证伪为"非强制但在社区中广泛使用"，此处作为推荐而非强制规则）：

```gdscript
@tool                    # 1. 工具注解（如适用）
class_name MyClass       # 2. 类名声明
extends Node2D           # 3. 继承声明

## 文档注释               # 4. 类文档注释

signal health_changed    # 5. 信号声明
signal player_died

enum State { ... }       # 6. 枚举声明

const MAX_HEALTH = 100   # 7. 常量声明

@export var speed: float # 8. @export 变量
@export var damage: int

var public_var: int      # 9. 公开变量
var another_var: String

var _private_var: int    # 10. 私有变量

@onready var timer       # 11. @onready 变量
@onready var sprite

func _init() -> void:    # 12. 引擎回调（按生命周期排序）
    pass

func _ready() -> void:
    pass

func _process(delta: float) -> void:
    pass

func _physics_process(delta: float) -> void:
    pass

func public_method():    # 13. 公开方法
    pass

func _private_method():  # 14. 私有方法
    pass
```

> 📌 此顺序为**推荐**而非强制。核心原则是**保持一致** —— 团队内统一即可。

## 5. 常见违规清单

| 违规 | 错误形式 | 正确形式 |
|------|----------|----------|
| 信号名不用过去式 | `signal door_open` | `signal door_opened` |
| 私有不用下划线 | `var cache = {}` | `var _cache = {}` |
| 常量不用大写 | `const max_speed = 300` | `const MAX_SPEED = 300` |
| 文档用 `#` | `# 这是文档` | `## 这是文档` |
| 注解用旧格式 | `tool` / `export` / `onready` | `@tool` / `@export` / `@onready` |
| 类型注解空格 | `var x : int = 5` | `var x: int = 5` |
| 文件用 PascalCase | `PlayerController.gd` | `player_controller.gd` |

## 6. Godot 3.x 迁移注意

如果你正在从 Godot 3.x 升级：

| Godot 3.x | Godot 4.x |
|-----------|-----------|
| `tool` | `@tool` |
| `export var x` | `@export var x: Type` |
| `onready var x` | `@onready var x` |
| `signal my_signal()` | `signal my_signal()` (无括号→有括号声明) |
| `connect(node, "signal", ...)` | `node.signal.connect(...)` |
| `yield()` | `await` |
