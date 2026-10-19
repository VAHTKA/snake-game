import random
import tkinter as tk
from pathlib import Path

CELL = 20
COLS, ROWS = 30, 25
HUD = 40
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + HUD

BG_COLOR = "#111111"
GRID_COLOR = "#1a1a1a"
HUD_COLOR = "#0a0a0a"
HEAD_COLOR = "#7CFC00"
TAIL_COLOR = "#1e7a2a"
BALL_COLOR = "#ff3b3b"
BONUS_COLOR = "#ffd700"
WALL_COLOR = "#555566"
TEXT_COLOR = "white"
FONT = "Consolas"

DIFFICULTIES = [("Easy", 140), ("Normal", 100), ("Hard", 70)]
MIN_SPEED_MS = 45
SPEEDUP_PER_LEVEL = 8
BALLS_PER_LEVEL = 5
OBSTACLES_PER_LEVEL = 3
BONUS_CHANCE = 0.25
BONUS_TICKS = 50
BONUS_POINTS = 5

OPPOSITE = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
MOVES = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
WASD = {"w": "Up", "s": "Down", "a": "Left", "d": "Right"}

HIGHSCORE_FILE = Path(__file__).with_name("snake_highscore.txt")


def blend(c1, c2, t):
    """Mix two #rrggbb colours; t=0 gives c1, t=1 gives c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def load_highscore():
    try:
        return int(HIGHSCORE_FILE.read_text().strip())
    except (OSError, ValueError):
        return 0


def save_highscore(score):
    try:
        HIGHSCORE_FILE.write_text(str(score))
    except OSError:
        pass


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("Snake")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()
        root.bind("<Key>", self.on_key)

        self.draw_grid()
        self.highscore = load_highscore()
        self.difficulty = 1
        self.state = "menu"
        self.frame = 0
        self.reset()
        self.tick()

    # ---------- game state ----------

    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = "Right"
        self.dir_queue = []
        self.score = 0
        self.eaten = 0
        self.level = 1
        self.obstacles = set()
        self.bonus = None
        self.bonus_ticks = 0
        self.new_record = False
        self.ball = self.random_free_cell()

    @property
    def speed(self):
        base = DIFFICULTIES[self.difficulty][1]
        return max(MIN_SPEED_MS, base - (self.level - 1) * SPEEDUP_PER_LEVEL)

    def random_free_cell(self, avoid=()):
        taken = set(self.snake) | self.obstacles | set(avoid)
        taken.update(c for c in (getattr(self, "ball", None), self.bonus) if c)
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in taken]
        return random.choice(free) if free else None

    def add_obstacles(self):
        # Keep the path directly in front of the snake clear so new walls are never an instant death.
        hx, hy = self.snake[0]
        dx, dy = MOVES[self.direction]
        ahead = [(hx + dx * i, hy + dy * i) for i in range(1, 7)]
        for _ in range(OBSTACLES_PER_LEVEL):
            cell = self.random_free_cell(avoid=ahead)
            if cell:
                self.obstacles.add(cell)

    def start(self):
        self.reset()
        self.state = "playing"

    def end_game(self):
        self.state = "over"
        if self.score > self.highscore:
            self.highscore = self.score
            self.new_record = True
            save_highscore(self.score)

    # ---------- input ----------

    def on_key(self, event):
        key = WASD.get(event.keysym.lower(), event.keysym)

        if self.state == "menu":
            if key in ("Up", "Down"):
                step = -1 if key == "Up" else 1
                self.difficulty = (self.difficulty + step) % len(DIFFICULTIES)
            elif key in ("1", "2", "3"):
                self.difficulty = int(key) - 1
                self.start()
            elif key in ("space", "Return"):
                self.start()

        elif self.state == "playing":
            if key in MOVES:
                # Queue up to two turns so quick presses between ticks aren't lost.
                last = self.dir_queue[-1] if self.dir_queue else self.direction
                if key != last and key != OPPOSITE[last] and len(self.dir_queue) < 2:
                    self.dir_queue.append(key)
            elif key in ("p", "P", "Escape"):
                self.state = "paused"

        elif self.state == "paused":
            if key in ("p", "P", "Escape", "space"):
                self.state = "playing"

        elif self.state == "over":
            if key in ("space", "Return"):
                self.start()
            elif key in ("m", "M", "Escape"):
                self.state = "menu"

    # ---------- loop ----------

    def tick(self):
        self.frame += 1
        if self.state == "playing":
            self.step()
        self.draw()
        self.root.after(self.speed if self.state == "playing" else 100, self.tick)

    def step(self):
        if self.dir_queue:
            self.direction = self.dir_queue.pop(0)
        dx, dy = MOVES[self.direction]
        hx, hy = self.snake[0]
        head = (hx + dx, hy + dy)

        growing = head == self.ball
        hit_wall = not (0 <= head[0] < COLS and 0 <= head[1] < ROWS)
        # The tail moves away this tick, so it isn't a collision unless we're growing.
        body = self.snake if growing else self.snake[:-1]
        if hit_wall or head in body or head in self.obstacles:
            self.end_game()
            return

        self.snake.insert(0, head)

        if head == self.bonus:
            self.score += BONUS_POINTS
            self.bonus = None

        if growing:
            self.score += 1
            self.eaten += 1
            if self.eaten % BALLS_PER_LEVEL == 0:
                self.level += 1
                self.add_obstacles()
            self.ball = self.random_free_cell()
            if self.bonus is None and random.random() < BONUS_CHANCE:
                self.bonus = self.random_free_cell()
                self.bonus_ticks = BONUS_TICKS
        else:
            self.snake.pop()

        if self.bonus:
            self.bonus_ticks -= 1
            if self.bonus_ticks <= 0:
                self.bonus = None

        if self.ball is None:  # board full
            self.end_game()

    # ---------- drawing ----------

    def draw_grid(self):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HUD, fill=HUD_COLOR, outline="")
        for x in range(COLS + 1):
            c.create_line(x * CELL, HUD, x * CELL, HEIGHT, fill=GRID_COLOR)
        for y in range(ROWS + 1):
            c.create_line(0, HUD + y * CELL, WIDTH, HUD + y * CELL, fill=GRID_COLOR)

    def cell_box(self, x, y, pad=1):
        return (x * CELL + pad, HUD + y * CELL + pad,
                (x + 1) * CELL - pad, HUD + (y + 1) * CELL - pad)

    def text(self, x, y, s, size=14, color=TEXT_COLOR, bold=False, anchor="center"):
        font = (FONT, size, "bold") if bold else (FONT, size)
        self.canvas.create_text(x, y, text=s, fill=color, font=font, anchor=anchor, tags="dyn")

    def draw(self):
        c = self.canvas
        c.delete("dyn")

        if self.state == "menu":
            self.draw_menu()
            return

        for (x, y) in self.obstacles:
            c.create_rectangle(*self.cell_box(x, y, 0), fill=WALL_COLOR, outline="#333344", tags="dyn")

        if self.ball:
            c.create_oval(*self.cell_box(*self.ball, 3), fill=BALL_COLOR, outline="", tags="dyn")

        # Pulse, and blink during the last few ticks as a warning.
        if self.bonus and (self.bonus_ticks > 12 or self.frame % 2 == 0):
            pad = 1 if self.frame % 4 < 2 else 3
            c.create_oval(*self.cell_box(*self.bonus, pad), fill=BONUS_COLOR, outline="", tags="dyn")

        self.draw_snake()
        self.draw_hud()

        cx, cy = WIDTH // 2, HUD + (HEIGHT - HUD) // 2
        if self.state == "paused":
            self.text(cx, cy - 15, "PAUSED", 32, bold=True)
            self.text(cx, cy + 25, "Press P to resume")
        elif self.state == "over":
            c.create_rectangle(cx - 190, cy - 75, cx + 190, cy + 85, fill="#000000",
                               outline=BALL_COLOR, width=2, tags="dyn")
            self.text(cx, cy - 45, "GAME OVER", 32, BALL_COLOR, bold=True)
            self.text(cx, cy - 5, f"Score: {self.score}   Level: {self.level}", 16)
            if self.new_record:
                self.text(cx, cy + 22, "NEW HIGH SCORE!", 14, BONUS_COLOR, bold=True)
            self.text(cx, cy + 55, "Space: play again   M: menu", 12, "#aaaaaa")

    def draw_snake(self):
        c = self.canvas
        n = len(self.snake)
        for i in range(n - 1, -1, -1):
            x, y = self.snake[i]
            color = blend(HEAD_COLOR, TAIL_COLOR, i / max(1, n - 1))
            c.create_rectangle(*self.cell_box(x, y, 1 if i == 0 else 2), fill=color, outline="", tags="dyn")

        # Eyes, placed toward the direction of travel.
        hx, hy = self.snake[0]
        dx, dy = MOVES[self.direction]
        px, py = -dy, dx
        cx, cy = (hx + 0.5) * CELL, HUD + (hy + 0.5) * CELL
        for side in (-1, 1):
            ex = cx + dx * CELL * 0.2 + px * side * CELL * 0.22
            ey = cy + dy * CELL * 0.2 + py * side * CELL * 0.22
            c.create_oval(ex - 2.5, ey - 2.5, ex + 2.5, ey + 2.5, fill="black", outline="", tags="dyn")

    def draw_hud(self):
        y = HUD // 2
        self.text(10, y, f"Score: {self.score}", 14, bold=True, anchor="w")
        self.text(170, y, f"Level: {self.level}", 14, anchor="w")
        self.text(WIDTH - 10, y, f"Best: {self.highscore}", 14, BONUS_COLOR, anchor="e")
        if self.bonus:
            # Countdown bar for the bonus ball.
            x0, w = 300, 120
            frac = self.bonus_ticks / BONUS_TICKS
            self.canvas.create_rectangle(x0, y - 5, x0 + w, y + 5, outline=BONUS_COLOR, tags="dyn")
            self.canvas.create_rectangle(x0, y - 5, x0 + w * frac, y + 5, fill=BONUS_COLOR,
                                         outline="", tags="dyn")

    def draw_menu(self):
        cx = WIDTH // 2
        self.text(cx, 130, "SNAKE", 48, HEAD_COLOR, bold=True)
        self.text(cx, 185, f"High score: {self.highscore}", 14, BONUS_COLOR)
        for i, (name, _) in enumerate(DIFFICULTIES):
            selected = i == self.difficulty
            label = f"> {i + 1}. {name} <" if selected else f"{i + 1}. {name}"
            self.text(cx, 250 + i * 36, label, 18, HEAD_COLOR if selected else "#888888", bold=selected)
        self.text(cx, 390, "Up/Down to choose, Space to start", 12, "#aaaaaa")
        self.text(cx, 420, "Arrows/WASD move   P pause", 12, "#aaaaaa")
        self.text(cx, 450, "Red = 1 pt   Gold = 5 pts (hurry!)   Avoid grey walls", 12, "#aaaaaa")


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
