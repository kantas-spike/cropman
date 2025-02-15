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


class CropmanProperties(bpy.types.PropertyGroup):
    target_strip: bpy.props.EnumProperty(
        name="target strip",
        description="Crop対象のstrip",
        items=[
            (
                "unselected",
                "  ",
                "未選択",
            ),
            ("a", "A", "あ"),
            ("b", "B", "い"),
        ],  # [(identifier, name, description, icon, number), ...]
        default=0,
    )  # type: ignore


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
        props = context.scene.cropman_props
        layout = self.layout
        layout.label(text="Crop対象ストリップの選択")
        layout.prop(props, "target_strip")
        layout.label(text="Placeholder操作")
        layout.operator(CropmanAddPlaceholder.bl_idname)
        layout.label(text="Crop操作")
        layout.operator(CropmanCropAllPlaceholders.bl_idname)


def register_props():
    bpy.types.Scene.cropman_props = bpy.props.PointerProperty(type=CropmanProperties)


def unregister_props():
    del bpy.types.Scene.cropman_props


classes = [
    CropmanProperties,
    CropmanAddPlaceholder,
    CropmanCropAllPlaceholders,
    CropmanMainPanel,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    register_props()
    print(f"{bl_info['name']}が有効化されました")


def unregister():
    unregister_props()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    print(f"{bl_info['name']}が無効化されました")
