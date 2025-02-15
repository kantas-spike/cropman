import bpy

bl_info = {
    "name": "Cropman",
    "description": "VSEで指定サイズにクロップしたtransformストリップを追加する。",
    "author": "kanta",
    "version": (0, 0),
    "blender": (4, 3, 0),
    "location": "VSE > Sidebar",
    "category": "Sequencer",
}


class CropmanMainPanel(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Cropman"
    bl_label = "Cropman"
    bl_idname = "CROPMAN_PT_MainPanel"

    @classmethod
    def poll(cls, context):
        return context.space_data.view_type == "SEQUENCER"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Crop対象ストリップの選択")
        layout.label(text="Placeholder操作")
        layout.label(text="Crop操作")


classes = [CropmanMainPanel]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    print(f"{bl_info['name']}が有効化されました")


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    print(f"{bl_info['name']}が無効化されました")
