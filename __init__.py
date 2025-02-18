import bpy
import datetime
from . import utils

bl_info = {
    "name": "Cropman",
    "description": "Adds a transform strip cropped to the specified size.",
    "author": "kanta",
    "version": (0, 0, 1),
    "blender": (4, 3, 0),
    "location": "VSE > Sidebar",
    "category": "Sequencer",
}

ENUM_STRING_CACHE = {}

ID_NOT_SELECTED = "@@@not_selected@@@"


def is_placeholder(strip):
    if (
        strip.get(CUSTOM_KEY_GENERATER) == ADDON_NAME
        and strip.get(CUSTOM_KEY_STRIP_TYPE) == STRIP_TYPE_PLACEHOLDER
    ):
        return True
    else:
        return False


def is_addon_generated(strip):
    if strip.get(CUSTOM_KEY_GENERATER) == ADDON_NAME:
        return True
    else:
        return False


def strip_names_callback(self, context):
    items = [(ID_NOT_SELECTED, "Please select Strip Name ...", "not selected")]

    for seq in bpy.context.scene.sequence_editor.sequences:
        if is_placeholder(seq):
            continue

        # [(identifier, name, description, icon, number), ...]
        key = seq.name
        ENUM_STRING_CACHE.setdefault(key, key)
        items.append((key, f"{seq.type}: {seq.name}", f"{seq.type}: {seq.name}"))

    return items


class CropmanProperties(bpy.types.PropertyGroup):
    target_strip: bpy.props.EnumProperty(
        name="target strip",
        description="Cropping target",
        items=strip_names_callback,
        default=0,
    )  # type: ignore


DEFAULT_PLACEHOLDER_DURATION = 30
DEFAULT_PLACEHOLDER_CHANNEL_NO = 3
CUSTOM_KEY_GENERATER = "generated_by"
CUSTOM_KEY_STRIP_TYPE = "strip_type"
CUSTOM_KEY_PLACEHOLDER_ID = "placeholder_id"
ADDON_NAME = "cropman"
STRIP_TYPE_PLACEHOLDER = "placeholder"
STRIP_TYPE_CROPPED_TRANSFORM = "cropped_transform"


def guess_available_channel(frame_start, frame_end, target_channel, seqs):
    unavailable_channels = set()
    for seq in seqs:
        if seq.channel in unavailable_channels:
            continue
        elif (
            frame_start <= seq.frame_final_start < frame_end
            or frame_start <= seq.frame_final_end <= frame_end
        ):
            unavailable_channels.add(seq.channel)
        elif (
            seq.frame_final_start <= frame_start <= seq.frame_final_end
            and seq.frame_final_start <= frame_end <= seq.frame_final_end
        ):
            unavailable_channels.add(seq.channel)
    if target_channel not in unavailable_channels:
        return target_channel

    last_no = sorted(unavailable_channels)[-1]
    candidate = set(range(target_channel, last_no + 2))
    diff = sorted(candidate - unavailable_channels)
    # 使われていない最小のチャンネルを返す
    return diff[0]


class CropmanAddPlaceholder(bpy.types.Operator):
    bl_idname = "cropman.add_placeholder"
    bl_label = "Add a placeholder"
    bl_description = "Add a placeholder representing the crop range."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cur_frame = bpy.context.scene.frame_current
        seqs = bpy.context.scene.sequence_editor.sequences
        frame_end = cur_frame + DEFAULT_PLACEHOLDER_DURATION

        target_channel = guess_available_channel(
            cur_frame, frame_end, DEFAULT_PLACEHOLDER_CHANNEL_NO, seqs
        )

        placeholder_strip = seqs.new_effect(
            name=f"placeholder_{datetime.datetime.now().timestamp()}",
            type="COLOR",
            frame_start=cur_frame,
            frame_end=frame_end,
            channel=target_channel,
        )
        placeholder_strip.transform.scale_x = 0.2
        placeholder_strip.transform.scale_y = 0.3
        placeholder_strip.transform.origin[0] = 0
        placeholder_strip.transform.origin[1] = 1.0
        utils.move_center(placeholder_strip)
        placeholder_strip.color = (0, 0, 1)
        placeholder_strip.blend_alpha = 0.35
        placeholder_strip[CUSTOM_KEY_GENERATER] = ADDON_NAME
        placeholder_strip[CUSTOM_KEY_STRIP_TYPE] = STRIP_TYPE_PLACEHOLDER
        placeholder_strip[CUSTOM_KEY_PLACEHOLDER_ID] = placeholder_strip.name

        return {"FINISHED"}


def showMessageBox(message="", title="Message Box", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


class CropmanCropAllPlaceholders(bpy.types.Operator):
    bl_idname = "cropman.crop_all_placeholder"
    bl_label = "Crop all placeholders"
    bl_description = "Replace all placeholders with cropped strips."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cropman_props
        if props.target_strip == ID_NOT_SELECTED:
            showMessageBox(message="Please select the strip to be cropped!!")
        else:
            seqs = bpy.context.scene.sequence_editor.sequences
            placeholder_list = [s for s in seqs if is_placeholder(s)]
            target_strip = seqs.get(props.target_strip)
            for placeholder_strip in placeholder_list:
                charnnel_no = placeholder_strip.channel
                crop_info = utils.get_crop_info(placeholder_strip)
                seqs.remove(placeholder_strip)
                # transform stripを追加
                transform_strip = seqs.new_effect(
                    name=f"cropped_{datetime.datetime.now().timestamp()}",
                    type="TRANSFORM",
                    channel=charnnel_no,
                    frame_start=target_strip.frame_final_start,
                    seq1=target_strip,
                )
                transform_strip[CUSTOM_KEY_GENERATER] = ADDON_NAME
                transform_strip[CUSTOM_KEY_STRIP_TYPE] = STRIP_TYPE_CROPPED_TRANSFORM
                transform_strip[CUSTOM_KEY_PLACEHOLDER_ID] = transform_strip.name
                transform_strip.crop.min_x = crop_info.left
                transform_strip.crop.max_x = crop_info.right
                transform_strip.crop.max_y = crop_info.top
                transform_strip.crop.min_y = crop_info.bottom
                screen_rect = utils.get_screen_rect()
                transform_strip.transform.origin[0] = crop_info.left / screen_rect.w
                transform_strip.transform.origin[1] = (
                    screen_rect.h - crop_info.top
                ) / screen_rect.h
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
        box = layout.box()
        box.prop(props, "target_strip")
        layout.label(text="Placeholder:")
        box = layout.box()
        box.operator(CropmanAddPlaceholder.bl_idname)
        layout.label(text="Cropping:")
        box = layout.box()
        box.operator(CropmanCropAllPlaceholders.bl_idname)


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
    print(f"{bl_info['name']} has been activated")


def unregister():
    unregister_props()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    print(f"{bl_info['name']} has been deactivated")
