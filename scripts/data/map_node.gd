# scripts/data/map_node.gd
## 地图节点数据。
class_name MapNode
extends RefCounted

var node_id: int = -1
var floor: int = 0
var position_index: int = 0
var node_type: int = MapConfig.NodeType.BATTLE
var position: Vector2 = Vector2.ZERO
var is_burning: bool = false  # Ascension 10+ 燃烧节点
var is_visited: bool = false
var is_revealed: bool = false  # 是否对玩家可见


func get_type_name() -> String:
    match node_type:
        MapConfig.NodeType.BATTLE: return "普通战斗"
        MapConfig.NodeType.ELITE:  return "精英战"
        MapConfig.NodeType.WHEEL:  return "轮盘"
        MapConfig.NodeType.CAMP:   return "营地"
        MapConfig.NodeType.EVENT:  return "命运事件"
        MapConfig.NodeType.BOSS:   return "Boss"
    return "未知"


func get_icon() -> String:
    match node_type:
        MapConfig.NodeType.BATTLE: return "👾"
        MapConfig.NodeType.ELITE:  return "💀"
        MapConfig.NodeType.WHEEL:  return "🎰"
        MapConfig.NodeType.CAMP:   return "🏕️"
        MapConfig.NodeType.EVENT:  return "❓"
        MapConfig.NodeType.BOSS:   return "👹"
    return "❓"
