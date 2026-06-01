# scripts/battle/effect_resolver.gd
## 效果结算管道: 接收 EffectData 数组, 按 TARGET_RESOLVE → PRECONDITION
## → PRE_TRIGGER → EXECUTE → POST_TRIGGER → KILL_CHECK 顺序结算。
class_name EffectResolver
extends Node

var _resource_manager: ResourceManager
var _card_manager: CardManager
var _status_manager: StatusManager
var _enemy_manager: EnemyManager  # EnemyManager 引用
var _relic_manager: RelicManager  # RelicManager 引用


signal effect_about_to_execute(effect: EffectData, target: Node)
signal effect_executed(effect: EffectData, target: Node, result: Dictionary)
signal damage_about_to_apply(target: Node, amount: int)
signal damage_applied(target: Node, raw_amount: int, actual: int, blocked: int)
signal block_gained(target: Node, amount: int)
signal healing_applied(target: Node, amount: int)
signal kill_confirmed(target: Node, crystals: int)


## 注入依赖
func setup(
    rm: ResourceManager,
    cm: CardManager,
    sm: StatusManager,
    em: EnemyManager,
    rem: RelicManager
) -> void:
    _resource_manager = rm
    _card_manager = cm
    _status_manager = sm
    _enemy_manager = em
    _relic_manager = rem


## 结算一组效果（一张卡牌的全部效果）
func resolve_effects(effects: Array[EffectData], source: Node, caster_is_player: bool = true, pierce: int = 0) -> void:
    for effect in effects:
        var targets: Array[Node] = _resolve_targets(effect, source, caster_is_player)
        for i in range(effect.repeat_count):
            for target in targets:
                if not _check_precondition(effect, target):
                    continue
                effect_about_to_execute.emit(effect, target)
                _execute_effect(effect, target, caster_is_player, pierce)
                effect_executed.emit(effect, target, {})
                _check_kill(target)


## 解析目标
func _resolve_targets(effect: EffectData, source: Node, caster_is_player: bool) -> Array[Node]:
    match effect.target:
        EffectData.EffectTarget.SELF:
            return [source]
        EffectData.EffectTarget.SINGLE_ENEMY:
            return []
        EffectData.EffectTarget.ALL_ENEMIES:
            if _enemy_manager and _enemy_manager.has_method("get_alive_enemies"):
                return _enemy_manager.get_alive_enemies()
            return []
        EffectData.EffectTarget.RANDOM_ENEMY:
            if _enemy_manager and _enemy_manager.has_method("get_alive_enemies"):
                var enemies: Array = _enemy_manager.get_alive_enemies()
                if not enemies.is_empty():
                    return [enemies.pick_random()]
            return []
        EffectData.EffectTarget.FRONTMOST_ENEMY:
            if _enemy_manager and _enemy_manager.has_method("get_frontmost_enemy"):
                var front: Node = _enemy_manager.get_frontmost_enemy()
                if front:
                    return [front]
            return []
        EffectData.EffectTarget.ALL_ALLIES:
            if _enemy_manager and _enemy_manager.has_method("get_alive_allies"):
                return _enemy_manager.get_alive_allies()
            return []
    return []


func _check_precondition(effect: EffectData, target: Node) -> bool:
    if effect.condition.is_empty():
        return true
    if effect.condition == "target_has_mark":
        return _status_manager.has_status(target, "mark")
    if effect.condition == "target_alive":
        return is_instance_valid(target)
    return true


## 执行单个效果
func _execute_effect(effect: EffectData, target: Node, caster_is_player: bool, pierce: int) -> void:
    match effect.type:
        EffectData.EffectType.DAMAGE:
            _execute_damage(effect, target, caster_is_player, pierce)
        EffectData.EffectType.BLOCK:
            _execute_block(effect, target, caster_is_player)
        EffectData.EffectType.DRAW:
            _execute_draw(effect)
        EffectData.EffectType.GAIN_ENERGY:
            _execute_gain_energy(effect)
        EffectData.EffectType.BUFF:
            _execute_buff(effect, target)
        EffectData.EffectType.DEBUFF:
            _execute_debuff(effect, target)
        EffectData.EffectType.HEAL:
            _execute_heal(effect, target, caster_is_player)
        EffectData.EffectType.MODIFY_STAT:
            _execute_modify_stat(effect, target, caster_is_player)
        EffectData.EffectType.REMOVE_STATUS:
            _status_manager.remove_status(target, effect.status_id)
        EffectData.EffectType.SPECIAL:
            pass  # 由角色 Mechanic 处理


