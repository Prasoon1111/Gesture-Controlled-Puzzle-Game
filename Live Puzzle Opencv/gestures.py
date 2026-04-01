"""
Gesture helpers for capture and tile interaction.
"""

from puzzle import place_tile
from utils import distance, get_slot_from_point


PINCH_START_DISTANCE = 34
PINCH_RELEASE_DISTANCE = 46


def detect_pinch(hand_landmarks):
    """
    Detect a pinch with a small distance buffer.

    This makes the pinch state more stable than using one threshold for
    both starting and releasing the gesture.
    """
    pinch_distance = distance(
        hand_landmarks["thumb_tip"],
        hand_landmarks["index_tip"],
    )
    previous_state = hand_landmarks.get("pinching", False)

    if previous_state:
        return pinch_distance < PINCH_RELEASE_DISTANCE

    return pinch_distance < PINCH_START_DISTANCE


def detect_dual_pinch(hands):
    """
    Return True when both detected hands are pinching together.
    """
    pinching_hands = [hand for hand in hands if hand.get("pinching", False)]
    return len(pinching_hands) >= 2


class PinchController:
    """
    Manage a gesture-driven tile pick, drag, and drop flow.
    """

    def __init__(self, hold_frames=6):
        self.hold_frames = hold_frames
        self.drag_tile = None
        self.drag_position = None
        self.source_slot = None
        self.active_hand_label = None
        self.candidate_slot = None
        self.candidate_frames = 0

    def reset(self):
        """
        Clear the current drag state.
        """
        self.drag_tile = None
        self.drag_position = None
        self.source_slot = None
        self.active_hand_label = None
        self.candidate_slot = None
        self.candidate_frames = 0

    def _find_active_hand(self, hands):
        """
        Keep following the same pinching hand while dragging if possible.
        """
        pinching_hands = [hand for hand in hands if hand.get("pinching", False)]

        if self.active_hand_label is not None:
            for hand in pinching_hands:
                if hand["label"] == self.active_hand_label:
                    return hand

        if pinching_hands:
            return pinching_hands[0]

        return None

    def _update_candidate(self, slot):
        """
        Require the pinch to stay over the same slot for a few frames
        before picking up a tile.
        """
        if slot is None:
            self.candidate_slot = None
            self.candidate_frames = 0
            return False

        if self.candidate_slot == slot:
            self.candidate_frames += 1
        else:
            self.candidate_slot = slot
            self.candidate_frames = 1

        return self.candidate_frames >= self.hold_frames

    def update(self, hands, board, puzzle_origin, puzzle_size, rows, cols):
        """
        Update the tile interaction state.

        Returns:
            str | None: "pick", "drop", or None for no event.
        """
        active_hand = self._find_active_hand(hands)

        if self.drag_tile is None:
            if active_hand is None:
                self._update_candidate(None)
                return None

            slot = get_slot_from_point(
                active_hand["pinch_point"],
                puzzle_origin,
                puzzle_size,
                rows,
                cols,
            )

            ready_to_pick = self._update_candidate(slot)
            if not ready_to_pick:
                return None

            self.drag_tile = board[slot]
            self.source_slot = slot
            self.drag_position = active_hand["pinch_point"]
            self.active_hand_label = active_hand["label"]
            self.candidate_slot = None
            self.candidate_frames = 0
            return "pick"

        if active_hand is not None:
            self.drag_position = active_hand["pinch_point"]
            return None

        target_slot = get_slot_from_point(
            self.drag_position,
            puzzle_origin,
            puzzle_size,
            rows,
            cols,
        )

        if target_slot is None:
            target_slot = self.source_slot

        place_tile(board, self.source_slot, target_slot)
        self.reset()
        return "drop"
