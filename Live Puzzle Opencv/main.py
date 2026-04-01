"""
Live Gesture-Controlled Puzzle Game

Main responsibilities:
1. Open the webcam
2. Track both hands with MediaPipe
3. Build a dynamic capture rectangle from two hands
4. Capture the selected region with a dual-pinch gesture
5. Show a centered puzzle board
6. Let the user pick and place tiles with a pinch gesture
"""

import random
import time

import cv2

from gestures import PinchController, detect_dual_pinch, detect_pinch
from hand_tracker import HandTracker
from puzzle import check_win, create_puzzle_data
from sound import (
    play_capture_sound,
    play_drop_sound,
    play_pick_sound,
    play_win_sound,
)
from ui import draw_capture_screen, draw_puzzle_screen, get_capture_status_text
from utils import (
    compute_capture_rectangle,
    crop_region,
    ensure_minimum_rectangle,
    smooth_rectangle,
)


WINDOW_NAME = "Live Gesture-Controlled Puzzle Game"
GRID_ROWS = 3
GRID_COLS = 3
PUZZLE_SIZE = 400
MIN_CAPTURE_SIZE = 160
CAPTURE_SMOOTHING = 0.25
CAPTURE_COOLDOWN_SECONDS = 1.5
CAPTURE_FLASH_DURATION = 0.18
SOLVED_FLASH_DURATION = 0.6


def capture_image(frame, capture_rect):
    """
    Capture only the selected camera region.
    """
    region = crop_region(frame, capture_rect)
    if region is None or region.size == 0:
        return None
    return region


def split_image(image, rows, cols):
    """
    Keep a small helper that returns puzzle tiles from the captured image.
    """
    puzzle_data = create_puzzle_data(image, rows, cols, PUZZLE_SIZE)
    return puzzle_data["tiles"]


def shuffle_tiles(tiles, rows, cols):
    """
    Return a shuffled board and the correct board layout.
    """
    tile_count = len(tiles)
    correct_board = list(range(tile_count))
    board = correct_board.copy()

    while board == correct_board:
        random.shuffle(board)

    return board, correct_board


def handle_mouse_click(event, x, y, flags, param):
    """
    Mouse is not used in the gesture version, but the function remains
    here to keep the structure beginner-friendly.
    """
    return None


def check_capture_ready(hands):
    """
    The capture box needs two visible hands.
    """
    return len(hands) >= 2


def build_capture_state(frame, hands, smoothed_rect):
    """
    Calculate the current capture rectangle using both hands.
    """
    capture_rect = smoothed_rect
    capture_ready = check_capture_ready(hands)

    if capture_ready:
        raw_rect = compute_capture_rectangle(hands)
        if raw_rect is not None:
            raw_rect = ensure_minimum_rectangle(
                raw_rect,
                frame.shape[1],
                frame.shape[0],
                MIN_CAPTURE_SIZE,
            )
            capture_rect = smooth_rectangle(smoothed_rect, raw_rect, CAPTURE_SMOOTHING)

    return capture_ready, capture_rect


def reset_game_state():
    """
    Create the default game state.
    """
    return {
        "mode": "capture",
        "capture_rect": None,
        "puzzle_data": None,
        "board": None,
        "correct_board": None,
        "solved": False,
        "last_capture_time": 0.0,
        "capture_flash_until": 0.0,
        "solved_flash_until": 0.0,
        "solved_sound_played": False,
    }


def main():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open webcam.")
        return

    tracker = HandTracker()
    pinch_controller = PinchController(hold_frames=6)
    game = reset_game_state()

    while True:
        now = time.time()
        success, frame = camera.read()
        if not success:
            print("Error: Could not read frame from webcam.")
            break

        # Mirror the frame so movement feels natural on screen.
        frame = cv2.flip(frame, 1)

        hands = tracker.process(frame)
        for hand in hands:
            hand["pinching"] = detect_pinch(hand)

        if game["mode"] == "capture":
            capture_ready, capture_rect = build_capture_state(
                frame,
                hands,
                game["capture_rect"],
            )
            game["capture_rect"] = capture_rect

            dual_pinch_active = detect_dual_pinch(hands)
            can_trigger_capture = (
                capture_ready
                and capture_rect is not None
                and dual_pinch_active
                and now - game["last_capture_time"] >= CAPTURE_COOLDOWN_SECONDS
            )

            if can_trigger_capture:
                captured_image = capture_image(frame, capture_rect)
                if captured_image is not None:
                    game["puzzle_data"] = create_puzzle_data(
                        captured_image,
                        GRID_ROWS,
                        GRID_COLS,
                        PUZZLE_SIZE,
                    )
                    game["board"] = game["puzzle_data"]["board"]
                    game["correct_board"] = game["puzzle_data"]["correct_board"]
                    game["solved"] = check_win(
                        game["board"],
                        game["correct_board"],
                    )
                    game["mode"] = "puzzle"
                    game["last_capture_time"] = now
                    game["capture_flash_until"] = now + CAPTURE_FLASH_DURATION
                    game["solved_sound_played"] = False
                    pinch_controller.reset()
                    play_capture_sound()

            screen = draw_capture_screen(
                frame=frame,
                hands=hands,
                capture_rect=capture_rect,
                hand_count=len(hands),
                dual_pinch_active=dual_pinch_active,
                grid_rows=GRID_ROWS,
                grid_cols=GRID_COLS,
                status_text=get_capture_status_text(capture_ready, dual_pinch_active),
            )
        else:
            puzzle_origin = (
                (frame.shape[1] - PUZZLE_SIZE) // 2,
                (frame.shape[0] - PUZZLE_SIZE) // 2,
            )

            interaction_event = pinch_controller.update(
                hands=hands,
                board=game["board"],
                puzzle_origin=puzzle_origin,
                puzzle_size=PUZZLE_SIZE,
                rows=GRID_ROWS,
                cols=GRID_COLS,
            )

            if interaction_event == "pick":
                play_pick_sound()
            elif interaction_event == "drop":
                play_drop_sound()

            game["solved"] = check_win(game["board"], game["correct_board"])
            if game["solved"] and not game["solved_sound_played"]:
                game["solved_sound_played"] = True
                game["solved_flash_until"] = now + SOLVED_FLASH_DURATION
                play_win_sound()

            screen = draw_puzzle_screen(
                frame=frame,
                hands=hands,
                tiles=game["puzzle_data"]["tiles"],
                board=game["board"],
                rows=GRID_ROWS,
                cols=GRID_COLS,
                puzzle_size=PUZZLE_SIZE,
                puzzle_origin=puzzle_origin,
                drag_tile=pinch_controller.drag_tile,
                drag_position=pinch_controller.drag_position,
                selected_slot=pinch_controller.source_slot,
                candidate_slot=pinch_controller.candidate_slot,
                pinch_progress=pinch_controller.candidate_frames
                / pinch_controller.hold_frames,
                solved=game["solved"],
                capture_flash_active=now < game["capture_flash_until"],
                solved_flash_active=now < game["solved_flash_until"],
            )

        cv2.imshow(WINDOW_NAME, screen)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key == ord("r"):
            game = reset_game_state()
            pinch_controller.reset()
            continue

    tracker.close()
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
