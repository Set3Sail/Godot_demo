# scripts/data/map_data.gd
## 地图运行时数据。存储生成后的节点和连接关系。
class_name MapData
extends RefCounted

var chapter: int = 1
var floors: int = 3
var wheel_level: int = 1
var nodes: Dictionary = {}           # {node_id: MapNode}
var connections: Dictionary = {}     # {node_id: [connected_node_ids]}
var current_node_id: int = -1        # 玩家当前位置
var visited_nodes: Array[int] = []   # 已访问节点


func get_node(node_id: int) -> MapNode:
    return nodes.get(node_id)


func get_current_node() -> MapNode:
    return nodes.get(current_node_id)


func get_available_next_nodes() -> Array[MapNode]:
    if current_node_id == -1:
        return []
    var next: Array[MapNode] = []
    if current_node_id in connections:
        for next_id in connections[current_node_id]:
            var node: MapNode = nodes.get(next_id)
            if node and node.floor > get_current_node().floor:
                next.append(node)
    return next


func move_to_node(node_id: int) -> void:
    if current_node_id != -1:
        visited_nodes.append(current_node_id)
    current_node_id = node_id


func is_complete() -> bool:
    if current_node_id == -1:
        return false
    var node: MapNode = get_current_node()
    return node and node.node_type == MapConfig.NodeType.BOSS
