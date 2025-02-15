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


class CropmanAddPlaceholder(bpy.types.Operator):
    bl_idname = "cropman.add_placeholder"
    bl_label = "placeholderを追加"
    bl_description = "Crop範囲を表すplaceholderを追加します。"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print(f"{self.bl_idname}を実行しました。")
        return {"FINISHED"}


class CropmanCropAllPlaceholders(bpy.types.Operator):
    bl_idname = "cropman.crop_all_placeholder"
    bl_label = "全てのplaceholderを切り抜く"
    bl_description = "全てのplaceholderをCropしたstripに置き換えます。"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print(f"{self.bl_idname}を実行しました。")
        return {"FINISHED"}


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
        layout.operator(CropmanAddPlaceholder.bl_idname)
        layout.label(text="Crop操作")
        layout.operator(CropmanCropAllPlaceholders.bl_idname)


classes = [CropmanAddPlaceholder, CropmanCropAllPlaceholders, CropmanMainPanel]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    print(f"{bl_info['name']}が有効化されました")


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    print(f"{bl_info['name']}が無効化されました")
