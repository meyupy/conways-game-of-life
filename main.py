import pygame

pygame.init()

S_WIDTH = 960
BG_COLOR, BG_PANEL_COLOR = (191, 191, 191), (159, 159, 159)
SQ_COLOR_1, SQ_COLOR_2 = (175, 175, 175), (127, 127, 127)
BUTTON_COLOR_1, BUTTON_COLOR_2 = (143, 143, 143), (127, 127, 127)
TEXT_COLOR_1, TEXT_COLOR_2 = (191, 191, 191), (95, 95, 95)

gui_font = pygame.font.Font(None, S_WIDTH//48)
gui_font_large = pygame.font.Font(None, S_WIDTH//24)

screen = pygame.display.set_mode((S_WIDTH, 3*S_WIDTH//4))
pygame.display.set_caption("Conway's Game of Life")

clock = pygame.time.Clock()

panel_rect = pygame.rect.Rect((3 * S_WIDTH // 4, 0), (S_WIDTH // 4, 3 * S_WIDTH // 4))

game_name_1_surf = gui_font_large.render("Conway's", True, TEXT_COLOR_1)
game_name_1_rect = game_name_1_surf.get_rect(center=(7*S_WIDTH//8, 5*S_WIDTH//48))
game_name_2_surf = gui_font_large.render("Game of Life", True, TEXT_COLOR_1)
game_name_2_rect = game_name_2_surf.get_rect(center=(7*S_WIDTH//8, 7*S_WIDTH//48))

GEN_NO_RECT_CENTER_POS = (7*S_WIDTH//8, 5*S_WIDTH//16)


class Button:

    def __init__(self, surface, text, font, x, y, width, height,
                 button_color_1, button_color_2, text_color):
        self.surface = surface
        self.button_color_1 = button_color_1
        self.button_color_2 = button_color_2
        self.color = button_color_1
        self.border_radius = width // 10
        self.body_rect = pygame.rect.Rect(x, y, width, height)
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)
        self.press_allowed = True
        self.pressed = False

    def is_clicked(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            if mouse_pressed:
                self.pressed = True
            elif self.pressed and self.press_allowed:
                self.pressed = False
                return True
        else:
            self.pressed = False
            if mouse_pressed:
                self.press_allowed = False
            else:
                self.press_allowed = True
        return False

    def draw(self):
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.button_color_2
        else:
            self.color = self.button_color_1
        pygame.draw.rect(self.surface, self.color, self.body_rect, border_radius=self.border_radius)
        self.surface.blit(self.text_surf, self.text_rect)


button_beginning = Button(screen, "<<", gui_font, 25 * S_WIDTH // 32, 29 * S_WIDTH // 96,
                          S_WIDTH // 48, S_WIDTH // 48, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)
button_end = Button(screen, ">>", gui_font, 91 * S_WIDTH // 96, 29 * S_WIDTH // 96,
                    S_WIDTH // 48, S_WIDTH // 48, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)
button_previous = Button(screen, "<", gui_font, 13 * S_WIDTH // 16, 29 * S_WIDTH // 96,
                         S_WIDTH // 48, S_WIDTH // 48, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)
button_next = Button(screen, ">", gui_font, 11 * S_WIDTH // 12, 29 * S_WIDTH // 96,
                     S_WIDTH // 48, S_WIDTH // 48, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)
button_ready = Button(screen, "Ready", gui_font, 5 * S_WIDTH // 6, 17 * S_WIDTH // 48,
                      S_WIDTH // 12, S_WIDTH // 24, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)
button_play = Button(screen, "Play", gui_font, 5 * S_WIDTH // 6, 5 * S_WIDTH // 12,
                     S_WIDTH // 12, S_WIDTH // 24, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)
button_stop = Button(screen, "Stop", gui_font, 5 * S_WIDTH // 6, 5 * S_WIDTH // 12,
                     S_WIDTH // 12, S_WIDTH // 24, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)
button_start_new = Button(screen, "Start New", gui_font, 5 * S_WIDTH // 6, S_WIDTH // 2,
                          S_WIDTH // 12, S_WIDTH // 24, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_1)


class Square:

    def __init__(self, surface, pos, width, index, color_death, color_alive):
        self.surface = surface
        self.index = index
        self.color_death = color_death
        self.color_alive = color_alive
        self.color = self.color_death
        self.is_alive = False
        self.body_rect = pygame.rect.Rect(pos, (width, width))

    def draw(self):
        if self.is_alive:
            self.color = self.color_alive
        else:
            self.color = self.color_death
        pygame.draw.rect(self.surface, self.color, self.body_rect)

    def check_if_pressed(self):
        if pygame.mouse.get_pressed()[0] and self.body_rect.collidepoint(pygame.mouse.get_pos()):
            return True


squares = []

y_index = 0
for y_pos in range(S_WIDTH//24, 17*S_WIDTH//24, S_WIDTH//48):
    y_pos += S_WIDTH//960
    new_row = []
    x_index = 0
    for x_pos in range(S_WIDTH//24, 17*S_WIDTH//24, S_WIDTH//48):
        x_pos += S_WIDTH//960
        new_square = Square(screen, (x_pos, y_pos), 3*S_WIDTH//160,
                            (y_index, x_index), SQ_COLOR_1, SQ_COLOR_2)
        x_index += 1
        new_row.append(new_square)
    y_index += 1
    squares.append(new_row)

DEFAULT_PERMUTATION = [[0 for _ in line] for line in squares]
ROW_NUM = len(DEFAULT_PERMUTATION)
COLUMN_NUM = len(DEFAULT_PERMUTATION[0])
NEIGHBOUR_SEARCH_ADD_AMOUNTS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def produce_next_generation(current_perm):

    new_perm = [[0 for _ in i] for i in DEFAULT_PERMUTATION]

    for the_row in range(ROW_NUM):
        for the_column in range(COLUMN_NUM):
            alive_neighbor_num = 0
            for r_add, c_add in NEIGHBOUR_SEARCH_ADD_AMOUNTS:
                new_r, new_c = the_row + r_add, the_column + c_add
                if 0 <= new_r < ROW_NUM and 0 <= new_c < COLUMN_NUM and current_perm[new_r][new_c] == 1:
                    alive_neighbor_num += 1
            if alive_neighbor_num in [2, 3]:
                if current_perm[the_row][the_column] == 1:
                    new_perm[the_row][the_column] = 1
                elif alive_neighbor_num == 3:
                    new_perm[the_row][the_column] = 1

    return new_perm


starting_permutation = [[0 for _ in line] for line in DEFAULT_PERMUTATION]
current_permutation = [[0 for _ in line] for line in DEFAULT_PERMUTATION]
generations = []
mode = "draw"   # "draw" or "game"

current_index = 0
max_seen_index = 0
infinite_loop_found = False
animation_continues = False

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, BG_PANEL_COLOR, panel_rect)
    screen.blit(game_name_1_surf, game_name_1_rect)
    screen.blit(game_name_2_surf, game_name_2_rect)

    # # # # # # #

    if mode == "draw":

        for sq_row in squares:
            for square in sq_row:
                if square.check_if_pressed():
                    r, c = square.index
                    starting_permutation[r][c] = 1
                    square.is_alive = True

        if button_ready.is_clicked():
            current_permutation = [[n for n in line] for line in starting_permutation]
            current_index = 0
            max_seen_index = 0
            infinite_loop_found = False
            generations = [starting_permutation]
            mode = "game"

        button_ready.draw()

    # # # # # # #

    elif mode == "game":

        while not infinite_loop_found and current_index > len(generations)-11:
            new_generation = produce_next_generation(generations[-1])
            if new_generation not in generations:
                generations.append(new_generation)
            else:
                infinite_loop_found = True

        if animation_continues:
            if current_index < len(generations)-1:
                current_index += 1
            else:
                animation_continues = False
        else:
            if button_beginning.is_clicked():
                current_index = 0
            if button_end.is_clicked():
                current_index = max_seen_index
            if button_previous.is_clicked() and current_index > 0:
                current_index -= 1
            if button_next.is_clicked() and current_index < len(generations)-1:
                current_index += 1

        if current_index > max_seen_index:
            max_seen_index = current_index

        current_permutation = generations[current_index]

        for r in range(ROW_NUM):
            for c in range(COLUMN_NUM):
                square = squares[r][c]
                if current_permutation[r][c] == 1:
                    square.is_alive = True
                else:
                    square.is_alive = False

        if not animation_continues and button_play.is_clicked():
            animation_continues = True
        elif animation_continues and button_stop.is_clicked():
            animation_continues = False

        if button_start_new.is_clicked():
            for sq_row in squares:
                for square in sq_row:
                    square.is_alive = False
            starting_permutation = [[0 for _ in line] for line in DEFAULT_PERMUTATION]
            current_permutation = [[0 for _ in line] for line in DEFAULT_PERMUTATION]
            animation_continues = False
            mode = "draw"

        gen_number_surf = gui_font_large.render(f"{current_index+1}", True, TEXT_COLOR_2)
        gen_number_rect = gen_number_surf.get_rect(center=GEN_NO_RECT_CENTER_POS)

        screen.blit(gen_number_surf, gen_number_rect)
        button_beginning.draw()
        button_end.draw()
        button_previous.draw()
        button_next.draw()
        if animation_continues:
            button_stop.draw()
        else:
            button_play.draw()
        button_start_new.draw()

    # # # # # # #

    for sq_row in squares:
        for square in sq_row:
            square.draw()

    clock.tick(60)
    pygame.display.update()
