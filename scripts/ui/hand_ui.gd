# scripts/ui/hand_ui.gd
## 手牌区 UI 控制器。挂载到 HandArea (HBoxContainer) 节点。
## 监听 CardManager 信号，动态创建/销毁 CardWidget。
class_name HandUI
extends HBoxContainer

var _card_mgr: CardManager
var _widgets: Array[CardWidget] = []
var _selected_card: CardData = null

var _card_widget_scene: PackedScene = preload("res://scenes/ui/card_widget.tscn")


func setup(card_manager: CardManager) -> void:
	_card_mgr = card_manager
	_connect_signals()


func _connect_signals() -> void:
	if not _card_mgr:
		return
	_card_mgr.card_drawn.connect(_on_cards_drawn)
	_card_mgr.card_played.connect(_on_card_played)
	_card_mgr.card_discarded.connect(_on_card_discarded)
	_card_mgr.card_exhausted.connect(_on_card_discarded)
	_card_mgr.hand_emptied.connect(_clear_all)


func _on_cards_drawn(card: CardData, count: int) -> void:
	# 直接全量重建（简单但可靠）
	_rebuild_hand()


func _on_card_played(card: CardData, target: Node) -> void:
	_rebuild_hand()
	_select_card(null)


func _on_card_discarded(card: CardData) -> void:
	_rebuild_hand()


func _clear_all() -> void:
	for w in _widgets:
		if is_instance_valid(w):
			w.queue_free()
	_widgets.clear()
	_select_card(null)


func _rebuild_hand() -> void:
	_clear_all()
	if not _card_mgr:
		return
	for card in _card_mgr.hand:
		var widget: CardWidget = _card_widget_scene.instantiate()
		widget.setup(card)
		widget.card_clicked.connect(_on_card_widget_clicked)
		add_child(widget)
		_widgets.append(widget)


func _on_card_widget_clicked(card: CardData) -> void:
	if _selected_card == card:
		_select_card(null)  # 再次点击取消选中
	else:
		_select_card(card)


func _select_card(card: CardData) -> void:
	_selected_card = card
	for w in _widgets:
		if is_instance_valid(w):
			w.set_selected(w.card_data == card)


func get_selected_card() -> CardData:
	return _selected_card
