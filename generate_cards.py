#!/usr/bin/env python3
"""Generate missing character cards for the Godot 4.x card game."""

import os

CARDS_DIR = "/home/fangqihang2/claude-task/my_game_coding/resources/cards"

def load_existing_ids():
    """Load existing card IDs to avoid duplicates."""
    ids = set()
    for root, dirs, files in os.walk(CARDS_DIR):
        for f in files:
            if f.endswith(".tres"):
                path = os.path.join(root, f)
                with open(path) as fh:
                    for line in fh:
                        if line.strip().startswith('card_id'):
                            cid = line.split('"')[1]
                            ids.add(cid)
    return ids

EXISTING_IDS = load_existing_ids()

def make_card(card_id, card_name, character, card_type, rarity, cost, effects, keywords, description, extra_fields=None):
    """
    Generate a .tres file content.

    effects: list of dicts {
        "type": int,
        "target": int,
        "base_value": int (optional),
        "scale_stat": str (optional),
        "status_id": str (optional),
        "status_stacks": int (optional),
        "repeat_count": int (optional),
        "cost_hp": int (optional),
        "status": str (optional),
    }
    """
    assert card_id not in EXISTING_IDS, f"Duplicate card_id: {card_id}"

    num_effects = len(effects)
    load_steps = 2 + num_effects + 1  # ext_resources + sub_resources + main_resource

    lines = []
    lines.append(f'[gd_resource type="Resource" script_class="CardData" load_steps={load_steps} format=3]')
    lines.append('[ext_resource type="Script" path="res://scripts/data/card_data.gd" id="1_card"]')
    lines.append('[ext_resource type="Script" path="res://scripts/data/effect_data.gd" id="2_e"]')
    lines.append('')

    for i, eff in enumerate(effects):
        lines.append(f'[sub_resource type="Resource" id="ef{i}"]')
        lines.append(f'script = ExtResource("2_e")')
        lines.append(f'type = {eff["type"]}')
        lines.append(f'target = {eff["target"]}')
        if "base_value" in eff:
            lines.append(f'base_value = {eff["base_value"]}')
        if "scale_stat" in eff:
            lines.append(f'scale_stat = "{eff["scale_stat"]}"')
        if "status_id" in eff:
            lines.append(f'status_id = "{eff["status_id"]}"')
        if "status_stacks" in eff:
            lines.append(f'status_stacks = {eff["status_stacks"]}')
        if "repeat_count" in eff:
            lines.append(f'repeat_count = {eff["repeat_count"]}')
        if "cost_hp" in eff:
            lines.append(f'cost_hp = {eff["cost_hp"]}')
        if "status" in eff:
            lines.append(f'status = "{eff["status"]}"')
        lines.append('')

    lines.append('[resource]')
    lines.append(f'script = ExtResource("1_card")')
    lines.append(f'card_id = "{card_id}"')
    lines.append(f'card_name = "{card_name}"')
    lines.append(f'character = "{character}"')
    lines.append(f'card_type = {card_type}')
    lines.append(f'rarity = {rarity}')
    lines.append(f'cost = {cost}')

    eff_refs = ", ".join([f'SubResource("ef{i}")' for i in range(num_effects)])
    lines.append(f'effects = Array[ExtResource("2_e")]([{eff_refs}])')

    kw_list = ", ".join(f'"{kw}"' for kw in keywords)
    lines.append(f'keywords = Array[String]([{kw_list}])')
    lines.append(f'description = "{description}"')

    if extra_fields:
        for k, v in extra_fields.items():
            if isinstance(v, bool):
                lines.append(f'{k} = {"true" if v else "false"}')
            else:
                lines.append(f'{k} = {v}')
    lines.append('')
    return "\n".join(lines)


def write_card(dir_path, card_id, content):
    os.makedirs(dir_path, exist_ok=True)
    filepath = os.path.join(dir_path, f"{card_id}.tres")
    with open(filepath, "w") as f:
        f.write(content)
    print(f"  Created: {card_id}.tres")


