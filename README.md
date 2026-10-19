# Snake Game

A classic Snake game written in Python with `tkinter`. Steer the green snake, eat the red balls, and avoid the walls and your own tail.

## Features

- **Three difficulty levels:** Easy, Normal and Hard
- **Levels:** every 5 balls you eat, the snake gets faster and new wall blocks appear
- **Gold bonus ball:** worth 5 points, but it disappears after a short time
- **High score:** saved between games
- **Pause and resume** at any time
- **Responsive controls:** quick key presses are buffered, so fast turns aren't lost
- Dark theme with a grid, a colour-gradient snake and a top bar showing score, level and best score

## Requirements

- Python 3.8 or newer
- `tkinter`, which comes with the standard Python installers for Windows and macOS. On Linux you may need to install it separately, for example `sudo apt install python3-tk`.

You don't need any other packages.

## How to run

```bash
git clone https://github.com/VAHTKA/snake-game.git
cd snake-game
python snake-game.py
```

## Controls

| Key | Action |
| --- | --- |
| Arrow keys / WASD | Move |
| Up / Down, then Space | Choose difficulty and start (or press 1, 2 or 3) |
| P / Esc | Pause or resume |
| Space | Play again after game over |
| M | Return to the menu after game over |

## Scoring

| Item | Points |
| --- | --- |
| Red ball | 1 |
| Gold ball | 5 |

Hitting a wall, a grey block or your own body ends the game.

## Customising

You can change the settings at the top of `snake-game.py`, such as `DIFFICULTIES`, `BALLS_PER_LEVEL`, `OBSTACLES_PER_LEVEL`, `BONUS_CHANCE`, and the board size (`COLS` and `ROWS`).
