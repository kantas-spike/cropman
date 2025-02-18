import bpy
from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int


# (crop_left, crop_right, crop_top, crop_bottom)
@dataclass(frozen=True)
class CropInfo:
    left: int
    right: int
    top: int
    bottom: int


def get_screen_rect() -> Rect:
    render = bpy.context.scene.render
    width = render.resolution_x * (render.resolution_percentage / 100)
    height = render.resolution_y * (render.resolution_percentage / 100)
    return Rect(0, 0, round(width), round(height))


def get_crop_info(placeholder_strip) -> CropInfo:
    screen_rect = get_screen_rect()
    strip_origin = placeholder_strip.transform.origin
    strip_w = screen_rect.w * placeholder_strip.transform.scale_x
    strip_h = screen_rect.h * placeholder_strip.transform.scale_y
    global_origin_x = (
        screen_rect.w * strip_origin[0] + placeholder_strip.transform.offset_x
    )
    global_origin_y = (
        screen_rect.h * strip_origin[1] + placeholder_strip.transform.offset_y
    )
    strip_l = global_origin_x - (strip_w * strip_origin[0])
    strip_b = global_origin_y - (strip_h * strip_origin[1])

    # (crop_left, crop_right, crop_top, crop_bottom)
    crop_info = [
        strip_l,
        screen_rect.w - (strip_l + strip_w),
        screen_rect.h - (strip_b + strip_h),
        strip_b,
    ]
    return CropInfo(*[round(elm) for elm in crop_info])


def move_center(strip):
    screen_rect = get_screen_rect()
    strip_origin = strip.transform.origin
    strip_w = screen_rect.w * strip.transform.scale_x
    strip_h = screen_rect.h * strip.transform.scale_y
    global_origin_x = screen_rect.w * strip_origin[0] + strip.transform.offset_x
    global_origin_y = screen_rect.h * strip_origin[1] + strip.transform.offset_y
    screen_center_x = screen_rect.w / 2
    screen_center_y = screen_rect.h / 2
    strip.transform.offset_x += (
        screen_center_x - global_origin_x - (0.5 - strip_origin[0]) * strip_w
    )
    strip.transform.offset_y += (
        screen_center_y - global_origin_y - (0.5 - strip_origin[1]) * strip_h
    )