def generate_moye_extra():
    """Generate ~55 cards for 墨夜 (moye)."""
    dir_path = os.path.join(CARDS_DIR, "moye")
    prefix = "moye"
    char = "墨夜"

    cards = []

    # ---- COMMON (20) ----
    common = [
        # (id_suffix, card_name, card_type, cost, effects, keywords, desc)
        ("frost_dagger", "冰霜匕首", 0, 1, [
            {"type": 0, "target": 1, "base_value": 4},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 2},
        ], ["冰霜"], "造成4点伤害，施加2层冰霜"),
        ("ice_wall", "冰墙", 1, 1, [
            {"type": 1, "target": 0, "base_value": 8},
        ], [], "获得8点格挡"),
        ("frost_touch", "寒冰触摸", 1, 0, [
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 1},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["冰霜"], "施加1层冰霜，抽1张牌"),
        ("cold_breath", "寒气吐息", 0, 2, [
            {"type": 0, "target": 2, "base_value": 4},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "全体4点伤害，施加1层冰霜"),
        ("frozen_armor", "冰甲术", 1, 2, [
            {"type": 1, "target": 0, "base_value": 10},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "获得10点格挡，施加1层冰霜"),
        ("ice_slash", "冰斩", 0, 1, [
            {"type": 0, "target": 1, "base_value": 8},
        ], [], "造成8点伤害"),
        ("frost_ward", "寒冰屏障", 1, 1, [
            {"type": 1, "target": 0, "base_value": 6},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["冰霜"], "获得6点格挡，抽1张牌"),
        ("chill_wind", "寒风", 0, 1, [
            {"type": 0, "target": 5, "base_value": 5},
            {"type": 5, "target": 5, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "对最前方敌人造成5点伤害，施加1层冰霜"),
        ("hail_strike", "冰雹击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 6, "repeat_count": 2},
        ], [], "造成6点伤害两次"),
        ("ice_barricade", "寒冰路障", 1, 2, [
            {"type": 1, "target": 0, "base_value": 12},
        ], [], "获得12点格挡"),
        ("frost_slash", "寒霜斩", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 2},
        ], ["冰霜"], "造成10点伤害，施加2层冰霜"),
        ("snowflake", "雪之舞", 1, 0, [
            {"type": 1, "target": 0, "base_value": 3},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "获得3点格挡，施加1层冰霜"),
        ("glacial_edge", "冰川之刃", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
        ], [], "造成6点伤害"),
        ("ice_needle", "冰针", 0, 0, [
            {"type": 0, "target": 3, "base_value": 3},
        ], [], "对随机敌人造成3点伤害"),
        ("winter_breath", "冬之吐息", 1, 1, [
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "全体施加1层冰霜"),
        ("cold_shield", "冷盾", 1, 1, [
            {"type": 1, "target": 0, "base_value": 7},
        ], [], "获得7点格挡"),
        ("frozen_strike", "冻结打击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 12},
        ], [], "造成12点伤害"),
        ("ice_pulse", "冰脉", 0, 1, [
            {"type": 0, "target": 1, "base_value": 5},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "造成5点伤害，施加1层冰霜"),
        ("permafrost_guard", "永冻守卫", 1, 2, [
            {"type": 1, "target": 0, "base_value": 8},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "获得8点格挡，全体施加1层冰霜"),
        ("ice_barb", "冰刺", 0, 1, [
            {"type": 0, "target": 1, "base_value": 7},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "造成7点伤害，施加1层冰霜"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in common:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 0, cost, effects, kws, desc))

    # ---- UNCOMMON (15) ----
    uncommon = [
        ("blizzard_strike", "暴风雪击", 0, 3, [
            {"type": 0, "target": 2, "base_value": 8},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 2},
        ], ["冰霜"], "全体8点伤害，施加2层冰霜"),
        ("frozen_mail", "冰霜铠甲", 1, 2, [
            {"type": 1, "target": 0, "base_value": 12},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "获得12点格挡，全体施加1层冰霜"),
        ("cold_snap_burst", "极寒爆发", 0, 2, [
            {"type": 0, "target": 1, "base_value": 12},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 3},
        ], ["冰霜"], "造成12点伤害，施加3层冰霜"),
        ("freeze_burst", "冻结爆裂", 0, 2, [
            {"type": 9, "target": 1, "base_value": 6, "status_id": "frost_damage"},
        ], ["冰霜"], "消耗冰霜层数造成伤害"),
        ("ice_spear", "冰枪术", 0, 2, [
            {"type": 0, "target": 1, "base_value": 8, "scale_stat": "strength"},
        ], ["冰霜"], "造成8(+力量)点伤害"),
        ("glacial_barrier", "寒冰障壁", 1, 2, [
            {"type": 1, "target": 0, "base_value": 15},
        ], [], "获得15点格挡"),
        ("whiteout", "白盲", 0, 2, [
            {"type": 0, "target": 2, "base_value": 5},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 2},
        ], ["冰霜"], "全体5点伤害，施加2层冰霜"),
        ("frost_bind", "冰霜束缚", 1, 1, [
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 4},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["冰霜"], "施加4层冰霜，抽1张牌"),
        ("cold_current", "寒流", 0, 1, [
            {"type": 0, "target": 2, "base_value": 3},
        ], ["冰霜"], "全体3点伤害"),
        ("ice_lance", "冰矛", 0, 3, [
            {"type": 0, "target": 1, "base_value": 18},
        ], [], "造成18点伤害"),
        ("frozen_legacy", "冰霜传承", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "frost_mastery"},
        ], ["冰霜"], "冰霜施加层数+1"),
        ("cold_recall", "寒冰回溯", 1, 1, [
            {"type": 2, "target": 0, "base_value": 2},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "抽2张牌，全体施加1层冰霜"),
        ("rime_storm", "霜暴", 0, 3, [
            {"type": 0, "target": 2, "base_value": 10},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 1},
        ], ["冰霜"], "全体10点伤害，施加1层冰霜"),
        ("ice_chain", "冰链", 0, 2, [
            {"type": 0, "target": 3, "base_value": 5, "repeat_count": 2},
        ], ["冰霜"], "对随机敌人造成5点伤害两次"),
        ("frostbite", "冻伤", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 2},
        ], ["冰霜"], "造成6点伤害，施加2层冰霜"),
        ("hibernate", "冬眠", 1, 2, [
            {"type": 1, "target": 0, "base_value": 10},
            {"type": 6, "target": 0, "base_value": 5},
        ], [], "获得10点格挡，回复5HP"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in uncommon:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 1, cost, effects, kws, desc))

    # ---- RARE (11) ----
    rare = [
        ("ice_age", "冰河时代", 0, 3, [
            {"type": 0, "target": 2, "base_value": 12},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 3},
        ], ["冰霜"], "全体12点伤害，施加3层冰霜"),
        ("permafrost", "永冻", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "perm_frost"},
        ], ["冰霜"], "冰霜不再自然衰减"),
        ("freeze_all", "万冻", 1, 3, [
            {"type": 9, "target": 2, "base_value": 1, "status_id": "trigger_freeze"},
        ], ["冰霜"], "冻结所有敌人"),
        ("glacier", "冰川崩裂", 0, 3, [
            {"type": 0, "target": 2, "base_value": 15},
        ], ["冰霜"], "全体15点伤害"),
        ("frost_armor_mastery", "寒甲精通", 1, 2, [
            {"type": 1, "target": 0, "base_value": 18},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 2},
        ], ["冰霜"], "获得18点格挡，全体施加2层冰霜"),
        ("absolute_chill", "极寒", 0, 3, [
            {"type": 0, "target": 5, "base_value": 20},
            {"type": 5, "target": 5, "base_value": 1, "status_id": "frost", "status_stacks": 4},
        ], ["冰霜"], "对最前方敌人造成20点伤害，施加4层冰霜"),
        ("frost_explosion", "冰霜爆裂", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
            {"type": 9, "target": 1, "base_value": 1, "status_id": "frost_detonate"},
        ], ["冰霜"], "造成10点伤害，引爆冰霜层数"),
        ("north_wind", "北风", 1, 1, [
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 3},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["冰霜"], "全体施加3层冰霜，抽1张牌"),
        ("frozen_heart", "冰封之心", 2, 2, [
            {"type": 9, "target": 0, "base_value": 3, "status_id": "frost_buff_on_draw"},
        ], ["冰霜"], "抽牌时全体施加1层冰霜"),
        ("cryo_blast", "冷冻冲击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 15},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "frost", "status_stacks": 2},
        ], ["冰霜"], "造成15点伤害，施加2层冰霜"),
        ("everwinter", "永冬", 0, 4, [
            {"type": 0, "target": 2, "base_value": 20},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 4},
        ], ["冰霜"], "全体20点伤害，施加4层冰霜"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in rare:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 2, cost, effects, kws, desc))

    # ---- EPIC (6) ----
    epic = [
        ("polar_night", "极夜", 0, 3, [
            {"type": 0, "target": 2, "base_value": 18},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "frost", "status_stacks": 5},
        ], ["冰霜"], "全体18点伤害，施加5层冰霜（冻结）"),
        ("absolute_zero_field", "绝对零度领域", 1, 3, [
            {"type": 9, "target": 2, "base_value": 1, "status_id": "trigger_freeze"},
            {"type": 1, "target": 0, "base_value": 15},
        ], ["冰霜"], "冻结全体，获得15点格挡"),
        ("frost_giant", "冰霜巨人", 2, 3, [
            {"type": 9, "target": 0, "base_value": 20, "status_id": "summon_frost_giant"},
        ], ["冰霜"], "召唤冰霜巨人（20HP,10ATK）"),
        ("winter_kingdom", "冰封王国", 0, 4, [
            {"type": 0, "target": 2, "base_value": 25},
        ], ["冰霜"], "全体25点伤害"),
        ("subzero", "零度", 1, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "instant_freeze"},
        ], ["冰霜"], "下次冰霜攻击直接冻结"),
        ("cold_immunity", "寒冰免疫", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "cold_immunity"},
        ], ["冰霜"], "免疫寒冷系伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in epic:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 3, cost, effects, kws, desc))

    # ---- LEGENDARY (3) ----
    legendary = [
        ("eternal_frost", "永恒霜寒", 2, 3, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "eternal_frost"},
        ], ["冰霜"], "冰霜永不衰减，每层冰霜额外造成1点伤害"),
        ("queen_of_ice", "冰霜女王", 2, 4, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "ice_queen_passive"},
        ], ["冰霜"], "每回合自动施加2层冰霜于全体敌人"),
        ("world_freezer", "世界冻结", 0, 5, [
            {"type": 9, "target": 2, "base_value": 0, "status_id": "world_freeze"},
        ], ["冰霜"], "冻结全体敌人，造成30点伤害\n消耗"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in legendary:
        extra = {}
        if "world_freeze" in suffix or "world_freezer" in suffix:
            extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 4, cost, effects, kws, desc, extra))

    return dir_path, cards


