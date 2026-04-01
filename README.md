# Live Gesture-Controlled Puzzle Game

## Project Overview
This project is a polished beginner-friendly puzzle game built with Python, OpenCV, NumPy, MediaPipe Hands, and Pygame.

The webcam stays live the whole time. First, you use both hands to create a dynamic capture box. When both hands pinch at the same time, the selected region is captured automatically. That image becomes a shuffled puzzle, and you solve it by pinching to pick up tiles and releasing to drop them.

## Features
- Live webcam feed with proper camera aspect ratio
- Two-hand dynamic capture rectangle
- Smooth resizing of the capture region
- Minimum box size to prevent accidental collapse
- Dual-pinch capture with no keyboard needed for taking the image
- Capture cooldown to avoid repeated triggers
- Color-based capture box feedback
- Quick capture flash animation
- Puzzle board generated from the captured image
- Configurable grid size such as `3 x 3` or `4 x 3`
- Stable pinch detection using a threshold buffer
- Short hold-to-pick timing to reduce accidental tile selection
- Gesture-based pick and place for puzzle tiles
- Highlighted tile slot and pickup progress bar
- Sound effects for capture, pick, drop, and puzzle completion
- Restart support with the `R` key
- Win detection with a success banner and sound

## Project Structure
- `main.py` - Main application loop and game state management
- `hand_tracker.py` - MediaPipe Hands tracking logic
- `puzzle.py` - Puzzle image splitting, shuffling, and win checking
- `gestures.py` - Pinch detection, dual-pinch detection, and drag-drop tile control
- `ui.py` - Visual drawing for overlays, puzzle board, instructions, and flashes
- `utils.py` - Helper functions used across the app
- `sound.py` - Generated sound effects using `pygame.mixer`
- `requirements.txt` - Python dependencies

## Installation Steps
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## How to Run
Start the game with:

```bash
python main.py
```

## Controls
- `Show both hands` - Create and resize the capture box
- `Pinch BOTH hands` - Capture the selected region and create the puzzle
- `Pinch over a tile` - Start selecting a tile
- `Hold pinch briefly` - Confirm tile pickup
- `Move while pinching` - Drag the tile
- `Release pinch` - Drop the tile into a slot
- `R` - Restart the game and return to capture mode
- `Q` - Quit the application

## How the Capture Box Works
- The game looks for two hands.
- The left-most visible hand helps define the top-left area.
- The right-most visible hand helps define the bottom-right area.
- The rectangle is smoothed so it does not jitter too much.
- The box is green with two hands, yellow with one hand, and red when no hands define a box.
- Pinching with both hands captures the image automatically.
- A short cooldown prevents repeated captures.

## How the Gesture Puzzle Works
- MediaPipe tracks the thumb tip and index finger tip.
- When those two points get close enough, the game treats it as a pinch.
- Pinch detection uses a small threshold buffer for smoother behavior.
- Pinching over a tile for a short moment selects it.
- Releasing the pinch drops the tile into the nearest slot.
- If the target slot already contains a tile, the tiles swap positions.
- The game plays simple sound effects for capture, tile actions, and success.

```python
GRID_ROWS = 3
GRID_COLS = 3
PUZZLE_SIZE = 400
```

Examples:
- `3 x 3` for an easier puzzle
- `4 x 3` for a harder puzzle

## Notes
- Good lighting helps MediaPipe detect both hands more reliably.
- Keep both hands clearly visible during capture mode.
- During puzzle mode, pinch over the puzzle area so the tile can be selected correctly.
- If your system has no available audio device, the game still runs without sound.

## Connect with Me

Feel free to reach out for collaborations, projects, or just a chat!

* Email: **[rprasoon11@gmail.com](mailto:rprasoon11@gmail.com)**
* LinkedIn: **https://linkedin.com/in/prasoon-ranjan-2049572b0**

---

## Contributing

Feel free to fork this repo and improve it!

---

## Show Your Support

If you like this project, give it a on GitHub!

---
