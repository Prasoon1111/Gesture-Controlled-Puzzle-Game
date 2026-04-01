"""
Drawing functions for the gesture-controlled UI.
"""

import cv2
import numpy as np


def draw_text_block(image, lines, origin=(16, 28), line_height=26):
    """
    Draw a small translucent instruction panel.
    """
    x, y = origin
    panel_width = 420
    panel_height = 18 + len(lines) * line_height

    overlay = image.copy()
    cv2.rectangle(
        overlay,
        (x - 10, y - 22),
        (x - 10 + panel_width, y - 22 + panel_height),
        (20, 20, 20),
        -1,
    )
    cv2.addWeighted(overlay, 0.45, image, 0.55, 0, image)

    current_y = y
    for line in lines:
        cv2.putText(
            image,
            line,
            (x, current_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        current_y += line_height


def draw_white_flash(image, strength=0.28):
    """
    Draw a quick white flash for capture feedback.
    """
    overlay = np.full_like(image, 255)
    cv2.addWeighted(overlay, strength, image, 1 - strength, 0, image)


def draw_solved_glow(image, strength=0.14):
    """
    Add a soft green success glow.
    """
    overlay = image.copy()
    overlay[:, :] = (80, 180, 80)
    cv2.addWeighted(overlay, strength, image, 1 - strength, 0, image)


def draw_hand_points(image, hands):
    """
    Draw fingertip markers for all visible hands.
    """
    for hand in hands:
        pinch_color = (80, 255, 80) if hand.get("pinching", False) else (0, 255, 0)
        cv2.circle(image, hand["thumb_tip"], 8, (0, 180, 255), -1)
        cv2.circle(image, hand["index_tip"], 8, (255, 220, 0), -1)
        cv2.circle(image, hand["pinch_point"], 7, pinch_color, -1)
        cv2.putText(
            image,
            hand["label"],
            (hand["pinch_point"][0] + 8, hand["pinch_point"][1] - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )


def draw_capture_rectangle(image, rect, hand_count, dual_pinch_active):
    """
    Draw the dynamic capture box with state-based colors.
    """
    if rect is None:
        return

    x1, y1, x2, y2 = rect

    if hand_count >= 2:
        color = (80, 220, 80)
    elif hand_count == 1:
        color = (0, 220, 255)
    else:
        color = (0, 0, 255)

    if dual_pinch_active:
        color = (255, 255, 255)

    cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)

    overlay = image.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    fill_alpha = 0.22 if dual_pinch_active else 0.12
    cv2.addWeighted(overlay, fill_alpha, image, 1 - fill_alpha, 0, image)


def get_capture_status_text(capture_ready, dual_pinch_active):
    """
    Helper text for the capture stage.
    """
    if dual_pinch_active:
        return "Dual pinch detected"
    if capture_ready:
        return "Both hands found - pinch both hands to capture"
    return "Show both hands to build the capture box"


def draw_capture_screen(
    frame,
    hands,
    capture_rect,
    hand_count,
    dual_pinch_active,
    grid_rows,
    grid_cols,
    status_text,
):
    """
    Draw the live camera feed with capture helpers.
    """
    screen = frame.copy()
    draw_capture_rectangle(screen, capture_rect, hand_count, dual_pinch_active)
    draw_hand_points(screen, hands)

    if dual_pinch_active:
        draw_white_flash(screen, strength=0.12)

    draw_text_block(
        screen,
        [
            "Use both hands to resize capture box",
            "Pinch BOTH hands to capture",
            "Pinch to pick and move tiles",
            "Press R to restart | Press Q to quit",
            f"Grid: {grid_rows} x {grid_cols}",
            status_text,
        ],
    )
    return screen


def draw_grid_lines(image, puzzle_origin, puzzle_size, rows, cols):
    """
    Draw puzzle grid lines.
    """
    origin_x, origin_y = puzzle_origin
    tile_width = puzzle_size // cols
    tile_height = puzzle_size // rows

    for col in range(cols + 1):
        x = origin_x + col * tile_width
        cv2.line(image, (x, origin_y), (x, origin_y + puzzle_size), (255, 255, 255), 2)

    for row in range(rows + 1):
        y = origin_y + row * tile_height
        cv2.line(image, (origin_x, y), (origin_x + puzzle_size, y), (255, 255, 255), 2)


def draw_board_background(image, puzzle_origin, puzzle_size):
    """
    Draw a soft panel behind the puzzle.
    """
    x, y = puzzle_origin
    overlay = image.copy()
    cv2.rectangle(
        overlay,
        (x - 10, y - 10),
        (x + puzzle_size + 10, y + puzzle_size + 10),
        (30, 30, 30),
        -1,
    )
    cv2.addWeighted(overlay, 0.55, image, 0.45, 0, image)


def draw_puzzle_tiles(image, tiles, board, puzzle_origin, puzzle_size, rows, cols, hidden_slot=None):
    """
    Draw the current puzzle layout.
    """
    origin_x, origin_y = puzzle_origin
    tile_width = puzzle_size // cols
    tile_height = puzzle_size // rows

    for slot_index, tile_index in enumerate(board):
        if hidden_slot is not None and slot_index == hidden_slot:
            continue

        row = slot_index // cols
        col = slot_index % cols
        x1 = origin_x + col * tile_width
        y1 = origin_y + row * tile_height
        x2 = x1 + tile_width
        y2 = y1 + tile_height

        tile = cv2.resize(tiles[tile_index], (tile_width, tile_height))
        image[y1:y2, x1:x2] = tile


def draw_selected_slot(image, slot_index, puzzle_origin, puzzle_size, rows, cols):
    """
    Highlight the tile slot currently being dragged from.
    """
    if slot_index is None:
        return

    origin_x, origin_y = puzzle_origin
    tile_width = puzzle_size // cols
    tile_height = puzzle_size // rows
    row = slot_index // cols
    col = slot_index % cols

    x1 = origin_x + col * tile_width
    y1 = origin_y + row * tile_height
    x2 = x1 + tile_width
    y2 = y1 + tile_height

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), 4)


