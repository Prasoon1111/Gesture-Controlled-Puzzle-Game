"""
MediaPipe hand tracking logic.
"""

import cv2
import mediapipe as mp

from utils import average_point


class HandTracker:
    """
    Small wrapper around MediaPipe Hands to keep main.py clean.
    """

    def __init__(self, detection_confidence=0.6, tracking_confidence=0.6):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def process(self, frame):
        """
        Detect hands and return useful fingertip information in pixels.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        detected_hands = []

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return detected_hands

        frame_height, frame_width = frame.shape[:2]

        for landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):
            thumb_tip_landmark = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
            index_tip_landmark = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

            thumb_tip = (
                int(thumb_tip_landmark.x * frame_width),
                int(thumb_tip_landmark.y * frame_height),
            )
            index_tip = (
                int(index_tip_landmark.x * frame_width),
                int(index_tip_landmark.y * frame_height),
            )

            detected_hands.append(
                {
                    "label": handedness.classification[0].label,
                    "thumb_tip": thumb_tip,
                    "index_tip": index_tip,
                    "pinch_point": average_point(thumb_tip, index_tip),
                }
            )

        return detected_hands

    def close(self):
        """
        Release MediaPipe resources.
        """
        self.hands.close()
