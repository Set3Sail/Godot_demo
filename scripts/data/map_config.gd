# scripts/data/map_config.gd
## 章节地图配置数据。定义每章的节点分布和约束。
class_name MapConfig
extends Resource

enum NodeType { BATTLE, ELITE, WHEEL, CAMP, EVENT, BOSS }

@export var chapter: int = 1
@export var total_nodes: int = 15
@export var floors: int = 3
@export var wheel_level: int = 1  # 轮盘等级 1-4
@export var node_distribution: Dictionary = {
	"BATTLE": 0.50,    # ~50% 普通战斗
	"EVENT": 0.20,     # ~20% 命运事件
	"WHEEL": 0.12,     # ~12% 轮盘
	"CAMP": 0.08,      # ~8% 营地
	"ELITE": 0.10,     # ~10% 精英
}
@export var nodes_per_floor_min: int = 4
@export var nodes_per_floor_max: int = 6
@export var min_paths: int = 2  # 每层最少可选路线