def generate_wenjing_extra():
    """Generate ~55 cards for 温静 (wenjing)."""
    dir_path = os.path.join(CARDS_DIR, "wenjing")
    prefix = "wenjing"
    char = "温静"

    cards = []

    # ---- COMMON (20) ----
    common = [
        ("stab", "刺击", 0, 0, [
            {"type": 0, "target": 1, "base_value": 3},
        ], [], "造成3点伤害"),
        ("mark_strike", "标记打击", 0, 1, [
            {"type": 0, "target": 1, "base_value": 5},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 1},
        ], ["标记"], "造成5点伤害，施加标记"),
        ("double_cut", "双重切割", 0, 1, [
            {"type": 0, "target": 1, "base_value": 3, "repeat_count": 2},
        ], ["连击"], "造成3点伤害两次"),
        ("quick_dodge", "闪避", 1, 1, [
            {"type": 1, "target": 0, "base_value": 5},
            {"type": 2, "target": 0, "base_value": 1},
        ], [], "获得5点格挡，抽1张牌"),
        ("mark_dagger", "标记匕首", 0, 1, [
            {"type": 0, "target": 1, "base_value": 4},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 1},
        ], ["标记"], "造成4点伤害，施加标记"),
        ("keen_edge", "锋刃", 0, 1, [
            {"type": 0, "target": 1, "base_value": 7},
        ], [], "造成7点伤害"),
        ("quick_step", "疾步", 1, 1, [
            {"type": 1, "target": 0, "base_value": 4},
            {"type": 2, "target": 0, "base_value": 2},
        ], [], "获得4点格挡，抽2张牌"),
        ("fan_of_blades", "飞刃", 0, 1, [
            {"type": 0, "target": 3, "base_value": 4, "repeat_count": 2},
        ], [], "对随机敌人造成4点伤害两次"),
        ("mark_cut", "标记斩", 0, 2, [
            {"type": 0, "target": 1, "base_value": 8},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 2},
        ], ["标记"], "造成8点伤害，施加2层标记"),
        ("slash_and_roll", "斩击回旋", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
        ], [], "造成6点伤害"),
        ("prep_strike", "蓄势打击", 1, 1, [
            {"type": 4, "target": 0, "base_value": 2, "status_id": "strength", "status_stacks": 2},
        ], [], "获得2点力量"),
        ("triple_threat", "三连威胁", 0, 2, [
            {"type": 0, "target": 1, "base_value": 3, "repeat_count": 3},
        ], ["连击"], "造成3点伤害三次"),
        ("wind_slash", "风斩", 0, 1, [
            {"type": 0, "target": 1, "base_value": 5},
        ], [], "造成5点伤害"),
        ("retreat", "后撤", 1, 0, [
            {"type": 1, "target": 0, "base_value": 3},
            {"type": 2, "target": 0, "base_value": 1},
        ], [], "获得3点格挡，抽1张牌"),
        ("focused_strike", "专注一击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 12},
        ], ["精准"], "造成12点伤害"),
        ("mark_sweep", "横扫标记", 0, 2, [
            {"type": 0, "target": 2, "base_value": 5},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "mark", "status_stacks": 1},
        ], ["标记"], "全体5点伤害，施加标记"),
        ("shadow_blade", "影刃", 0, 1, [
            {"type": 0, "target": 1, "base_value": 4, "repeat_count": 2},
        ], ["连击"], "造成4点伤害两次"),
        ("cautious_stance", "谨慎姿态", 1, 1, [
            {"type": 1, "target": 0, "base_value": 8},
        ], [], "获得8点格挡"),
        ("quick_shot", "速射", 0, 1, [
            {"type": 0, "target": 3, "base_value": 5},
        ], [], "对随机敌人造成5点伤害"),
        ("piercing_stab", "穿刺", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
        ], [], "造成10点伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in common:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 0, cost, effects, kws, desc))

    # ---- UNCOMMON (16) ----
    uncommon = [
        ("burst_mark", "爆发标记", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
            {"type": 9, "target": 1, "base_value": 0, "status_id": "detonate_mark"},
        ], ["标记"], "造成10点伤害，引爆标记"),
        ("combo_strike", "连击突刺", 0, 2, [
            {"type": 0, "target": 1, "base_value": 5, "repeat_count": 2},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 1},
        ], ["连击", "标记"], "造成5点伤害两次，施加标记"),
        ("evasive_maneuver", "规避", 1, 1, [
            {"type": 1, "target": 0, "base_value": 6},
            {"type": 2, "target": 0, "base_value": 1},
        ], [], "获得6点格挡，抽1张牌"),
        ("critical_chance", "暴击蓄能", 1, 1, [
            {"type": 4, "target": 0, "base_value": 3, "status_id": "critical_rate", "status_stacks": 3},
        ], ["暴击"], "暴击率+3%"),
        ("soul_mark", "灵魂印记", 1, 1, [
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 3},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["标记"], "施加3层标记，抽1张牌"),
        ("blade_flurry", "剑刃乱舞", 0, 2, [
            {"type": 0, "target": 3, "base_value": 4, "repeat_count": 3},
        ], ["连击"], "对随机敌人造成4点伤害三次"),
        ("deadly_mark", "致命标记", 1, 1, [
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 4},
        ], ["标记"], "施加4层标记"),
        ("precise_strike", "精确打击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
            {"type": 4, "target": 0, "base_value": 2, "status_id": "critical_rate", "status_stacks": 2},
        ], ["暴击"], "造成10点伤害，暴击率+2%"),
        ("combo_prep", "连击准备", 1, 0, [
            {"type": 4, "target": 0, "base_value": 1, "status_id": "strength", "status_stacks": 1},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["连击"], "获得1点力量，抽1张牌"),
        ("mark_fan", "标记散射", 0, 2, [
            {"type": 0, "target": 2, "base_value": 6},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "mark", "status_stacks": 1},
        ], ["标记"], "全体6点伤害，施加标记"),
        ("critical_strike", "暴击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 0, "status_id": "critical_strike"},
        ], ["暴击"], "造成暴击（攻击力×2）"),
        ("shadow_veil", "暗影面纱", 1, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "dodge_next"},
        ], [], "下次攻击必闪避"),
        ("twin_fangs", "双牙", 0, 1, [
            {"type": 0, "target": 1, "base_value": 4, "repeat_count": 2},
        ], ["连击"], "造成4点伤害两次"),
        ("combo_boost", "连击增幅", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "combo_empower"},
        ], ["连击"], "连击额外造成2点伤害"),
        ("mark_refresh", "标记刷新", 1, 1, [
            {"type": 2, "target": 0, "base_value": 2},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "mark", "status_stacks": 1},
        ], ["标记"], "抽2张牌，全体施加标记"),
        ("quick_assess", "快速评估", 1, 0, [
            {"type": 2, "target": 0, "base_value": 2},
        ], [], "抽2张牌"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in uncommon:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 1, cost, effects, kws, desc))

    # ---- RARE (11) ----
    rare = [
        ("combo_chain", "连击链", 0, 3, [
            {"type": 0, "target": 1, "base_value": 6, "repeat_count": 3},
        ], ["连击"], "造成6点伤害三次"),
        ("mark_explosion_chain", "标记连锁", 0, 3, [
            {"type": 9, "target": 2, "base_value": 0, "status_id": "detonate_all_marks"},
        ], ["标记"], "引爆全体敌人的所有标记层数"),
        ("deadly_aim_mastery", "致命瞄准", 2, 2, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "crit_multiplier"},
        ], ["暴击"], "暴击伤害×2"),
        ("phantom_strike", "幻影突袭", 0, 3, [
            {"type": 0, "target": 1, "base_value": 5, "repeat_count": 4},
        ], ["连击"], "造成5点伤害四次"),
        ("mark_of_doom", "末日印记", 1, 2, [
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 5},
        ], ["标记"], "施加5层标记"),
        ("chain_kill", "连锁击杀", 0, 3, [
            {"type": 0, "target": 1, "base_value": 15},
            {"type": 9, "target": 1, "base_value": 0, "status_id": "chain_on_kill"},
        ], ["连击"], "造成15点伤害，击杀后随机攻击另一敌人"),
        ("mark_mastery", "标记专精", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "mark_mastery"},
        ], ["标记"], "标记造成伤害+3"),
        ("guranteed_crit", "必定暴击", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "guaranteed_crit"},
        ], ["暴击"], "下三次攻击必定暴击"),
        ("combo_overflow", "连击溢出", 2, 2, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "combo_overflow"},
        ], ["连击"], "连击计数超过阈值时额外抽1张牌"),
        ("shadow_master", "暗影大师", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "shadow_dodge_mastery"},
        ], [], "攻击后获得1层闪避"),
        ("lethal_combo", "致死连击", 0, 3, [
            {"type": 0, "target": 1, "base_value": 8, "repeat_count": 3},
        ], ["连击"], "造成8点伤害三次"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in rare:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 2, cost, effects, kws, desc))

    # ---- EPIC (5) ----
    epic = [
        ("mark_apocalypse", "标记天启", 0, 4, [
            {"type": 0, "target": 2, "base_value": 10},
            {"type": 9, "target": 2, "base_value": 0, "status_id": "detonate_all_marks"},
        ], ["标记"], "全体10点伤害，引爆全体标记"),
        ("combo_god", "连击之神", 2, 3, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "infinite_combo_god"},
        ], ["连击"], "连击无上限，每4连击额外攻击一次"),
        ("death_mark", "死亡标记", 0, 3, [
            {"type": 0, "target": 1, "base_value": 8},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "mark", "status_stacks": 5},
            {"type": 9, "target": 1, "base_value": 0, "status_id": "detonate_mark"},
        ], ["标记"], "造成8点伤害，施加5层标记后引爆"),
        ("shadow_realm", "暗影领域", 2, 3, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "shadow_realm_dodge"},
        ], [], "每回合自动获得1层闪避"),
        ("critical_overload", "暴击超载", 0, 4, [
            {"type": 0, "target": 2, "base_value": 25},
        ], [], "全体25点伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in epic:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 3, cost, effects, kws, desc))

    # ---- LEGENDARY (3) ----
    legendary = [
        ("phantom_combo", "幻影连击", 2, 3, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "phantom_combo"},
        ], ["连击"], "所有连击卡效果翻倍"),
        ("mark_of_eternity", "永恒印记", 1, 3, [
            {"type": 9, "target": 2, "base_value": 0, "status_id": "eternal_mark"},
        ], ["标记"], "标记永不消失，引爆后重新施加\n消耗"),
        ("assassin_legend", "暗杀传说", 0, 5, [
            {"type": 0, "target": 1, "base_value": 40},
        ], ["暴击"], "造成40点伤害（必定暴击）\n消耗"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in legendary:
        extra = {}
        if suffix in ("mark_of_eternity", "assassin_legend"):
            extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 4, cost, effects, kws, desc, extra))

    return dir_path, cards


