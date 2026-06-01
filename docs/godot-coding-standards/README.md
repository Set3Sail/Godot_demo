# Godot 4.x + GDScript 代码规范

> **适用范围**: Godot 4.0~4.5, GDScript 2.0
> **目标读者**: 使用 GDScript 进行 Godot 4.x 项目开发的程序员
> **整理日期**: 2026-06-01

## 目录

| 序号 | 文档 | 内容概要 |
|------|------|----------|
| 01 | [GDScript 风格指南](./01-gdscript-style-guide.md) | 命名规范、代码格式、文档注释、代码段排序 |
| 02 | [场景与节点架构](./02-scene-node-architecture.md) | 场景树、节点继承、组合模式、场景设计原则 |
| 03 | [信号与通信模式](./03-signals-communication.md) | 观察者模式、信号命名、连接方式、解耦最佳实践 |
| 04 | [资源与文件管理](./04-resource-file-management.md) | 脚本作为资源、preload vs load、文件结构约定 |
| 05 | [性能优化与反模式](./05-performance-anti-patterns.md) | 常见陷阱、性能考量、内存管理、代码异味 |
| 06 | [静态类型与类型提示](./06-static-typing.md) | 类型注解、typed array、类型推断、as 类型转换 |
| 07 | [Autoload 与单例模式](./07-autoload-patterns.md) | 全局单例、场景切换、何时使用/不适用 Autoload |

## 快速参考卡片

### 命名速查
```gdscript
# 文件: snake_case.gd
# 类: class_name PascalCase
# 函数/变量: snake_case
# 私有成员: _leading_underscore
# 常量: CONSTANT_CASE
# 枚举: enum PascalCase { VALUE_ONE, VALUE_TWO }
# 信号: past_tense_verb  (door_opened, health_changed)
# Autoload: PascalCase
```

### 类型注解速查
```gdscript
var health: int = 100
var name: String = "Player"
var enemies: Array[Node] = []
var inventory: Dictionary[String, int] = {}
func take_damage(amount: float) -> void:
```

### 信号速查
```gdscript
signal health_changed(new_health: int)
signal door_opened

# 连接
button.pressed.connect(_on_button_pressed)

# 发射
health_changed.emit(current_health)
```

### 场景设计原则
1. 场景应自包含（无外部依赖）
2. 每个场景只有一个根节点
3. 场景 = OOP 中的"类"，实例化 = "实例"
4. 信号向上（子→父），调用向下（父→子）

## 核心规则速查（Top 10）

1. ✅ 使用 `##` 写文档注释，而非 `#`
2. ✅ 所有信号名使用过去式动词（`door_opened`，非 `door_open`）
3. ✅ `@tool`、`@export`、`@onready` 使用注解格式，不用旧关键字
4. ✅ 挂载到节点的脚本必须显式 `extends Node`（或子类）
5. ✅ Typed 数组：`Array[Node]`，非 `Array`
6. ✅ 类型注解冒号紧贴变量名：`var x: int`，非 `var x : int`
7. ✅ `##` 文档注释中不支持 `@param`/`@return`，用 `[param name]` 替代
8. ✅ 注解标签 `@tutorial:` 不允许冒号前有空格
9. ✅ Autoload 不允许 `free()` / `queue_free()`
10. ✅ 使用 `_get_configuration_warnings()` 暴露场景依赖问题

## 参考来源

所有规则基于 Godot 官方文档 4.0~4.5 版本，经对抗性验证确认：
- [GDScript Style Guide](https://docs.godotengine.org/en/4.0/tutorials/scripting/gdscript/gdscript_styleguide.html)
- [Static Typing in GDScript](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/static_typing.html)
- [Scene Organization Best Practices](https://docs.godotengine.org/en/4.3/tutorials/best_practices/scene_organization.html)
- [Singletons (Autoload)](https://docs.godotengine.org/en/4.0/tutorials/scripting/singletons_autoload.html)
- [GDScript Documentation Comments](https://docs.godotengine.org/en/4.3/tutorials/scripting/gdscript/gdscript_documentation_comments.html)
- [Godot Design Philosophy](https://docs.godotengine.org/en/4.0/getting_started/introduction/godot_design_philosophy.html)
