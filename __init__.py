bl_info = {
    "name": "Cropman",
    "description": "VSEで指定サイズにクロップしたtransformストリップを追加する。",
    "author": "kanta",
    "version": (0, 0),
    "blender": (4, 3, 0),
    "location": "VSE > Sidebar",
    "category": "Sequencer",
}


def register():
    print(f"{bl_info['name']}が有効化されました")


def unregister():
    print(f"{bl_info['name']}が無効化されました")