def generate_shengyuan_extra():
    """Generate ~50 cards for 盛元 (shengyuan)."""
    dir_path = os.path.join(CARDS_DIR, "shengyuan")
    prefix = "shengyuan"
    char = "盛元"

    cards = []

    # ---- COMMON (19) ----
    common = [
        ("revenge_slash", "复仇斩", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
            {"type": 9, "target": 1, "base_value": 1, "status_id": "vengeance_damage"},
        ], ["复仇"], "造成6点伤害，附加复仇层数伤害"),
        ("blood_tap", "血之轻触", 1, 1, [
            {"type": 1, "target": 0, "base_value": 8},
            {"type": 0, "target": 0, "base_value": 2, "cost_hp": 2},
        ], ["血祭"], "消耗2HP，获得8点格挡"),
        ("heavy_blow", "重击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 12},
        ], [], "造成12点伤害"),
        ("blood_thirst", "嗜血", 1, 1, [
            {"type": 4, "target": 0, "base_value": 2, "status_id": "strength", "status_stacks": 2, "cost_hp": 3},
        ], ["血祭"], "消耗3HP，获得2点力量"),
        ("defend_stance", "防御姿态", 1, 1, [
            {"type": 1, "target": 0, "base_value": 6},
        ], [], "获得6点格挡"),
        ("vicious_strike", "恶毒打击", 0, 1, [
            {"type": 0, "target": 1, "base_value": 7},
        ], [], "造成7点伤害"),
        ("blood_strike", "血之打击", 0, 1, [
            {"type": 0, "target": 1, "base_value": 10, "cost_hp": 2},
        ], ["血祭"], "消耗2HP，造成10点伤害"),
        ("revenge_block", "复仇格挡", 1, 1, [
            {"type": 1, "target": 0, "base_value": 5},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "vengeance_stack"},
        ], ["复仇"], "获得5点格挡，复仇层数+1"),
        ("power_sacrifice", "力量牺牲", 1, 0, [
            {"type": 4, "target": 0, "base_value": 3, "status_id": "strength", "status_stacks": 3, "cost_hp": 3},
        ], ["血祭"], "消耗3HP，获得3点力量"),
        ("hardened_skin", "硬皮", 1, 1, [
            {"type": 1, "target": 0, "base_value": 7},
        ], [], "获得7点格挡"),
        ("fury_swing", "愤怒挥击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
            {"type": 9, "target": 1, "base_value": 1, "status_id": "vengeance_damage"},
        ], ["复仇"], "造成10点伤害，附加复仇层数伤害"),
        ("blood_letting", "放血", 0, 0, [
            {"type": 0, "target": 1, "base_value": 8, "cost_hp": 3},
        ], ["血祭"], "消耗3HP，造成8点伤害"),
        ("endure_hit", "承受", 1, 1, [
            {"type": 1, "target": 0, "base_value": 10, "cost_hp": 2},
        ], ["血祭"], "消耗2HP，获得10点格挡"),
        ("revenge_fuel", "复仇燃料", 1, 1, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "vengeance_stack"},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["复仇"], "复仇层数+2，抽1张牌"),
        ("wild_swing", "狂野挥击", 0, 2, [
            {"type": 0, "target": 2, "base_value": 6},
        ], [], "全体6点伤害"),
        ("blood_recovery", "血液回收", 1, 1, [
            {"type": 6, "target": 0, "base_value": 5, "cost_hp": 2},
        ], ["血祭"], "消耗2HP，回复5HP（净回复3HP）"),
        ("slash_and_bleed", "斩裂", 0, 1, [
            {"type": 0, "target": 1, "base_value": 5},
        ], [], "造成5点伤害"),
        ("shoulder_bash", "肩撞", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
            {"type": 1, "target": 0, "base_value": 3},
        ], [], "造成6点伤害，获得3点格挡"),
        ("life_for_power", "命换力", 1, 0, [
            {"type": 4, "target": 0, "base_value": 4, "status_id": "strength", "status_stacks": 4, "cost_hp": 5},
        ], ["血祭"], "消耗5HP，获得4点力量"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in common:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 0, cost, effects, kws, desc))

    # ---- UNCOMMON (13) ----
    uncommon = [
        ("blood_barrier", "血之障壁", 1, 2, [
            {"type": 1, "target": 0, "base_value": 15},
            {"type": 0, "target": 0, "base_value": 3, "cost_hp": 3},
        ], ["血祭"], "消耗3HP，获得15点格挡"),
        ("vengeful_rage", "复仇之怒", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "vengeance_on_hit"},
        ], ["复仇"], "每次受伤复仇+1"),
        ("blood_cleave", "血之横扫", 0, 2, [
            {"type": 0, "target": 2, "base_value": 8, "cost_hp": 3},
        ], ["血祭"], "消耗3HP，全体8点伤害"),
        ("revenge_armor", "复仇铠甲", 1, 2, [
            {"type": 1, "target": 0, "base_value": 10},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "vengeance_block"},
        ], ["复仇"], "获得10点格挡，格挡值附加复仇层数"),
        ("blood_drain", "血之汲取", 0, 2, [
            {"type": 0, "target": 1, "base_value": 12},
            {"type": 6, "target": 0, "base_value": 6},
        ], [], "造成12点伤害，回复6HP"),
        ("sacrificial_power", "祭力", 0, 2, [
            {"type": 0, "target": 1, "base_value": 16, "cost_hp": 4},
        ], ["血祭"], "消耗4HP，造成16点伤害"),
        ("bleed_out", "血流不止", 0, 1, [
            {"type": 0, "target": 1, "base_value": 8, "cost_hp": 2},
        ], ["血祭"], "消耗2HP，造成8点伤害"),
        ("revenge_reserve", "复仇储备", 1, 1, [
            {"type": 9, "target": 0, "base_value": 3, "status_id": "vengeance_stack"},
        ], ["复仇"], "复仇层数+3"),
        ("blood_armor", "血肉铠甲", 1, 2, [
            {"type": 1, "target": 0, "base_value": 12, "cost_hp": 3},
            {"type": 1, "target": 0, "base_value": 8},
        ], ["血祭"], "消耗3HP获得12点格挡+8点额外格挡"),
        ("pain_to_power", "苦痛之力", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "pain_to_strength"},
        ], ["血祭"], "每次血祭自伤获得1点力量"),
        ("soul_fuel", "灵魂燃料", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6, "cost_hp": 2},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["血祭"], "消耗2HP造成6伤，抽1张牌"),
        ("tough_skin", "坚韧皮肤", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "thorns_on_hit"},
        ], ["复仇"], "每次受伤反伤2点"),
        ("blood_revive", "血之复苏", 1, 1, [
            {"type": 6, "target": 0, "base_value": 10, "cost_hp": 4},
        ], ["血祭"], "消耗4HP，回复10HP（净回复6HP）"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in uncommon:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 1, cost, effects, kws, desc))

    # ---- RARE (10) ----
    rare = [
        ("extreme_sacrifice", "极限献祭", 1, 3, [
            {"type": 4, "target": 0, "base_value": 6, "status_id": "strength", "status_stacks": 6, "cost_hp": 8},
            {"type": 1, "target": 0, "base_value": 10},
        ], ["血祭"], "消耗8HP，获得6点力量和10点格挡"),
        ("vengeance_overflow", "复仇溢出", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "vengeance_overflow"},
        ], ["复仇"], "复仇超过10时，伤害翻倍"),
        ("blood_explosion", "血爆", 0, 3, [
            {"type": 0, "target": 2, "base_value": 12, "cost_hp": 5},
        ], ["血祭"], "消耗5HP，全体12点伤害"),
        ("undying_rage", "不灭之怒", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "undying_rage"},
        ], ["复仇"], "首次致命伤保留1HP"),
        ("blood_giant", "血之巨人", 2, 3, [
            {"type": 1, "target": 0, "base_value": 25, "cost_hp": 5},
            {"type": 4, "target": 0, "base_value": 4, "status_id": "strength", "status_stacks": 4},
        ], ["血祭"], "消耗5HP，获得25格挡和4力量"),
        ("final_revenge", "最终复仇", 0, 4, [
            {"type": 0, "target": 1, "base_value": 10},
            {"type": 9, "target": 1, "base_value": 3, "status_id": "vengeance_multiplier"},
        ], ["复仇"], "造成10+复仇×3伤害"),
        ("pact_of_blood", "血之契约", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "blood_pact_cost_reduce"},
        ], ["血祭"], "血祭自伤-3"),
        ("revenge_threshold", "复仇阈值", 2, 2, [
            {"type": 9, "target": 0, "base_value": 3, "status_id": "vengeance_floor"},
        ], ["复仇"], "复仇层数不低于3"),
        ("life_siphon", "生命虹吸", 0, 2, [
            {"type": 0, "target": 1, "base_value": 14},
            {"type": 6, "target": 0, "base_value": 7, "cost_hp": 2},
        ], ["血祭"], "消耗2HP，造成14伤害，回复7HP"),
        ("blood_moon", "血月", 2, 3, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "blood_moon_buff"},
        ], ["血祭"], "每回合开始血祭不消耗HP"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in rare:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 2, cost, effects, kws, desc))

    # ---- EPIC (5) ----
    epic = [
        ("blood_tsunami", "血之海啸", 0, 4, [
            {"type": 0, "target": 2, "base_value": 18, "cost_hp": 8},
        ], ["血祭"], "消耗8HP，全体18点伤害"),
        ("vengeance_avatar", "复仇化身", 2, 3, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "vengeance_avatar_epic"},
        ], ["复仇"], "复仇层数×2，每次复仇额外造成2点伤害"),
        ("sacrificial_altar", "牺牲祭坛", 1, 3, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "blood_to_power"},
            {"type": 0, "target": 0, "base_value": 10, "cost_hp": 10},
        ], ["血祭"], "消耗10HP，获得永久力量+2"),
        ("undying_legend", "不死传说", 2, 4, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "undying_legend"},
        ], ["复仇"], "死亡时100%复活，回复50%HP\n消耗"),
        ("hell_blood", "地狱之血", 0, 3, [
            {"type": 0, "target": 1, "base_value": 25, "cost_hp": 5},
            {"type": 4, "target": 0, "base_value": 3, "status_id": "strength", "status_stacks": 3},
        ], ["血祭"], "消耗5HP，造成25伤害，获得3力量"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in epic:
        extra = {}
        if suffix == "undying_legend":
            extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 3, cost, effects, kws, desc, extra))

    # ---- LEGENDARY (3) ----
    legendary = [
        ("eternal_revenge", "永恒复仇", 2, 3, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "eternal_revenge"},
        ], ["复仇"], "复仇层数永不消失，每层额外增加5%伤害"),
        ("blood_god", "血之神", 0, 5, [
            {"type": 0, "target": 2, "base_value": 30, "cost_hp": 10},
        ], ["血祭"], "消耗10HP，全体30点伤害"),
        ("immortal_sacrifice", "不朽牺牲", 1, 4, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "immortal_sacrifice"},
        ], ["血祭"], "血祭不再扣HP，改为扣格挡\n消耗"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in legendary:
        extra = {}
        if suffix == "immortal_sacrifice":
            extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 4, cost, effects, kws, desc, extra))

    return dir_path, cards


