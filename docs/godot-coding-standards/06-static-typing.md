# 06 - 静态类型与类型提示

> 基于 Godot 官方静态类型文档 — 对抗性验证通过 (2-1 ~ 3-0)

## 1. 为什么使用静态类型

### 1.1 收益

1. **性能提升**: 类型化的 GDScript 在编译时已知操作数类型，可生成优化的操作码
2. **自动补全**: 编辑器能提供更好的代码补全建议
3. **错误预防**: 编译时捕获类型不匹配的错误
4. **代码自文档化**: 类型提示让代码意图更清晰
5. **安全行 (Safe Lines)**: 编辑器用绿线标记类型安全的代码行

> 官方引用: "typed GDScript improves performance by using optimized opcodes when operand/argument types are known at compile time."

### 1.2 团队项目建议

> "Typed GDScript and dynamic GDScript can coexist in the same project. But it's recommended to stick to either style for consistency."

**建议: 在团队项目中统一使用类型化 GDScript。**

## 2. 类型注解语法

### 2.1 变量和常量

```gdscript
# 基本语法: var name: Type = value
var health: int = 100
var speed: float = 300.0
var player_name: String = "Hero"
var is_alive: bool = true
var position: Vector2 = Vector2.ZERO
var color: Color = Color.WHITE

# 常量
const MAX_HEALTH: int = 100
const GRAVITY: float = 9.8
const GAME_TITLE: String = "My Game"
```

### 2.2 函数参数和返回值

```gdscript
# 参数类型提示
func take_damage(amount: float, source: Node) -> void:
    health -= amount

# 返回值类型提示（使用 ->）
func get_health_percentage() -> float:
    return float(health) / float(max_health) * 100.0

# void 返回类型
func _ready() -> void:
    pass

# 无返回值
func _process(delta: float) -> void:
    pass
```

### 2.3 类型推断（`:=`）

```gdscript
# 写冒号不加类型，Godot 自动推断
var health := 100              # 推断为 int
var speed := 300.0             # 推断为 float
var name := "Player"           # 推断为 String
var pos := Vector2(100, 200)   # 推断为 Vector2

# 函数参数类型推断
func add(a := 0, b := 0) -> int:
    return a + b

# 常量推断（= 和 := 对常量没有区别）
const MAX := 100       # 等同于 const MAX = 100
```

> ⚠️ **何时用 := vs : Type**:
> - 类型从赋值**完全明确可推断**时 → 可以用 `:=`
> - 类型需要**从右侧表达式推导**时 → 必须用 `: Type`
> - **团队成员一致性优先** → 团队统一选用一种风格

### 2.4 可空类型

```gdscript
# 允许 null 的变量
var target: Node = null       # Node 可为 null
var optional_name: String = ""  # String 不能为 null（默认）
var nullable_int: int = 0     # int 不能为 null

# 使用 Variant 处理真正未知的类型
var unknown: Variant = null
```

## 3. Typed Array（类型化数组）

### 3.1 语法

```gdscript
# 语法: Array[ElementType]
var scores: Array[int] = [10, 20, 30]
var enemies: Array[Node] = []
var players: Array[Player] = []  # 使用自定义类名
var names: Array[String] = ["Alice", "Bob"]

# 嵌套类型数组不支持
# var matrix: Array[Array[int]] = []  # ❌ 语法错误
```

### 3.2 Typed Array 的性能优势

```gdscript
# ❌ 无类型: 每次访问都是 Variant，需要运行时类型检查
var items = []
items.append("sword")
var first: Variant = items[0]  # 不知道类型

# ✅ 类型化: 编译器知道元素类型，生成优化代码
var items: Array[String] = []
items.append("sword")
var first: String = items[0]  # 编译时确定类型
```

### 3.3 for 循环中的类型

```gdscript
var enemies: Array[Enemy] = get_enemies()

# 自动推断循环变量类型
for enemy in enemies:
    enemy.take_damage(10)  # enemy 自动推断为 Enemy 类型

# Godot 4.2+: 即使数组无类型，也可指定循环变量类型
var data = [1, 2, 3]  # 无类型数组
for num: int in data:
    print(num)
```

### 3.4 Typed Array 的限制

```gdscript
# push_back 等方法仍然无类型（返回 Variant）
var arr: Array[int] = [1, 2, 3]
var val = arr.pop_back()  # val 是 Variant，不是 int

# 解决方案: 显式声明返回类型
var val: int = arr.pop_back()
```

## 4. Typed Dictionary（类型化字典）

### 4.1 语法

```gdscript
# 语法: Dictionary[KeyType, ValueType]
var scores: Dictionary[String, int] = {
    "Alice": 100,
    "Bob": 85
}
var inventory: Dictionary[String, ItemData] = {}
var settings: Dictionary[String, Variant] = {}

# 嵌套类型字典不支持
# var nested: Dictionary[String, Dictionary[String, int]] = {}  # ❌
```

### 4.2 使用

```gdscript
var costs: Dictionary[String, int] = {"apple": 5, "orange": 10}

# for 循环: 值和键都有类型
for item_name: String in costs:
    var price: int = costs[item_name]
    print("%s costs %d" % [item_name, price])

# [] 运算符有类型安全
costs["banana"] = 8       # ✅
costs["banana"] = "free"  # ❌ 类型不匹配
```

## 5. as 类型转换

### 5.1 基本用法

```gdscript
# as 尝试类型转换，失败时返回 null（不报错）
var player = body as Player
if player:
    player.take_damage(10)

# 内置类型转换失败时抛出错误（不同于自定义类型）
# var x = "hello" as int  # 抛出错误！
```

### 5.2 as vs is

