"""
Shared helper functions used across the project.
"""

import math

import cv2


def clamp(value, minimum, maximum):
    """
    Keep a value inside a range.
    """
    return max(minimum, min(value, maximum))


def distance(point_a, point_b):
    """
    Euclidean distance between two 2D points.
    """
    return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def average_point(point_a, point_b):
    """
    Midpoint between two points.
    """
    return (
        int((point_a[0] + point_b[0]) / 2),
        int((point_a[1] + point_b[1]) / 2),
    )


def resize_and_crop_to_square(image, size):
    """
    Crop the center of an image to a square, then resize it.
    This avoids stretching the captured region.
    """
    height, width = image.shape[:2]
    side = min(width, height)

    start_x = (width - side) // 2
    start_y = (height - side) // 2
    square = image[start_y:start_y + side, start_x:start_x + side]

    return cv2.resize(square, (size, size))


def compute_capture_rectangle(hands):
    """
    Build a rectangle from the left-hand point to the right-hand point.

    To keep this robust, we sort hands by x-position on screen and use:
    - left-most hand as top-left guide
    - right-most hand as bottom-right guide
    """
    if len(hands) < 2:
        return None

    sorted_hands = sorted(hands, key=lambda hand: hand["pinch_point"][0])
    left_hand = sorted_hands[0]
    right_hand = sorted_hands[-1]

    x1 = min(left_hand["pinch_point"][0], right_hand["pinch_point"][0])
    y1 = min(left_hand["pinch_point"][1], right_hand["pinch_point"][1])
    x2 = max(left_hand["pinch_point"][0], right_hand["pinch_point"][0])
    y2 = max(left_hand["pinch_point"][1], right_hand["pinch_point"][1])

    return [x1, y1, x2, y2]


def ensure_minimum_rectangle(rect, frame_width, frame_height, min_size):
    """
    Make sure the capture rectangle never becomes too small.
    """
    x1, y1, x2, y2 = rect
    width = x2 - x1
    height = y2 - y1

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    width = max(width, min_size)
    height = max(height, min_size)

    half_width = width // 2
    half_height = height // 2

    x1 = clamp(center_x - half_width, 0, frame_width - 1)
    y1 = clamp(center_y - half_height, 0, frame_height - 1)
    x2 = clamp(center_x + half_width, 0, frame_width - 1)
    y2 = clamp(center_y + half_height, 0, frame_height - 1)

    return [x1, y1, x2, y2]


def smooth_rectangle(previous_rect, new_rect, alpha):
    """
    Smooth rectangle movement to reduce jitter.
    """
    if previous_rect is None:
        return new_rect

    smoothed = []
    for old_value, new_value in zip(previous_rect, new_rect):
        value = int((1 - alpha) * old_value + alpha * new_value)
        smoothed.append(value)

    return smoothed


def crop_region(frame, rect):
    """
    Crop a rectangle from the frame.
    """
    if rect is None:
        return None

    x1, y1, x2, y2 = rect
    x1 = clamp(x1, 0, frame.shape[1] - 1)
    y1 = clamp(y1, 0, frame.shape[0] - 1)
    x2 = clamp(x2, 0, frame.shape[1] - 1)
    y2 = clamp(y2, 0, frame.shape[0] - 1)

    if x2 <= x1 or y2 <= y1:
        return None

    return frame[y1:y2, x1:x2].copy()


def point_inside_rectangle(point, rect):
    """
    Check if a point is inside a rectangle.
    """
    x, y = point
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def get_slot_from_point(point, puzzle_origin, puzzle_size, rows, cols):
    """
    Convert a point to a puzzle slot index.
    """
    x, y = point
    origin_x, origin_y = puzzle_origin

    if (
        x < origin_x
        or y < origin_y
        or x >= origin_x + puzzle_size
        or y >= origin_y + puzzle_size
    ):
        return None

    tile_width = puzzle_size // cols
    tile_height = puzzle_size // rows

    col = (x - origin_x) // tile_width
    row = (y - origin_y) // tile_height

    return int(row * cols + col)


def get_slot_center(slot_index, puzzle_origin, puzzle_size, rows, cols):
    """
    Return the center point of a puzzle slot.
    """
    tile_width = puzzle_size // cols
    tile_height = puzzle_size // rows

    row = slot_index // cols
    col = slot_index % cols

    center_x = puzzle_origin[0] + col * tile_width + tile_width // 2
    center_y = puzzle_origin[1] + row * tile_height + tile_height // 2

    return center_x, center_y