def generate_jinying_extra():
    """Generate ~50 cards for 金英 (jinying)."""
    dir_path = os.path.join(CARDS_DIR, "jinying")
    prefix = "jinying"
    char = "金英"

    cards = []

    # ---- COMMON (19) ----
    common = [
        ("healing_word", "治愈术", 1, 1, [
            {"type": 6, "target": 0, "base_value": 6},
        ], [], "回复6HP"),
        ("holy_light_strike", "圣光打击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 5, "status_id": "holy_damage"},
        ], ["神罚"], "造成5点神圣伤害"),
        ("protect", "护佑", 1, 1, [
            {"type": 1, "target": 0, "base_value": 6},
        ], [], "获得6点格挡"),
        ("small_blessing", "小祝福", 1, 1, [
            {"type": 6, "target": 4, "base_value": 3},
        ], ["亲和"], "全体回复3HP"),
        ("holy_touch", "圣洁触摸", 1, 0, [
            {"type": 6, "target": 0, "base_value": 3},
            {"type": 2, "target": 0, "base_value": 1},
        ], [], "回复3HP，抽1张牌"),
        ("light_strike", "光击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 6, "status_id": "holy_damage"},
        ], ["神罚"], "造成6点神圣伤害"),
        ("blessed_shield", "祝福之盾", 1, 2, [
            {"type": 1, "target": 0, "base_value": 10},
            {"type": 6, "target": 0, "base_value": 3},
        ], [], "获得10点格挡，回复3HP"),
        ("sacred_strike", "圣击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 7, "status_id": "holy_damage"},
        ], ["神罚"], "造成7点神圣伤害"),
        ("rejuvenation", "活力", 1, 1, [
            {"type": 6, "target": 0, "base_value": 8},
        ], [], "回复8HP"),
        ("divine_protection", "神圣庇护", 1, 2, [
            {"type": 1, "target": 0, "base_value": 12},
        ], [], "获得12点格挡"),
        ("holy_cleansing", "圣洁净化", 1, 1, [
            {"type": 6, "target": 0, "base_value": 4},
            {"type": 8, "target": 0, "base_value": 1},
        ], ["亲和"], "回复4HP，移除1层负面状态"),
        ("light_barrier", "光之障壁", 1, 2, [
            {"type": 1, "target": 0, "base_value": 8},
            {"type": 6, "target": 0, "base_value": 5},
        ], [], "获得8点格挡，回复5HP"),
        ("holy_mending", "神圣愈合", 1, 1, [
            {"type": 6, "target": 0, "base_value": 5},
        ], [], "回复5HP"),
        ("radiant_flash", "闪光", 0, 1, [
            {"type": 9, "target": 1, "base_value": 4, "status_id": "holy_damage"},
        ], ["神罚"], "造成4点神圣伤害"),
       ("group_heal", "群体治疗", 1, 2, [
            {"type": 6, "target": 4, "base_value": 4},
        ], ["亲和"], "全体回复4HP"),
        ("holy_armor", "圣光铠甲", 1, 2, [
            {"type": 1, "target": 0, "base_value": 9},
            {"type": 9, "target": 1, "base_value": 3, "status_id": "holy_damage"},
        ], ["神罚"], "获得9点格挡，造成3点神圣伤害"),
        ("healing_strike", "治愈打击", 0, 2, [
            {"type": 9, "target": 1, "base_value": 8, "status_id": "holy_damage"},
            {"type": 6, "target": 0, "base_value": 3},
        ], ["神罚"], "造成8点神圣伤害，回复3HP"),
        ("blessed_aegis", "祝福之盾", 1, 1, [
            {"type": 1, "target": 0, "base_value": 7},
            {"type": 6, "target": 0, "base_value": 2},
        ], [], "获得7点格挡，回复2HP"),
        ("divine_light", "神光", 0, 2, [
            {"type": 9, "target": 1, "base_value": 10, "status_id": "holy_damage"},
        ], ["神罚"], "造成10点神圣伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in common:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 0, cost, effects, kws, desc))

    # ---- UNCOMMON (13) ----
    uncommon = [
        ("holy_beam", "圣光射线", 0, 2, [
            {"type": 9, "target": 5, "base_value": 10, "status_id": "holy_damage"},
        ], ["神罚"], "对最前方敌人造成10点神圣伤害"),
        ("healing_circle", "治愈光环", 1, 2, [
            {"type": 6, "target": 4, "base_value": 6},
        ], ["亲和"], "全体回复6HP"),
        ("holy_charge", "神圣充能", 2, 1, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "holy_charge"},
        ], ["神罚"], "每回合获得2层神罚蓄能"),
        ("guardian_angel", "守护天使", 1, 2, [
            {"type": 6, "target": 0, "base_value": 12},
            {"type": 1, "target": 0, "base_value": 5},
        ], ["亲和"], "回复12HP，获得5点格挡"),
        ("holy_blade", "圣剑", 0, 2, [
            {"type": 9, "target": 1, "base_value": 12, "status_id": "holy_damage"},
        ], ["神罚"], "造成12点神圣伤害"),
        ("renewal", "焕新", 1, 1, [
            {"type": 6, "target": 0, "base_value": 10},
        ], [], "回复10HP"),
        ("divine_barrier", "神之障壁", 1, 3, [
            {"type": 1, "target": 4, "base_value": 8},
            {"type": 6, "target": 0, "base_value": 5},
        ], ["亲和"], "全体获得8点格挡，回复5HP"),
        ("holy_fire", "圣火", 0, 2, [
            {"type": 9, "target": 2, "base_value": 6, "status_id": "holy_damage"},
        ], ["神罚"], "全体6点神圣伤害"),
        ("heal_convert", "治愈转化", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "heal_to_strength"},
        ], ["亲和"], "每回复5HP获得1点力量"),
        ("sanctuary", "圣所", 1, 2, [
            {"type": 1, "target": 0, "base_value": 10},
            {"type": 6, "target": 0, "base_value": 8},
        ], ["亲和"], "获得10点格挡，回复8HP"),
        ("divine_strike", "神圣攻击", 0, 2, [
            {"type": 9, "target": 1, "base_value": 10, "status_id": "holy_damage"},
            {"type": 6, "target": 0, "base_value": 4},
        ], ["神罚"], "造成10点神圣伤害，回复4HP"),
        ("holy_infusion", "圣力灌注", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "holy_empower"},
        ], ["神罚"], "神圣伤害+3"),
        ("radiant_barrier", "光耀屏障", 1, 2, [
            {"type": 1, "target": 4, "base_value": 6},
            {"type": 9, "target": 2, "base_value": 3, "status_id": "holy_damage"},
        ], ["神罚"], "全体获得6点格挡，全体3点神圣伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in uncommon:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 1, cost, effects, kws, desc))

    # ---- RARE (10) ----
    rare = [
        ("judgment_strike", "审判打击", 0, 3, [
            {"type": 9, "target": 1, "base_value": 0, "status_id": "holy_retribution"},
        ], ["神罚"], "消耗神罚蓄能，每层造成3点伤害"),
        ("mass_heal", "大治愈", 1, 3, [
            {"type": 6, "target": 4, "base_value": 10},
        ], ["亲和"], "全体回复10HP"),
        ("holy_charge_exploit", "蓄能爆发", 0, 2, [
            {"type": 9, "target": 1, "base_value": 5, "status_id": "holy_damage", "repeat_count": 3},
        ], ["神罚"], "造成5点神圣伤害三次"),
        ("divine_wall", "神之壁垒", 1, 3, [
            {"type": 1, "target": 0, "base_value": 20},
            {"type": 6, "target": 0, "base_value": 10},
        ], ["亲和"], "获得20点格挡，回复10HP"),
        ("holy_martyr", "圣殉", 0, 2, [
            {"type": 9, "target": 2, "base_value": 10, "status_id": "holy_damage"},
            {"type": 6, "target": 4, "base_value": 5},
        ], ["神罚"], "全体10点神圣伤害，全体回复5HP"),
        ("light_of_dawn", "黎明之光", 1, 2, [
            {"type": 9, "target": 0, "base_value": 3, "status_id": "heal_over_time"},
        ], ["亲和"], "每回合回复3HP，持续3回合"),
        ("heavenly_protection", "天佑", 1, 2, [
            {"type": 1, "target": 0, "base_value": 15},
            {"type": 6, "target": 0, "base_value": 5},
            {"type": 8, "target": 0, "base_value": 1},
        ], ["亲和"], "获得15格挡，回复5HP，移除负面状态"),
        ("holy_overflow", "神圣溢出", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "holy_overflow"},
        ], ["神罚"], "过量治疗转化为格挡"),
        ("divine_retribution_touch", "神罚之触", 0, 1, [
            {"type": 9, "target": 1, "base_value": 4, "status_id": "holy_damage"},
        ], ["神罚"], "造成4点神圣伤害（每张神罚卡额外+1）"),
        ("sacred_shield_of_god", "神之盾", 1, 3, [
            {"type": 1, "target": 0, "base_value": 18},
            {"type": 9, "target": 1, "base_value": 8, "status_id": "holy_damage"},
        ], ["神罚"], "获得18格挡，造成8点神圣伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in rare:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 2, cost, effects, kws, desc))

    # ---- EPIC (5) ----
    epic = [
        ("holy_cataclysm", "神圣天灾", 0, 4, [
            {"type": 9, "target": 2, "base_value": 15, "status_id": "holy_damage"},
            {"type": 6, "target": 4, "base_value": 8},
        ], ["神罚"], "全体15点神圣伤害，全体回复8HP"),
        ("angelic_host", "天使军团", 2, 3, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "angelic_guardian"},
        ], ["亲和"], "每回合回复5HP，获得5点格挡"),
        ("divine_heal_nuke", "神愈核爆", 0, 4, [
            {"type": 9, "target": 2, "base_value": 20, "status_id": "holy_damage"},
        ], ["神罚"], "全体20点神圣伤害"),
        ("holy_sanctuary", "神圣避难所", 1, 3, [
            {"type": 1, "target": 4, "base_value": 15},
            {"type": 6, "target": 4, "base_value": 10},
        ], ["亲和"], "全体获得15格挡，全体回复10HP\n消耗"),
        ("light_of_purification", "净化之光", 0, 3, [
            {"type": 9, "target": 2, "base_value": 12, "status_id": "holy_damage"},
            {"type": 8, "target": 4, "base_value": 1},
        ], ["神罚"], "全体12点神圣伤害，移除负面状态"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in epic:
        extra = {}
        if suffix == "holy_sanctuary":
            extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 3, cost, effects, kws, desc, extra))

    # ---- LEGENDARY (3) ----
    legendary = [
        ("all_heal_doubled", "众生愈", 2, 4, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "double_healing"},
        ], ["亲和"], "所有治疗量翻倍\n消耗"),
        ("goddess_blessing", "女神祝福", 1, 4, [
            {"type": 6, "target": 0, "base_value": 30},
            {"type": 1, "target": 0, "base_value": 20},
            {"type": 9, "target": 2, "base_value": 10, "status_id": "holy_damage"},
        ], ["神罚"], "回复30HP，获得20格挡，全体10点神圣伤害"),
        ("holy_trinity", "神圣三位一体", 2, 5, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "holy_trinity"},
        ], ["神罚"], "回合结束：全体回复15HP，全体15点神圣伤害\n消耗"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in legendary:
        extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 4, cost, effects, kws, desc, extra))

    return dir_path, cards