func _execute_damage(effect: EffectData, target: Node, caster_is_player: bool, pierce: int) -> void:
    var is_player_target: bool = (target == _get_player_node())
    var effective_damage: int = _resource_manager.get_effective_damage(effect.base_value, caster_is_player)
    var mult: float = _status_manager.get_damage_multiplier(
        _get_player_node() if caster_is_player else target,
        caster_is_player
    )
    var raw: int = int(ceilf(effective_damage * mult))
    damage_about_to_apply.emit(target, raw)

    var block: int
    if is_player_target:
        block = _resource_manager.get_player_block()
    else:
        block = _resource_manager.get_enemy_block(target)
    block = maxi(0, block - pierce)

    var absorbed: int = mini(raw, block)
    var actual: int = raw - absorbed

    if is_player_target:
        _resource_manager.modify_player_hp(-actual, "normal")
        if absorbed > 0:
            _resource_manager.modify_player_block(-absorbed)
    else:
        _resource_manager.modify_enemy_hp(target, -actual, "normal")
        if absorbed > 0:
            _resource_manager.modify_enemy_block(target, -absorbed)

    damage_applied.emit(target, raw, actual, absorbed)


func _execute_block(effect: EffectData, target: Node, caster_is_player: bool) -> void:
    var effective_block: int = _resource_manager.get_effective_block(effect.base_value, caster_is_player)
    var is_player_target: bool = (target == _get_player_node())
    if is_player_target:
        _resource_manager.modify_player_block(effective_block)
    else:
        _resource_manager.modify_enemy_block(target, effective_block)
    block_gained.emit(target, effective_block)


func _execute_draw(effect: EffectData) -> void:
    _card_manager.draw_cards(effect.base_value)


func _execute_gain_energy(effect: EffectData) -> void:
    _resource_manager.modify_player_energy(effect.base_value)


func _execute_buff(effect: EffectData, target: Node) -> void:
    _status_manager.apply_status(target, effect.status_id, effect.status_stacks, effect.status_duration)


func _execute_debuff(effect: EffectData, target: Node) -> void:
    _status_manager.apply_status(target, effect.status_id, effect.status_stacks, effect.status_duration)


func _execute_heal(effect: EffectData, target: Node, caster_is_player: bool) -> void:
    var is_player_target: bool = (target == _get_player_node())
    if is_player_target:
        _resource_manager.modify_player_hp(effect.base_value, "heal")
    else:
        _resource_manager.modify_enemy_hp(target, effect.base_value, "heal")
    healing_applied.emit(target, effect.base_value)


func _execute_modify_stat(effect: EffectData, target: Node, caster_is_player: bool) -> void:
    var is_player_target: bool = (target == _get_player_node())
    match effect.status_id:
        "strength":
            if is_player_target:
                _resource_manager.modify_player_strength(effect.base_value)
            else:
                _resource_manager.modify_enemy_strength(target, effect.base_value)
        "dexterity":
            if is_player_target:
                _resource_manager.modify_player_dexterity(effect.base_value)
            else:
                _resource_manager.modify_enemy_dexterity(target, effect.base_value)


func _check_kill(target: Node) -> void:
    if not is_instance_valid(target):
        return
    var hp: int
    if target == _get_player_node():
        hp = _resource_manager.get_player_hp()
    else:
        hp = _resource_manager.get_enemy_hp(target)
    if hp <= 0:
        var crystals: int = 0
        if _enemy_manager and _enemy_manager.has_method("get_crystal_drop"):
            crystals = _enemy_manager.get_crystal_drop(target)
        kill_confirmed.emit(target, crystals)


## 对具体目标结算效果（由外部通过 play_card 调用时传入具体 target）
func resolve_effects_on_target(effects: Array[EffectData], target: Node, source: Node, caster_is_player: bool = true, pierce: int = 0) -> void:
    for effect in effects:
        if not _check_precondition(effect, target):
            continue
        effect_about_to_execute.emit(effect, target)
        _execute_effect(effect, target, caster_is_player, pierce)
        effect_executed.emit(effect, target, {})
        _check_kill(target)


func _get_player_node() -> Node:
    if _resource_manager:
        return _resource_manager.get_parent()
    return null