def draw_pick_progress(image, slot_index, puzzle_origin, puzzle_size, rows, cols, progress):
    """
    Show the short hold-to-pick progress on a tile.
    """
    if slot_index is None or progress <= 0:
        return

    origin_x, origin_y = puzzle_origin
    tile_width = puzzle_size // cols
    tile_height = puzzle_size // rows
    row = slot_index // cols
    col = slot_index % cols
    x1 = origin_x + col * tile_width
    y1 = origin_y + row * tile_height

    bar_x1 = x1 + 8
    bar_x2 = x1 + tile_width - 8
    bar_y1 = y1 + 8
    bar_y2 = bar_y1 + 8

    fill_width = max(1, int((bar_x2 - bar_x1) * min(progress, 1.0)))

    cv2.rectangle(image, (bar_x1, bar_y1), (bar_x2, bar_y2), (40, 40, 40), -1)
    cv2.rectangle(image, (bar_x1, bar_y1), (bar_x1 + fill_width, bar_y2), (0, 255, 255), -1)


def draw_drag_tile(image, tile_image, drag_position, puzzle_size, rows, cols):
    """
    Draw the tile that is currently being moved by a pinch gesture.
    """
    if tile_image is None or drag_position is None:
        return

    tile_width = puzzle_size // cols
    tile_height = puzzle_size // rows
    tile = cv2.resize(tile_image, (tile_width, tile_height))

    x = int(drag_position[0] - tile_width / 2)
    y = int(drag_position[1] - tile_height / 2)

    x = max(0, min(image.shape[1] - tile_width, x))
    y = max(0, min(image.shape[0] - tile_height, y))

    overlay = image.copy()
    overlay[y:y + tile_height, x:x + tile_width] = tile
    cv2.addWeighted(overlay, 0.88, image, 0.12, 0, image)
    cv2.rectangle(image, (x, y), (x + tile_width, y + tile_height), (0, 255, 255), 3)


def draw_solved_banner(image):
    """
    Draw a success message after the puzzle is completed.
    """
    text = "Puzzle Solved!"
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
    text_width, text_height = text_size

    x = (image.shape[1] - text_width) // 2
    y = 44 + text_height

    overlay = image.copy()
    cv2.rectangle(
        overlay,
        (x - 18, y - text_height - 14),
        (x + text_width + 18, y + 14),
        (30, 150, 30),
        -1,
    )
    cv2.addWeighted(overlay, 0.55, image, 0.45, 0, image)

    cv2.putText(
        image,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


def draw_puzzle_screen(
    frame,
    hands,
    tiles,
    board,
    rows,
    cols,
    puzzle_size,
    puzzle_origin,
    drag_tile,
    drag_position,
    selected_slot,
    candidate_slot,
    pinch_progress,
    solved,
    capture_flash_active,
    solved_flash_active,
):
    """
    Draw the puzzle mode screen.
    """
    screen = frame.copy()

    dim_overlay = np.zeros_like(screen)
    cv2.addWeighted(dim_overlay, 0.28, screen, 0.72, 0, screen)

    draw_board_background(screen, puzzle_origin, puzzle_size)
    draw_puzzle_tiles(
        screen,
        tiles,
        board,
        puzzle_origin,
        puzzle_size,
        rows,
        cols,
        hidden_slot=selected_slot if drag_tile is not None else None,
    )
    draw_grid_lines(screen, puzzle_origin, puzzle_size, rows, cols)
    draw_selected_slot(screen, selected_slot, puzzle_origin, puzzle_size, rows, cols)
    draw_pick_progress(
        screen,
        candidate_slot,
        puzzle_origin,
        puzzle_size,
        rows,
        cols,
        pinch_progress,
    )

    if drag_tile is not None:
        draw_drag_tile(screen, tiles[drag_tile], drag_position, puzzle_size, rows, cols)

    draw_hand_points(screen, hands)
    draw_text_block(
        screen,
        [
            "Pinch to pick and move tiles",
            "Hold pinch briefly to pick a tile",
            "Release pinch to drop tile",
            "Press R to restart | Press Q to quit",
        ],
    )

    if capture_flash_active:
        draw_white_flash(screen, strength=0.24)

    if solved_flash_active:
        draw_solved_glow(screen, strength=0.16)

    if solved:
        draw_solved_banner(screen)

    return screen