def generate_hongfa_extra():
    """Generate ~50 cards for 红发 (hongfa)."""
    dir_path = os.path.join(CARDS_DIR, "hongfa")
    prefix = "hongfa"
    char = "红发"

    cards = []

    # ---- COMMON (19) ----
    common = [
        ("zombie_claw", "丧尸爪击", 0, 0, [
            {"type": 0, "target": 1, "base_value": 3},
        ], ["召唤"], "造成3点伤害"),
        ("raise_zombie_cheap", "低廉亡灵", 1, 0, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "召唤1只丧尸"),
        ("corpse_explosion", "尸爆", 0, 1, [
            {"type": 9, "target": 1, "base_value": 1, "status_id": "sacrifice_damage"},
        ], ["牺牲"], "牺牲1只丧尸造成6点伤害"),
        ("dark_mending", "暗黑治愈", 1, 1, [
            {"type": 9, "target": 0, "base_value": 4, "status_id": "dark_pact"},
        ], ["牺牲"], "牺牲1只丧尸，回复4HP"),
        ("zombie_assault", "丧尸突击", 0, 1, [
            {"type": 0, "target": 1, "base_value": 5},
        ], ["召唤"], "造成5点伤害"),
        ("undead_swing", "亡灵挥击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
        ], [], "造成10点伤害"),
        ("bone_shield", "骨盾", 1, 1, [
            {"type": 1, "target": 0, "base_value": 6},
        ], ["召唤"], "获得6点格挡"),
        ("fearful_gaze", "恐惧凝视", 1, 1, [
            {"type": 5, "target": 1, "base_value": 1, "status_id": "fear", "status_stacks": 1},
        ], ["牺牲"], "施加1层恐惧"),
        ("zombie_bite_weak", "丧尸噬咬", 0, 1, [
            {"type": 0, "target": 1, "base_value": 4},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "造成4点伤害，召唤1只丧尸"),
        ("dark_protection", "暗黑守护", 1, 2, [
            {"type": 1, "target": 0, "base_value": 10},
        ], [], "获得10点格挡"),
        ("summon_pair", "双亡灵", 1, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "召唤2只丧尸"),
        ("necrotic_touch", "死灵之触", 0, 1, [
            {"type": 0, "target": 1, "base_value": 5},
            {"type": 6, "target": 0, "base_value": 2},
        ], [], "造成5点伤害，回复2HP"),
        ("bone_bolt", "骨箭", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
        ], [], "造成6点伤害"),
        ("raise_zombie_army", "亡灵征兵", 1, 2, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "summon_zombie"},
        ], ["召唤"], "召唤2只丧尸"),
        ("fear_blast", "恐惧冲击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 6},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "fear", "status_stacks": 1},
        ], ["牺牲"], "造成6点伤害，施加1层恐惧"),
        ("zombie_body", "丧尸身躯", 1, 0, [
            {"type": 1, "target": 0, "base_value": 3},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "获得3点格挡，召唤1只丧尸"),
        ("necrotic_barrier", "亡者屏障", 1, 2, [
            {"type": 1, "target": 0, "base_value": 8},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "获得8点格挡，召唤1只丧尸"),
        ("dark_pact_lesser", "微弱契约", 1, 0, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "dark_pact"},
        ], ["牺牲"], "牺牲1只丧尸，回复2HP"),
        ("bone_strike", "骨击", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
            {"type": 1, "target": 0, "base_value": 2},
        ], [], "造成6点伤害，获得2点格挡"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in common:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 0, cost, effects, kws, desc))

    # ---- UNCOMMON (13) ----
    uncommon = [
        ("zombie_horde", "丧尸群", 1, 2, [
            {"type": 9, "target": 0, "base_value": 3, "status_id": "summon_zombie"},
        ], ["召唤"], "召唤3只丧尸"),
        ("sacrificial_detonation", "牺牲爆裂", 0, 2, [
            {"type": 9, "target": 2, "base_value": 1, "status_id": "sacrifice_all_damage"},
        ], ["牺牲"], "牺牲所有丧尸，每只造成5点全体伤害"),
        ("curse_of_weakness", "虚弱诅咒", 1, 1, [
            {"type": 5, "target": 2, "base_value": 1, "status_id": "weakness", "status_stacks": 2},
        ], ["牺牲"], "全体施加2层虚弱"),
        ("undead_strength", "亡灵之力", 1, 1, [
            {"type": 4, "target": 0, "base_value": 2, "status_id": "strength", "status_stacks": 2},
        ], ["召唤"], "每有一只丧尸获得1点力量"),
        ("zombie_copy", "丧尸复制", 1, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "copy_zombie"},
        ], ["召唤"], "复制1只丧尸"),
        ("dark_healing", "黑暗治愈", 1, 2, [
            {"type": 9, "target": 0, "base_value": 8, "status_id": "dark_pact"},
        ], ["牺牲"], "牺牲1只丧尸，回复8HP"),
        ("fear_aura_enhance", "恐惧光环强化", 2, 1, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "fear_aura"},
        ], ["牺牲"], "每回合开始全体施加1层恐惧"),
        ("undead_charge", "亡灵冲锋", 0, 2, [
            {"type": 0, "target": 1, "base_value": 8},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "造成8点伤害，召唤1只丧尸"),
        ("plague_strike", "瘟疫打击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 7},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "plague", "status_stacks": 2},
        ], ["牺牲"], "造成7点伤害，施加2层瘟疫"),
        ("sacrificial_energy", "牺牲能量", 1, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "dark_pact"},
            {"type": 3, "target": 0, "base_value": 1},
        ], ["牺牲"], "牺牲1只丧尸，获得1点能量"),
        ("undead_fortitude_buff", "亡灵坚韧", 2, 1, [
            {"type": 9, "target": 0, "base_value": 3, "status_id": "zombie_buff"},
        ], ["召唤"], "丧尸HP+3"),
        ("terrify", "恐吓", 1, 2, [
            {"type": 5, "target": 2, "base_value": 1, "status_id": "fear", "status_stacks": 2},
        ], ["牺牲"], "全体施加2层恐惧"),
        ("zombie_buff_strike", "亡灵强化", 0, 2, [
            {"type": 0, "target": 1, "base_value": 8},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "zombie_buff_damage"},
        ], ["召唤"], "造成8点伤害，每只丧尸+2伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in uncommon:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 1, cost, effects, kws, desc))

    # ---- RARE (10) ----
    rare = [
        ("zombie_explosion", "丧尸爆裂", 0, 3, [
            {"type": 9, "target": 2, "base_value": 8, "status_id": "sacrifice_all_damage"},
        ], ["牺牲"], "牺牲所有丧尸，每只造成8点全体伤害"),
        ("undead_king", "亡灵君王", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "zombie_king_buff"},
        ], ["召唤"], "丧尸ATK+3"),
        ("mass_terror", "群体恐惧", 1, 2, [
            {"type": 5, "target": 2, "base_value": 1, "status_id": "fear", "status_stacks": 3},
        ], ["牺牲"], "全体施加3层恐惧"),
        ("eternal_servitude", "永恒奴役", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "zombie_revive"},
        ], ["召唤"], "丧尸死亡时50%复活"),
        ("dark_summoner", "黑暗召唤师", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "double_summon"},
        ], ["召唤"], "召唤卡效果翻倍"),
        ("army_of_death", "死亡军团", 1, 3, [
            {"type": 9, "target": 0, "base_value": 4, "status_id": "summon_zombie"},
        ], ["召唤"], "召唤4只丧尸"),
        ("fear_exploitation", "恐惧利用", 0, 2, [
            {"type": 9, "target": 1, "base_value": 0, "status_id": "fear_damage"},
        ], ["牺牲"], "消耗恐惧层数造成伤害"),
        ("necromancy", "亡灵术", 1, 1, [
            {"type": 2, "target": 0, "base_value": 2},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "抽2张牌，召唤1只丧尸"),
        ("bone_armor_mastery", "骨甲精通", 1, 2, [
            {"type": 1, "target": 0, "base_value": 12},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_zombie"},
        ], ["召唤"], "获得12点格挡，召唤1只丧尸"),
        ("plague_master", "瘟疫大师", 0, 2, [
            {"type": 0, "target": 2, "base_value": 5},
            {"type": 5, "target": 2, "base_value": 1, "status_id": "plague", "status_stacks": 3},
        ], ["牺牲"], "全体5点伤害，施加3层瘟疫"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in rare:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 2, cost, effects, kws, desc))

    # ---- EPIC (5) ----
    epic = [
        ("undead_apocalypse", "亡灵天灾", 0, 4, [
            {"type": 0, "target": 2, "base_value": 10},
            {"type": 9, "target": 0, "base_value": 3, "status_id": "summon_zombie"},
        ], ["召唤"], "全体10点伤害，召唤3只丧尸"),
        ("soul_sacrifice", "灵魂献祭", 1, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "sacrifice_all_draw"},
        ], ["牺牲"], "牺牲所有丧尸，每只抽1张牌"),
        ("lich_king", "巫妖王", 2, 3, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "lich_passive"},
        ], ["召唤"], "每回合召唤2只丧尸"),
        ("fear_pocalypse", "恐惧末日", 0, 4, [
            {"type": 5, "target": 2, "base_value": 1, "status_id": "fear", "status_stacks": 5},
            {"type": 0, "target": 2, "base_value": 15},
        ], ["牺牲"], "全体5层恐惧，15点伤害"),
        ("undead_leviathan", "亡灵巨兽", 1, 4, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "summon_leviathan"},
        ], ["召唤"], "召唤亡灵巨兽（30HP,15ATK）"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in epic:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 3, cost, effects, kws, desc))

    # ---- LEGENDARY (3) ----
    legendary = [
        ("infinite_zombies", "无尽丧尸", 2, 4, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "infinite_zombies"},
        ], ["召唤"], "丧尸数量无上限\n消耗"),
        ("lich_eternal", "永恒巫妖", 2, 3, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "lich_eternal"},
        ], ["召唤"], "自己死亡时变为丧尸继续战斗"),
        ("undead_overlord", "亡灵霸主", 0, 5, [
            {"type": 9, "target": 0, "base_value": 6, "status_id": "summon_zombie"},
            {"type": 4, "target": 0, "base_value": 5, "status_id": "strength", "status_stacks": 5},
        ], ["召唤"], "召唤6只丧尸，获得5点力量\n消耗"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in legendary:
        extra = {}
        if suffix in ("infinite_zombies", "undead_overlord"):
            extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 4, cost, effects, kws, desc, extra))

    return dir_path, cards


