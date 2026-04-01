"""
Puzzle logic for creating and checking the tile board.
"""

import random

import cv2

from utils import resize_and_crop_to_square


def split_image(image, rows, cols):
    """
    Split an image into equal tiles.
    """
    tiles = []
    tile_height = image.shape[0] // rows
    tile_width = image.shape[1] // cols

    for row in range(rows):
        for col in range(cols):
            x1 = col * tile_width
            y1 = row * tile_height
            x2 = x1 + tile_width
            y2 = y1 + tile_height
            tiles.append(image[y1:y2, x1:x2].copy())

    return tiles


def create_shuffled_board(tile_count):
    """
    Create a shuffled list of tile indexes.
    """
    board = list(range(tile_count))
    correct_board = list(range(tile_count))

    while True:
        random.shuffle(board)
        if board != correct_board:
            break

    return board, correct_board


def create_puzzle_data(image, rows, cols, puzzle_size):
    """
    Resize the captured image and prepare all puzzle data.
    """
    prepared = resize_and_crop_to_square(image, puzzle_size)
    tiles = split_image(prepared, rows, cols)
    board, correct_board = create_shuffled_board(len(tiles))

    return {
        "image": prepared,
        "tiles": tiles,
        "board": board,
        "correct_board": correct_board,
    }


def place_tile(board, source_slot, target_slot):
    """
    Move the dragged tile to a target slot.

    If the target slot already has a tile, the tiles are swapped.
    """
    if source_slot is None or target_slot is None:
        return

    board[source_slot], board[target_slot] = board[target_slot], board[source_slot]


def check_win(current_board, correct_board):
    """
    Return True when every tile is back in the correct position.
    """
    return current_board == correct_board
