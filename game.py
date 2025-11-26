from pgzrun import go
from pygame import Rect

WIDTH = 1300
HEIGHT = 700
TILE = 32

game_state = "menu"
sound_on = True
win = False

music.play("back_music")
music.set_volume(0.2)
sounds.walk.set_volume(0.3)
sounds.jump.set_volume(0.8)
sounds.kill.set_volume(1)

button_play = Rect((WIDTH // 2 - 100, HEIGHT // 2 - 50), (200, 60))
button_sound = Rect((WIDTH // 2 - 100, HEIGHT // 2 + 20), (200, 60))
button_exit = Rect((WIDTH // 2 - 100, HEIGHT // 2 + 90), (200, 60))

buttons = [
    {"rect": button_play, "color": "blue", "text": "JOGAR"},
    {"rect": button_sound, "color": "orange", "text": "SOM"},
    {"rect": button_exit, "color": "red", "text": "SAIR"},
]

button_back = Rect((20, 20), (150, 50))

player = Actor("platformchar_idle", (100, 500))

vel_x = 0
vel_y = 0
speed = 4
jump_force = -12
gravity = 0.5
on_ground = False

hitbox_width = 45
hitbox_height = 68

state = "idle"
last_state = "idle"
last_direction = "right"
frame_index = 0
frame_timer = 0
animation_speed = 10

frames = {
    "idle": ["platformchar_idle", "platformchar_idle2"],
    "run_right": ["platformchar_walk1", "platformchar_walk2"],
    "run_left": ["platformchar_walk3", "platformchar_walk4"],
    "jump-right": ["platformchar_jump"],
    "jump-left": ["platformchar_jump_left"],
}

can_play_footstep = True
can_play_jump_sound = True
can_play_kill_sound = True

tilemap = [
    "....................................#####",
    "....................................#####",
    "....................................#####",
    "..............................G.....#####",
    ".............................G#.....#####",
    ".................G..........G##.....#####",
    "...............G.#.G.......G###.....#####",
    "..............G#G#G#.......####.....#####",
    "........GG....######.......####.....#####",
    "..............######.......####.....#####",
    "..............######.......####.....#####",
    "................##.........####.....#####",
    "GGGGGG..........##.........####......####",
    "................##.........####.........#",
    "................##.........####.........#",
    ".........GGGGGGG##.........####GGGG.....#",
    ".........#########.........########....D#",
    ".........#########.........####..##..GGG#",
    "GGGGGG...#########.........####..##..####",
    "######...#########.........####..##..####",
    "######...#########.........####..##..####",
    "######...#########.........####..##..####",
]

tile_sprites = {
    ".": "platformpack_tile003",
    "#": "platformpack_tile002",
    "G": "platformpack_tile001",
    "D": "platformpack_door",
}

platforms = []
door = None

for row_index, row in enumerate(tilemap):
    for col_index, tile in enumerate(row):
        if tile in ["#", "G"]:
            platforms.append(Rect((col_index * TILE, row_index * TILE), (TILE, TILE)))
        elif tile == "D":
            door = Rect((col_index * TILE - 32, row_index * TILE - 32),
                        (TILE * 2, TILE * 2))

snake_frames = {
    "walk_left": ["snake", "snake_walk"],
    "walk_right": ["snake_right", "snake_walk_right"],
    "dead": ["snake_dead"],
}

enemies = []
enemies_props = [
    {"pos": (10 * TILE, 15 * TILE - TILE / 4), "distance": 4, "speed": 1.5},
    {"pos": (12 * TILE, 15 * TILE - TILE / 4), "distance": 3, "speed": 0.5},
    {"pos": (32 * TILE, 15 * TILE - TILE / 4), "distance": 2, "speed": 0.5},
]

for props in enemies_props:
    enemy = {
        "actor": Actor("snake", props["pos"]),
        "vel_x": props["speed"],
        "state": "walk",
        "frame_index": 0,
        "frame_timer": 0,
        "start_x": props["pos"][0],
        "distance": props["distance"] * TILE,
    }
    enemies.append(enemy)

def allow_sound():
    global can_play_footstep, can_play_jump_sound, can_play_kill_sound
    can_play_footstep = True
    can_play_jump_sound = True
    can_play_kill_sound = True

def back_menu():
    global game_state, win
    game_state = "menu"
    win = False

def reset_game():
    global vel_x, vel_y, on_ground
    player.pos = (100, 500)
    vel_x = vel_y = 0
    on_ground = False
    for enemy, props in zip(enemies, enemies_props):
        enemy["state"] = "walk"
        enemy["vel_x"] = props["speed"]
        enemy["actor"].pos = props["pos"]
        enemy["frame_index"] = enemy["frame_timer"] = 0

def update():
    global vel_x, vel_y, on_ground, win, can_play_footstep, can_play_jump_sound, can_play_kill_sound

    if player.y > HEIGHT + 100:
        reset_game()

    vel_x = 0
    moving_left = keyboard.left
    moving_right = keyboard.right

    if moving_left:
        vel_x = -speed
        player.flip_x = True
    elif moving_right:
        vel_x = speed
        player.flip_x = False

    if (moving_left or moving_right) and on_ground and can_play_footstep:
        sounds.walk.play()
        can_play_footstep = False
        clock.schedule_unique(allow_sound, 0.25)

    hitbox = Rect(
        player.centerx - hitbox_width // 2,
        player.bottom - hitbox_height,
        hitbox_width,
        hitbox_height
    )

    hitbox.x += vel_x
    for platform in platforms:
        if hitbox.colliderect(platform):
            if vel_x > 0:
                hitbox.right = platform.left
            else:
                hitbox.left = platform.right

    player.centerx = hitbox.centerx

    vel_y += gravity
    hitbox.y += vel_y
    on_ground = False

    for platform in platforms:
        if hitbox.colliderect(platform):
            if vel_y > 0:
                hitbox.bottom = platform.top
                vel_y = 0
                on_ground = True
            elif vel_y < 0:
                hitbox.top = platform.bottom
                vel_y = 0

    if door and hitbox.colliderect(door):
        reset_game()
        win = True
        clock.schedule_unique(back_menu, 2)

    if keyboard.up and on_ground:
        vel_y = jump_force
        on_ground = False
        sounds.jump.play()
        can_play_jump_sound = False
        clock.schedule_unique(allow_sound, 0.25)

    player.bottom = hitbox.bottom

    update_player_animation()

    for enemy in enemies:
        actor = enemy["actor"]

        if enemy["state"] != "dead":
            actor.x += enemy["vel_x"]

        enemy_hitbox = Rect(
            actor.x - actor.width // 2,
            actor.y - actor.height // 2,
            actor.width,
            actor.height
        )

        if enemy["state"] != "dead" and hitbox.colliderect(enemy_hitbox):
            if vel_y > 0 and player.bottom - vel_y <= enemy_hitbox.top:
                enemy["state"] = "dead"
                enemy["vel_x"] = 0
                vel_y = jump_force / 2
                sounds.kill.play()
            else:
                reset_game()

        if enemy["state"] != "dead":
            if actor.x < enemy["start_x"] or actor.x > enemy["start_x"] + enemy["distance"]:
                enemy["vel_x"] *= -1

        update_enemy_animation(enemy)

def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "quit":
        exit()

def draw_menu():
    screen.clear()
    screen.fill((50, 50, 50))

    screen.draw.text("Meu Jogo",
        center=(WIDTH // 2, HEIGHT // 3),
        fontsize=80,
        color="white"
    )

    for button in buttons:
        screen.draw.filled_rect(button["rect"], button["color"])
        screen.draw.text(button["text"],
            center=button["rect"].center,
            fontsize=40,
            color="white"
        )

def draw_game():
    screen.clear()

    for row_index, row in enumerate(tilemap):
        for col_index, tile in enumerate(row):
            if tile == "D":
                screen.blit(tile_sprites["D"],
                            (col_index * TILE - 32, row_index * TILE - 32))
            else:
                screen.blit(tile_sprites[tile],
                            (col_index * TILE, row_index * TILE))

    player.draw()

    for enemy in enemies:
        enemy["actor"].draw()

    if win:
        screen.draw.text(
            "VOCE GANHOU!",
            center=(WIDTH // 2, HEIGHT // 2),
            fontsize=160,
            color="white"
        )

    screen.draw.filled_rect(button_back, "darkred")
    screen.draw.text("MENU",
        center=button_back.center,
        fontsize=35,
        color="white"
    )

def update_player_animation():
    global state, last_state, frame_index, frame_timer, animation_speed, last_direction

    if vel_x > 0:
        last_direction = "right"
    elif vel_x < 0:
        last_direction = "left"

    if not on_ground:
        if vel_x == 0:
            state = "jump-right"
        else:
            state = "jump-left" if vel_x < 0 else "jump-right"
    else:
        if vel_x == 0:
            state = "idle"
        else:
            state = "run_left" if vel_x < 0 else "run_right"

    animation_speed = 60 if state == "idle" else 10

    if state != last_state:
        frame_index = 0
        frame_timer = 0
        last_state = state

    frames_list = frames[state]

    if len(frames_list) == 1:
        player.image = frames_list[0]
        return

    frame_timer += 1
    if frame_timer >= animation_speed:
        frame_timer = 0
        frame_index = (frame_index + 1) % len(frames_list)

    player.image = frames_list[frame_index]

def update_enemy_animation(enemy):
    if enemy["state"] == "dead":
        enemy["actor"].image = snake_frames["dead"][0]
        return

    direction_frames = (
        snake_frames["walk_right"]
        if enemy["vel_x"] > 0 else
        snake_frames["walk_left"]
    )

    enemy["frame_timer"] += 1
    if enemy["frame_timer"] >= 12:
        enemy["frame_timer"] = 0
        enemy["frame_index"] = (enemy["frame_index"] + 1) % len(direction_frames)

    enemy["actor"].image = direction_frames[enemy["frame_index"]]

def on_mouse_down(pos):
    global game_state, sound_on

    if game_state == "playing" and button_back.collidepoint(pos):
        reset_game()
        game_state = "menu"
        return

    for button in buttons:
        if button["rect"].collidepoint(pos):

            if button["text"] == "JOGAR":
                game_state = "playing"

            elif button["text"] == "SOM":
                sound_on = not sound_on
                volume = 0.2 if sound_on else 0

                music.set_volume(volume)
                sounds.walk.set_volume(0.3 if sound_on else 0)
                sounds.jump.set_volume(0.8 if sound_on else 0)
                sounds.kill.set_volume(1 if sound_on else 0)

            elif button["text"] == "SAIR":
                exit()

go()