def generate_lilian_extra():
    """Generate ~55 cards for 莉莲 (lilian)."""
    dir_path = os.path.join(CARDS_DIR, "lilian")
    prefix = "lilian"
    char = "莉莲"

    cards = []

    # ---- COMMON (20) ----
    common = [
        ("strike", "攻击", 0, 1, [
            {"type": 0, "target": 1, "base_value": 6},
        ], [], "造成6点伤害"),
        ("guard", "防御", 1, 1, [
            {"type": 1, "target": 0, "base_value": 6},
        ], [], "获得6点格挡"),
        ("dual_thrust", "双面刺击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 5, "status_id": "dual_attack"},
        ], ["战甲"], "攻击：5伤 / 防御：4伤+2甲"),
        ("heat_up", "升温", 1, 0, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_add"},
        ], ["战甲"], "过热度+1"),
        ("cool_down", "冷却", 1, 0, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_remove"},
        ], ["战甲"], "过热度-1"),
        ("knight_sweep", "骑士横扫", 0, 2, [
            {"type": 0, "target": 2, "base_value": 5},
        ], [], "全体5点伤害"),
        ("iron_wall", "铁壁", 1, 2, [
            {"type": 1, "target": 0, "base_value": 10},
        ], [], "获得10点格挡"),
        ("dual_mode_strike", "双模打击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 6, "status_id": "dual_strike"},
        ], ["战甲"], "攻击模式：6伤 / 防御模式：4伤+4甲"),
        ("heat_vent_small", "散热", 1, 1, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "overheat_remove"},
        ], ["战甲"], "过热度-2"),
        ("heavy_strike", "重斩", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
        ], [], "造成10点伤害"),
        ("defensive_stance", "防御态势", 1, 1, [
            {"type": 1, "target": 0, "base_value": 8},
        ], [], "获得8点格挡"),
        ("heated_strike", "过热打击", 0, 2, [
            {"type": 0, "target": 1, "base_value": 8},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_add"},
        ], ["战甲"], "造成8点伤害，过热度+1"),
        ("cooling_stance", "冷却姿态", 1, 1, [
            {"type": 1, "target": 0, "base_value": 4},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_remove"},
        ], ["战甲"], "获得4点格挡，过热度-1"),
        ("armor_touch", "甲触", 1, 0, [
            {"type": 1, "target": 0, "base_value": 3},
        ], [], "获得3点格挡"),
        ("quick_slash", "快速斩", 0, 1, [
            {"type": 0, "target": 1, "base_value": 5},
        ], [], "造成5点伤害"),
        ("dual_mode_guard", "双模防御", 1, 1, [
            {"type": 9, "target": 0, "base_value": 7, "status_id": "dual_defense"},
        ], ["战甲"], "攻击模式：4甲 / 防御模式：7甲"),
        ("battle_cry", "战吼", 0, 0, [
            {"type": 4, "target": 0, "base_value": 1, "status_id": "strength", "status_stacks": 1},
        ], [], "获得1点力量"),
        ("knight_protection", "骑士守护", 1, 2, [
            {"type": 1, "target": 0, "base_value": 7},
            {"type": 1, "target": 4, "base_value": 3},
        ], [], "获得7点格挡，全体获得3点格挡"),
        ("overheat_strike", "过载攻击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 3, "status_id": "overheat_attack"},
        ], ["战甲"], "过热度×3伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in common:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 0, cost, effects, kws, desc))

    # ---- UNCOMMON (16) ----
    uncommon = [
        ("mode_switch_attack", "切换攻击", 0, 1, [
            {"type": 9, "target": 1, "base_value": 0, "status_id": "mode_switch_attack"},
        ], ["战甲"], "切换模式后攻击，造成8点伤害"),
        ("fortress_barrier", "堡垒障壁", 1, 2, [
            {"type": 1, "target": 0, "base_value": 12},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "fortress_mode_boost"},
        ], ["战甲"], "获得12点格挡，防御模式格挡+3"),
        ("overheat_exploit", "过热利用", 0, 2, [
            {"type": 0, "target": 1, "base_value": 10},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_add"},
        ], ["战甲"], "造成10点伤害，过热度+1"),
        ("heat_to_power", "热能转力", 2, 1, [
            {"type": 9, "target": 0, "base_value": 2, "status_id": "heat_to_strength"},
        ], ["战甲"], "每点过热度获得1点力量"),
        ("assault_boost", "突击强化", 2, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "assault_upgrade"},
        ], ["战甲"], "攻击模式：伤害+3"),
        ("dual_enhance", "双面强化", 1, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "dual_enhance"},
        ], ["战甲"], "双面卡效果+20%"),
        ("thermal_vent", "散热口", 1, 2, [
            {"type": 9, "target": 0, "base_value": 3, "status_id": "overheat_remove"},
            {"type": 1, "target": 0, "base_value": 5},
        ], ["战甲"], "过热度-3，获得5点格挡"),
        ("knight_charge_boost", "骑士冲锋强化", 0, 2, [
            {"type": 0, "target": 1, "base_value": 8, "scale_stat": "strength"},
        ], [], "造成8(+力量)点伤害"),
        ("armor_refit", "装甲改装", 1, 1, [
            {"type": 1, "target": 0, "base_value": 8},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["战甲"], "获得8点格挡，抽1张牌"),
        ("heat_burst_mode", "热能爆发", 0, 2, [
            {"type": 9, "target": 1, "base_value": 10, "status_id": "dual_attack"},
        ], ["战甲"], "攻击模式：10伤 / 防御模式：6伤+5甲"),
        ("mode_tactics", "战术切换", 1, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "mode_switch_free"},
            {"type": 2, "target": 0, "base_value": 1},
        ], ["战甲"], "免费切换模式，抽1张牌"),
        ("overheat_protection", "过载保护", 1, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_cap_up"},
        ], ["战甲"], "过热度上限+3"),
        ("knight_vigor", "骑士活力", 1, 1, [
            {"type": 6, "target": 0, "base_value": 5},
            {"type": 4, "target": 0, "base_value": 1, "status_id": "strength", "status_stacks": 1},
        ], [], "回复5HP，获得1点力量"),
        ("precision_strike_mode", "模式精准打击", 0, 2, [
            {"type": 9, "target": 1, "base_value": 8, "status_id": "dual_strike"},
        ], ["战甲"], "攻击：8伤 / 防御：6伤+4甲"),
        ("iron_fortress", "钢铁堡垒", 1, 3, [
            {"type": 1, "target": 0, "base_value": 15},
        ], [], "获得15点格挡"),
        ("heat_conversion", "热量转化", 1, 1, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_remove"},
            {"type": 3, "target": 0, "base_value": 1},
        ], ["战甲"], "过热度-1，获得1点能量"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in uncommon:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 1, cost, effects, kws, desc))

    # ---- RARE (11) ----
    rare = [
        ("perfect_balance", "完美平衡", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "perfect_balance"},
        ], ["战甲"], "双面卡同时获得攻防效果"),
        ("heat_mastery", "过热精通", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "heat_mastery"},
        ], ["战甲"], "过热度不影响切换"),
        ("mode_switch_combo", "模式连击", 0, 3, [
            {"type": 0, "target": 1, "base_value": 12},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "mode_switch"},
        ], ["战甲"], "造成12点伤害，强制切换模式"),
        ("overheat_detonation", "过热引爆", 0, 2, [
            {"type": 9, "target": 1, "base_value": 0, "status_id": "overheat_detonation"},
        ], ["战甲"], "消耗过热度，每点造成3点伤害"),
        ("assault_mode_mastery", "突击精通", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "assault_mastery"},
        ], ["战甲"], "攻击模式：伤害+30%"),
        ("fortress_mode_mastery", "堡垒精通", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "fortress_mastery"},
        ], ["战甲"], "防御模式：格挡+30%"),
        ("knight_courage", "骑士勇气", 1, 2, [
            {"type": 1, "target": 4, "base_value": 8},
            {"type": 6, "target": 4, "base_value": 4},
        ], [], "全体获得8点格挡，全体回复4HP"),
        ("thermal_overload", "热能超载", 0, 3, [
            {"type": 0, "target": 1, "base_value": 15},
            {"type": 9, "target": 0, "base_value": 2, "status_id": "overheat_add"},
        ], ["战甲"], "造成15点伤害，过热度+2"),
        ("dual_perfection", "双面完美", 2, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "dual_perfection"},
        ], ["战甲"], "切换模式时抽1张牌"),
        ("armor_shatter", "碎甲", 0, 2, [
            {"type": 0, "target": 1, "base_value": 12},
            {"type": 5, "target": 1, "base_value": 1, "status_id": "vulnerable", "status_stacks": 2},
        ], [], "造成12点伤害，施加2层易伤"),
        ("heroic_strike", "英勇打击", 0, 3, [
            {"type": 0, "target": 1, "base_value": 18},
        ], [], "造成18点伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in rare:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 2, cost, effects, kws, desc))

    # ---- EPIC (5) ----
    epic = [
        ("perfect_form_attack", "完美攻击形态", 0, 3, [
            {"type": 0, "target": 2, "base_value": 15},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_add"},
        ], ["战甲"], "全体15点伤害，过热度+1"),
        ("perfect_form_defense", "完美防御形态", 1, 3, [
            {"type": 1, "target": 4, "base_value": 15},
            {"type": 9, "target": 0, "base_value": 1, "status_id": "overheat_remove"},
        ], ["战甲"], "全体获得15点格挡，过热度-1"),
        ("overheat_annihilation", "过热湮灭", 0, 4, [
            {"type": 9, "target": 2, "base_value": 0, "status_id": "overheat_annihilation"},
        ], ["战甲"], "消耗过热度，每点全体2点伤害"),
        ("third_mode", "第三形态", 2, 3, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "third_mode"},
        ], ["战甲"], "解锁第三形态：攻防一体\n消耗"),
        ("knight_legend", "骑士传说", 0, 4, [
            {"type": 0, "target": 1, "base_value": 25},
            {"type": 1, "target": 0, "base_value": 15},
        ], [], "造成25点伤害，获得15点格挡"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in epic:
        extra = {}
        if suffix == "third_mode":
            extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 3, cost, effects, kws, desc, extra))

    # ---- LEGENDARY (3) ----
    legendary = [
        ("unlocked_potential", "潜能解放", 2, 4, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "unlocked_potential"},
        ], ["战甲"], "双面卡获得双倍效果\n消耗"),
        ("all_mode_god", "全形态之神", 2, 5, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "all_mode_god"},
        ], ["战甲"], "同时拥有所有模式加成\n消耗"),
        ("eternal_armor", "永恒装甲", 1, 4, [
            {"type": 9, "target": 0, "base_value": 0, "status_id": "eternal_armor"},
        ], ["战甲"], "回合开始获得15点格挡\n消耗"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in legendary:
        extra = {"exhaust_on_use": True}
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 4, cost, effects, kws, desc, extra))

    return dir_path, cards


