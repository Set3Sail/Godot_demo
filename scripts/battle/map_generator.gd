# scripts/battle/map_generator.gd
## 地图节点生成器: 基于种子随机生成楼层制地图。
class_name MapGenerator
extends RefCounted

const FLOOR_HEIGHT: float = 300.0
const NODE_SPACING_X: float = 200.0

var _rng: RandomNumberGenerator = RandomNumberGenerator.new()

## 生成完整章节地图
func generate(config: MapConfig, seed: int = -1) -> MapData:
    if seed >= 0:
        _rng.seed = seed
    else:
        _rng.randomize()

    var map: MapData = MapData.new()
    map.chapter = config.chapter
    map.floors = config.floors
    map.wheel_level = config.wheel_level

    var nodes_per_floor: Array[int] = _distribute_nodes(config)

    var node_id_counter: int = 0
    var prev_floor_nodes: Array[int] = []

    for floor in range(config.floors):
        var floor_nodes: Array[int] = []
        var count: int = nodes_per_floor[floor]

        # 分配节点类型
        var types: Array[int] = _assign_node_types(config, count, floor, config.floors)

        for i in range(count):
            var ntype: int = types[i]
            var node: MapNode = MapNode.new()
            node.node_id = node_id_counter
            node.floor = floor
            node.position_index = i
            node.node_type = ntype
            node.position = Vector2(
                (i - (count - 1) * 0.5) * NODE_SPACING_X,
                floor * FLOOR_HEIGHT
            )
            map.nodes[node_id_counter] = node
            floor_nodes.append(node_id_counter)
            node_id_counter += 1

        # 连接上一层的节点（确保每个节点至少有一条路径）
        if floor > 0 and not prev_floor_nodes.is_empty():
            _connect_floors(map, prev_floor_nodes, floor_nodes, config.min_paths)

        prev_floor_nodes = floor_nodes

    return map


func _distribute_nodes(config: MapConfig) -> Array[int]:
    var nodes: Array[int] = []
    var remaining: int = config.total_nodes
    var floors: int = config.floors

    # Boss在顶层占1个节点
    remaining -= 1

    for f in range(floors - 1):
        var min_n: int = config.nodes_per_floor_min
        var max_n: int = mini(config.nodes_per_floor_max, remaining - (floors - f - 2) * min_n)
        max_n = mini(max_n, remaining)
        var count: int = _rng.randi_range(min_n, max_n)
        nodes.append(count)
        remaining -= count

    nodes.append(remaining)  # 倒数第二层
    nodes.append(1)  # 顶层=Boss

    return nodes


func _assign_node_types(config: MapConfig, count: int, floor: int, total_floors: int) -> Array[int]:
    var types: Array[int] = []

    # 第1层不出现精英和营地（除第1章教学外）
    var no_elite_camp: bool = (floor == 0 and config.chapter > 1)

    for i in range(count):
        var roll: float = _rng.randf()
        var cumulative: float = 0.0

        for type_key in config.node_distribution:
            cumulative += config.node_distribution[type_key]
            if roll <= cumulative:
                var ntype: int = _str_to_type(type_key)
                if no_elite_camp and (ntype == MapConfig.NodeType.ELITE or ntype == MapConfig.NodeType.CAMP):
                    ntype = MapConfig.NodeType.BATTLE
                types.append(ntype)
                break

    # Boss层固定为Boss
    if floor == total_floors - 1:
        types = [MapConfig.NodeType.BOSS]

    return types


func _connect_floors(map: MapData, upper: Array[int], lower: Array[int], min_paths: int) -> void:
    # 确保每个上层节点至少连接到 min_paths 个下层节点
    for u_id in upper:
        var connections: Array[int] = []
        var connect_count: int = _rng.randi_range(1, mini(min_paths, lower.size()))
        var shuffled_lower: Array[int] = lower.duplicate()
        shuffled_lower.shuffle()
        for j in range(connect_count):
            connections.append(shuffled_lower[j])
        for c in connections:
            if not c in map.connections[u_id]:
                map.connections[u_id].append(c)
            if not u_id in map.connections[c]:
                map.connections[c].append(u_id)

    # 验证每个下层节点至少有一条来自上层的连接
    for l_id in lower:
        var has_connection: bool = false
        for u_id in upper:
            if l_id in map.connections.get(u_id, []):
                has_connection = true
                break
        if not has_connection:
            var u_id: int = upper[_rng.randi_range(0, upper.size() - 1)]
            map.connections[u_id].append(l_id)
            map.connections[l_id].append(u_id)


func _str_to_type(s: String) -> int:
    match s:
        "BATTLE": return MapConfig.NodeType.BATTLE
        "ELITE":  return MapConfig.NodeType.ELITE
        "WHEEL":  return MapConfig.NodeType.WHEEL
        "CAMP":   return MapConfig.NodeType.CAMP
        "EVENT":  return MapConfig.NodeType.EVENT
        "BOSS":   return MapConfig.NodeType.BOSS
    return MapConfig.NodeType.BATTLE
