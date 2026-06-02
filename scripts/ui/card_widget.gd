# scripts/ui/card_widget.gd
## 单张卡牌的 UI 组件。由 HandUI 动态创建和管理。
class_name CardWidget
extends Control

var card_data: CardData

signal card_clicked(card: CardData)


func setup(card: CardData) -> void:
	card_data = card
	_refresh_display()


func set_selected(selected: bool) -> void:
	if selected:
		modulate = Color(1.2, 1.2, 0.8, 1.0)  # 高亮偏金色
	else:
		modulate = Color.WHITE


func _refresh_display() -> void:
	# 子节点名称约定: CostLabel, NameLabel, DescLabel, TypeBg
	var cost_label: Label = _get_child_or_null("CostLabel")
	var name_label: Label = _get_child_or_null("NameLabel")
	var desc_label: Label = _get_child_or_null("DescLabel")
	var type_bg: ColorRect = _get_child_or_null("TypeBg")

	if cost_label:
		cost_label.text = str(card_data.cost)

	if name_label:
		name_label.text = card_data.card_name

	if desc_label:
		desc_label.text = card_data.description

	if type_bg:
		type_bg.color = _color_for_type(card_data.card_type)


func _get_child_or_null(node_name: String) -> Node:
	if has_node(node_name):
		return get_node(node_name)
	return null


func _color_for_type(card_type: int) -> Color:
	match card_type:
		CardData.CardType.ATTACK:
			return Color(0.8, 0.2, 0.2, 0.6)   # 红色
		CardData.CardType.SKILL:
			return Color(0.2, 0.5, 0.8, 0.6)   # 蓝色
		CardData.CardType.ABILITY:
			return Color(0.8, 0.7, 0.1, 0.6)   # 金色
		CardData.CardType.EQUIPMENT:
			return Color(0.5, 0.5, 0.5, 0.6)   # 灰色
	return Color(0.3, 0.3, 0.3, 0.6)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		card_clicked.emit(card_data)
		accept_event()