def generate_yemo_extra():
    """Generate 5 more cards for 叶默 (yemo)."""
    dir_path = os.path.join(CARDS_DIR, "yemo")
    prefix = "yemo"
    char = "叶默"

    cards = []

    # 2 common, 2 uncommon, 1 rare
    # Equipment/forge themed
    common = [
        ("quick_sharpen", "快速磨砺", 1, 0, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "forge_weapon"},
        ], ["锻造"], "为武器锻造+1"),
        ("nature_shield", "自然屏障", 1, 1, [
            {"type": 1, "target": 0, "base_value": 6},
            {"type": 9, "target": 1, "base_value": 1, "status_id": "thorn_damage"},
        ], ["荆棘"], "获得6格挡，造成1点荆棘伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in common:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 0, cost, effects, kws, desc))

    uncommon = [
        ("furnace_blade", "熔炉之刃", 0, 2, [
            {"type": 0, "target": 1, "base_value": 8},
            {"type": 9, "target": 1, "base_value": 1, "status_id": "burn", "status_stacks": 2},
        ], ["锻造"], "造成8点伤害，施加2层灼烧"),
        ("forge_armor", "锻造护甲", 3, 2, [
            {"type": 9, "target": 0, "base_value": 1, "status_id": "armor_slot"},
        ], ["锻造"], "装备：获得5点永久格挡"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in uncommon:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 1, cost, effects, kws, desc))

    rare = [
        ("thorn_forge_hybrid", "荆棘熔铸", 0, 3, [
            {"type": 0, "target": 2, "base_value": 6},
            {"type": 9, "target": 0, "base_value": 3, "status_id": "thorn_forge_synergy"},
        ], ["锻造", "荆棘"], "全体6点伤害，荆棘层数转化为伤害"),
    ]
    for suffix, name, ctype, cost, effects, kws, desc in rare:
        cards.append((f"{prefix}_{suffix}", name, char, ctype, 2, cost, effects, kws, desc))

    return dir_path, cards


def generate_all():
    generators = [
        generate_moye_extra,
        generate_wenjing_extra,
        generate_shengyuan_extra,
        generate_jinying_extra,
        generate_hongfa_extra,
        generate_lilian_extra,
        generate_yemo_extra,
    ]

    total = 0
    for gen in generators:
        dir_path, cards = gen()
        for card_data in cards:
            # Unpack: (prefix_suffix, name, char, ctype, rarity, cost, effects, kws, desc) or with extra_fields
            if len(card_data) == 10:
                card_id, name, char, ctype, rarity, cost, effects, kws, desc, extra = card_data
            else:
                card_id, name, char, ctype, rarity, cost, effects, kws, desc = card_data
                extra = None

            content = make_card(card_id, name, char, ctype, rarity, cost, effects, kws, desc, extra)
            write_card(dir_path, card_id, content)
            total += 1

    print(f"\n=== Total cards generated: {total} ===")


if __name__ == "__main__":
    generate_all()
