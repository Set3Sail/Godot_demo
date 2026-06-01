# scripts/data/event_data.gd
## 命运事件数据定义。
class_name EventData
extends Resource

enum EventType { FRIENDLY, RISKY, CURSE, SPECIAL }
enum EventChapter { CH1, CH2, CH3, CH4, CH5 }

@export var event_id: String = ""
@export var event_name: String = ""
@export var event_type: EventType = EventType.FRIENDLY
@export var chapter: EventChapter = EventChapter.CH1
@export var description: String = ""
@export var choices: Array[EventChoice] = []
@export var trigger_condition: String = ""  # 特殊触发条件（留空=无条件）
@export var can_repeat: bool = false