```gdscript
# as: 静默返回 null（可能隐藏 bug）
func _on_body_entered(body: Node2D) -> void:
    var player = body as Player
    player.take_damage(10)  # 如果 body 不是 Player，player 为 null，可能崩溃！

# ✅ 推荐: 使用 is + 带类型声明的赋值
func _on_body_entered(body: Node2D) -> void:
    if not (body is Player):
        push_error("Expected Player, got: " + str(body.get_class()))
        return
    var player: Player = body
    player.take_damage(10)
```

> 📌 `is` 提供更清晰的错误信息，`as` 更简洁但会隐藏类型错误。**社区推荐尽量使用 `is`。**

### 5.3 安全行与 as

```gdscript
# 使用 as 获得安全行（绿色行号）
@onready var timer := $Timer as Timer        # ✅ 安全行
@onready var timer: Timer = $Timer           # ❌ 非安全行

# ⚠️ 注意: 安全行不等于更可靠的代码！
# $Timer 是 Timer 类型时两者等价
# $Timer 不是 Timer 类型时:
#   timer := $Timer as Timer  → timer 为 null（静默失败）
#   timer: Timer = $Timer     → 立即报错（快速失败）

# ✅ 推荐: 使用显式类型 + 快速失败
@onready var timer: Timer = $Timer  # 如果不是 Timer，立即报错
```

## 6. 自定义类类型

### 6.1 通过 class_name 注册

```gdscript
# enemy.gd
class_name Enemy
extends CharacterBody2D

# 注册后全局可用
var enemy: Enemy = Enemy.new()
var enemies: Array[Enemy] = []
```

### 6.2 通过 preload 引用

```gdscript
# 不需要 class_name 的方式
const EnemyScript = preload("res://scripts/enemies/enemy.gd")
var enemy: EnemyScript

# 或者直接 preload 场景的脚本
const PlayerScene = preload("res://scenes/player/player.tscn")
var player: PlayerScene  # 使用场景类型
```

## 7. 注解系统（Godot 4.x 新特性）

### 7.1 为什么 Godot 4 使用注解

Godot 4 将 Godot 3 的关键字（`tool`, `export`, `onready`）替换为注解系统（`@tool`, `@export`, `@onready`），原因有三个：

1. **避免语法复杂化**: 每个新功能都加关键字会让语言语法过于复杂
2. **避免标识符冲突**: 关键字可能与用户声明的标识符冲突
3. **降低扩展成本**: 添加注解不需要大幅修改解析器

### 7.2 常用注解

```gdscript
@tool           # 脚本在编辑器中运行
@export         # 变量在编辑器中可见和可编辑
@export_range   # 带范围的导出变量
@export_enum    # 枚举导出
@export_file    # 文件路径导出
@export_dir     # 目录路径导出
@onready        # 在 _ready 之前初始化
@warning_ignore # 忽略特定警告
@rpc            # 远程过程调用
@static_unload  # 静态卸载
```

### 7.3 注解参数限制

> ⚠️ 注解参数必须是编译时/解析时可解析的常量表达式或字符串字面量——不能引用运行时值。

```gdscript
# ✅ 正确
@export_range(0, 100) var health: int
@export var speed: float = 300.0
@export_enum("Warrior", "Mage", "Rogue") var class_type: String

# ❌ 错误
@export_range(0, max_health) var health: int  # max_health 是运行时变量
```

## 8. 编辑器警告配置

### 8.1 推荐的严格类型设置

在 **项目设置 → GDScript → 警告** 中启用：

```gdscript
# 推荐启用的警告（团队项目）
UNTYPED_DECLARATION: warn     # 无类型声明 → 警告
INFERRED_DECLARATION: ignore  # 类型推断声明 → 忽略（团队选择）
UNSAFE_PROPERTY_ACCESS: warn  # 不安全属性访问 → 警告
UNSAFE_METHOD_ACCESS: warn    # 不安全方法访问 → 警告
UNSAFE_CAST: warn             # 不安全类型转换 → 警告
UNSAFE_CALL_ARGUMENT: warn    # 不安全调用参数 → 警告
RETURN_VALUE_DISCARDED: warn  # 返回值未使用 → 警告
```

> 📌 如果团队统一使用显式类型（不使用 `:=`），则将 `INFERRED_DECLARATION` 设为 `warn`。

### 8.2 编辑器辅助设置

```
编辑器设置 → 文本编辑器 → 补全:
  ☑ Add Type Hints           # 自动添加类型提示
  ☑ 启用安全行指示器

编辑器设置 → 文本编辑器 → GDScript:
  ☑ 显示不安全代码提示
```

## 9. 类型系统限制

以下情况无法使用类型化（会导致语法错误）：

- ❌ 数组元素的单独类型说明（`var arr: Array[int, String]` 不合法）
- ❌ 嵌套类型化集合（`Array[Array[int]]`, `Dictionary[String, Array[int]]`）
- ❌ 元组类型
- ❌ 函数类型（不能将函数作为类型传递）

## 10. 类型规范检查清单

- [ ] 所有 `var` 声明添加类型注解或使用 `:=`
- [ ] 所有函数参数添加类型提示
- [ ] 所有函数添加返回类型（包括 `-> void`）
- [ ] 数组使用 `Array[Type]` 而非裸 `Array`
- [ ] 字典使用 `Dictionary[K, V]` 而非裸 `Dictionary`
- [ ] 优先使用 `is` 而非 `as` 进行类型检查
- [ ] 避免 `Variant` 除非确实需要动态类型
- [ ] 项目设置中启用类型相关警告
- [ ] 自定义类使用 `class_name` 以便全局类型引用
- [ ] 使用类型化全局方法（`absf` 替代 `abs`）
