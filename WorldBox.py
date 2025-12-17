import pygame
import random
import math

WIDTH, HEIGHT = 1400, 850
CELL_SIZE = 10
FPS = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
SAND = (194, 178, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)
PURPLE = (128, 0, 128)


class GameSettings:
    def __init__(self):
        self.initial_energy = 100
        self.max_energy = 120
        self.energy_loss = 1.6
        self.energy_from_food = 35
        self.food_search_radius = 3
        self.reproduction_energy = 40
        self.reproduction_chance = 0.08
        self.reproduction_cost = 15
        self.min_reproduction_age = 20
        self.max_reproduction_age_ratio = 0.9
        self.max_nearby_agents = 15
        self.fight_chance = 0.3
        self.fight_death_chance = 0.3
        self.village_energy_cost = 30
        self.village_build_cost = 15
        self.village_build_chance = 0.005
        self.village_min_distance = 6
        self.initial_food = 400
        self.max_food = 500
        self.food_spawn_chance = 0.7
        self.disaster_chance = 0.0001
        self.meteor_radius = 3
        self.human_max_age = 500
        self.elf_max_age = 800
        self.dwarf_max_age = 700
        self.orc_max_age = 400
        self.human_strength = 5
        self.elf_strength = 4
        self.dwarf_strength = 6
        self.orc_strength = 7
        self.human_speed = 1.0
        self.elf_speed = 1.2
        self.dwarf_speed = 1.4
        self.orc_speed = 1.1


settings = GameSettings()


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label, step=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.step = step
        self.dragging = False
        self.handle_radius = 8

    def draw(self, screen, font):
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, BLUE, fill_rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        handle_x = self.rect.x + fill_width
        handle_y = self.rect.y + self.rect.height // 2
        pygame.draw.circle(screen, YELLOW, (handle_x, handle_y), self.handle_radius)
        pygame.draw.circle(screen, WHITE, (handle_x, handle_y), self.handle_radius, 2)
        label_text = font.render(f"{self.label}: {self.value:.2f}", True, WHITE)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            handle_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
            handle_y = self.rect.y + self.rect.height // 2
            if (abs(mouse_pos[0] - handle_x) < self.handle_radius and abs(
                    mouse_pos[1] - handle_y) < self.handle_radius) or self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.update_value(mouse_pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(self.rect.width, relative_x))
        ratio = relative_x / self.rect.width
        new_value = self.min_val + ratio * (self.max_val - self.min_val)
        self.value = round(new_value / self.step) * self.step
        self.value = max(self.min_val, min(self.max_val, self.value))


class Terrain:
    GRASS = 0
    WATER = 1
    SAND = 2
    MOUNTAIN = 3

    def __init__(self):
        self.grid = [[Terrain.GRASS for _ in range(WIDTH // CELL_SIZE)] for _ in range(HEIGHT // CELL_SIZE)]
        self.generate_terrain()

    def generate_terrain(self):
        for _ in range(9):
            x = random.randint(20, WIDTH // CELL_SIZE - 20)
            y = random.randint(15, HEIGHT // CELL_SIZE - 15)
            size = random.randint(2, 8)
            for dx in range(-size, size):
                for dy in range(-size, size):
                    if (dx * dx + dy * dy) < size * size:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < WIDTH // CELL_SIZE and 0 <= ny < HEIGHT // CELL_SIZE:
                            self.grid[ny][nx] = Terrain.WATER
        for _ in range(6):
            x = random.randint(25, WIDTH // CELL_SIZE - 25)
            y = random.randint(20, HEIGHT // CELL_SIZE - 20)
            size = random.randint(3, 10)
            for dx in range(-size, size):
                for dy in range(-size, size):
                    if random.random() > 0.5:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < WIDTH // CELL_SIZE and 0 <= ny < HEIGHT // CELL_SIZE:
                            if self.grid[ny][nx] != Terrain.WATER:
                                self.grid[ny][nx] = Terrain.SAND
        for _ in range(15):
            x = random.randint(15, WIDTH // CELL_SIZE - 15)
            y = random.randint(15, HEIGHT // CELL_SIZE - 15)
            if self.grid[y][x] != Terrain.WATER:
                self.grid[y][x] = Terrain.MOUNTAIN

    def get_color(self, terrain_type):
        colors = {Terrain.GRASS: DARK_GREEN, Terrain.WATER: BLUE, Terrain.SAND: SAND, Terrain.MOUNTAIN: GRAY}
        return colors.get(terrain_type, BLACK)

    def is_walkable(self, x, y):
        if 0 <= x < WIDTH // CELL_SIZE and 0 <= y < HEIGHT // CELL_SIZE:
            return self.grid[y][x] not in [Terrain.WATER, Terrain.MOUNTAIN]
        return False


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Village:
    def __init__(self, x, y, race):
        self.x = x
        self.y = y
        self.race = race
        self.population = 1
        self.level = 1

    def grow(self):
        if self.population > 5 and self.level < 2:
            self.level = 2
        elif self.population > 12 and self.level < 3:
            self.level = 3


class Agent:
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    ORC = "Orc"

    def __init__(self, x, y, race=None):
        self.x = x
        self.y = y
        self.race = race or random.choice([Agent.HUMAN, Agent.ELF, Agent.DWARF, Agent.ORC])
        self.energy = settings.initial_energy
        self.age = 0
        self.max_age = self.get_max_age()
        self.village = None
        self.color = self.get_race_color()
        self.strength = self.get_race_strength()
        self.speed = self.get_race_speed()

    def get_max_age(self):
        ages = {Agent.HUMAN: settings.human_max_age, Agent.ELF: settings.elf_max_age,
                Agent.DWARF: settings.dwarf_max_age, Agent.ORC: settings.orc_max_age}
        return ages.get(self.race, 500)

    def get_race_color(self):
        colors = {Agent.HUMAN: RED, Agent.ELF: GREEN, Agent.DWARF: BROWN, Agent.ORC: PURPLE}
        return colors.get(self.race, WHITE)

    def get_race_strength(self):
        strength = {Agent.HUMAN: settings.human_strength, Agent.ELF: settings.elf_strength,
                    Agent.DWARF: settings.dwarf_strength, Agent.ORC: settings.orc_strength}
        return strength.get(self.race, 5)

    def get_race_speed(self):
        speed = {Agent.HUMAN: settings.human_speed, Agent.ELF: settings.elf_speed, Agent.DWARF: settings.dwarf_speed,
                 Agent.ORC: settings.orc_speed}
        return speed.get(self.race, 1.0)

    def move(self, terrain):
        for _ in range(int(self.speed)):
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            new_x = (self.x + dx) % (WIDTH // CELL_SIZE)
            new_y = (self.y + dy) % (HEIGHT // CELL_SIZE)
            if terrain.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y
        self.energy -= settings.energy_loss
        self.age += 1

    def eat(self, food_list):
        for food in food_list[:]:
            if abs(self.x - food.x) <= settings.food_search_radius and abs(
                    self.y - food.y) <= settings.food_search_radius:
                self.energy = min(self.energy + settings.energy_from_food, settings.max_energy)
                food_list.remove(food)
                break

    def reproduce(self, agents_list, terrain):
        if (
                self.energy >= settings.reproduction_energy and self.age < self.max_age * settings.max_reproduction_age_ratio and self.age > settings.min_reproduction_age):
            nearby_agents = sum(
                1 for a in agents_list if abs(a.x - self.x) <= 5 and abs(a.y - self.y) <= 5 and a.race == self.race)
            if nearby_agents < settings.max_nearby_agents and random.random() < settings.reproduction_chance:
                self.energy -= settings.reproduction_cost
                child = Agent(self.x, self.y, self.race)
                child.village = self.village
                agents_list.append(child)

    def fight(self, other_agent):
        if self.race != other_agent.race:
            if random.random() < settings.fight_death_chance:
                my_power = self.strength + random.randint(0, 3)
                enemy_power = other_agent.strength + random.randint(0, 3)
                if my_power > enemy_power:
                    return other_agent
                elif enemy_power > my_power:
                    return self
        return None

    def build_village(self, villages, terrain):
        if self.energy >= settings.village_energy_cost and not self.village:
            if terrain.is_walkable(self.x, self.y):
                for v in villages:
                    dist = math.sqrt((self.x - v.x) ** 2 + (self.y - v.y) ** 2)
                    if dist < settings.village_min_distance:
                        return
                village = Village(self.x, self.y, self.race)
                villages.append(village)
                self.village = village
                self.energy -= settings.village_build_cost


class Disaster:
    @staticmethod
    def meteor_strike(x, y, agents, terrain):
        casualties = []
        radius = settings.meteor_radius
        for agent in agents[:]:
            dist = math.sqrt((agent.x - x) ** 2 + (agent.y - y) ** 2)
            if dist < radius:
                casualties.append(agent)
        for agent in casualties:
            agents.remove(agent)
        for dx in range(-radius, radius):
            for dy in range(-radius, radius):
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH // CELL_SIZE and 0 <= ny < HEIGHT // CELL_SIZE:
                    if (dx * dx + dy * dy) < radius * radius:
                        terrain.grid[ny][nx] = Terrain.SAND
        return len(casualties)

    @staticmethod
    def lightning_strike(x, y, agents):
        for agent in agents[:]:
            if agent.x == x and agent.y == y:
                agents.remove(agent)
                return True
        return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WorldBox Simulátor s Menu")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    terrain = Terrain()
    agents = []
    food = []
    villages = []

    races_positions = [(Agent.HUMAN, 5, 5), (Agent.ELF, WIDTH // CELL_SIZE - 6, 5),
                       (Agent.DWARF, 5, HEIGHT // CELL_SIZE - 6),
                       (Agent.ORC, WIDTH // CELL_SIZE - 6, HEIGHT // CELL_SIZE - 6)]

    for race, base_x, base_y in races_positions:
        for _ in range(12):
            x = base_x + random.randint(-3, 3)
            y = base_y + random.randint(-3, 3)
            x = max(0, min(WIDTH // CELL_SIZE - 1, x))
            y = max(0, min(HEIGHT // CELL_SIZE - 1, y))
            if terrain.is_walkable(x, y):
                agents.append(Agent(x, y, race))

    for _ in range(int(settings.initial_food)):
        x = random.randint(0, WIDTH // CELL_SIZE - 1)
        y = random.randint(0, HEIGHT // CELL_SIZE - 1)
        if terrain.is_walkable(x, y):
            food.append(Food(x, y))

    running = True
    paused = False
    selected_tool = None
    show_menu = False

    menu_x = 50
    menu_y = 100
    slider_width = 300
    slider_height = 20
    slider_spacing = 50

    sliders = [
        Slider(menu_x, menu_y, slider_width, slider_height, 20, 200, settings.initial_energy, "Počáteční energie", 5),
        Slider(menu_x, menu_y + slider_spacing, slider_width, slider_height, 10, 100, settings.energy_from_food,
               "Energie z jídla", 5),
        Slider(menu_x, menu_y + slider_spacing * 2, slider_width, slider_height, 0.5, 5.0, settings.energy_loss,
               "Úbytek energie", 0.1),
        Slider(menu_x, menu_y + slider_spacing * 3, slider_width, slider_height, 0.01, 0.3,
               settings.reproduction_chance, "Šance rozmnožení", 0.01),
        Slider(menu_x, menu_y + slider_spacing * 4, slider_width, slider_height, 0.0, 0.5, settings.fight_death_chance,
               "Smrtelnost bojů", 0.05),
        Slider(menu_x, menu_y + slider_spacing * 5, slider_width, slider_height, 0.1, 2.0, settings.food_spawn_chance,
               "Rychlost jídla", 0.1),
        Slider(menu_x + 400, menu_y, slider_width, slider_height, 200, 1000, settings.human_max_age, "Human věk", 50),
        Slider(menu_x + 400, menu_y + slider_spacing, slider_width, slider_height, 300, 1500, settings.elf_max_age,
               "Elf věk", 50),
        Slider(menu_x + 400, menu_y + slider_spacing * 2, slider_width, slider_height, 200, 1200,
               settings.dwarf_max_age, "Dwarf věk", 50),
        Slider(menu_x + 400, menu_y + slider_spacing * 3, slider_width, slider_height, 100, 800, settings.orc_max_age,
               "Orc věk", 50),
        Slider(menu_x + 400, menu_y + slider_spacing * 4, slider_width, slider_height, 1, 15, settings.human_strength,
               "Human síla", 1),
        Slider(menu_x + 400, menu_y + slider_spacing * 5, slider_width, slider_height, 1, 15, settings.elf_strength,
               "Elf síla", 1),
        Slider(menu_x + 800, menu_y, slider_width, slider_height, 1, 15, settings.dwarf_strength, "Dwarf síla", 1),
        Slider(menu_x + 800, menu_y + slider_spacing, slider_width, slider_height, 1, 15, settings.orc_strength,
               "Orc síla", 1),
        Slider(menu_x + 800, menu_y + slider_spacing * 2, slider_width, slider_height, 0.5, 3.0, settings.human_speed,
               "Human rychlost", 0.1),
        Slider(menu_x + 800, menu_y + slider_spacing * 3, slider_width, slider_height, 0.5, 3.0, settings.elf_speed,
               "Elf rychlost", 0.1),
        Slider(menu_x + 800, menu_y + slider_spacing * 4, slider_width, slider_height, 0.5, 3.0, settings.dwarf_speed,
               "Dwarf rychlost", 0.1),
        Slider(menu_x + 800, menu_y + slider_spacing * 5, slider_width, slider_height, 0.5, 3.0, settings.orc_speed,
               "Orc rychlost", 0.1),
    ]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if show_menu:
                for slider in sliders:
                    slider.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_TAB:
                    show_menu = not show_menu
                elif event.key == pygame.K_1:
                    selected_tool = "add_human"
                elif event.key == pygame.K_2:
                    selected_tool = "add_elf"
                elif event.key == pygame.K_3:
                    selected_tool = "add_dwarf"
                elif event.key == pygame.K_4:
                    selected_tool = "add_orc"
                elif event.key == pygame.K_m:
                    selected_tool = "meteor"
                elif event.key == pygame.K_l:
                    selected_tool = "lightning"
                elif event.key == pygame.K_f:
                    selected_tool = "food"
                elif event.key == pygame.K_ESCAPE:
                    selected_tool = None
            elif event.type == pygame.MOUSEBUTTONDOWN and not show_menu:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // CELL_SIZE
                grid_y = mouse_y // CELL_SIZE
                if selected_tool and terrain.is_walkable(grid_x, grid_y):
                    if selected_tool == "add_human":
                        agents.append(Agent(grid_x, grid_y, Agent.HUMAN))
                    elif selected_tool == "add_elf":
                        agents.append(Agent(grid_x, grid_y, Agent.ELF))
                    elif selected_tool == "add_dwarf":
                        agents.append(Agent(grid_x, grid_y, Agent.DWARF))
                    elif selected_tool == "add_orc":
                        agents.append(Agent(grid_x, grid_y, Agent.ORC))
                    elif selected_tool == "meteor":
                        Disaster.meteor_strike(grid_x, grid_y, agents, terrain)
                    elif selected_tool == "lightning":
                        Disaster.lightning_strike(grid_x, grid_y, agents)
                    elif selected_tool == "food":
                        food.append(Food(grid_x, grid_y))

        settings.initial_energy = sliders[0].value
        settings.energy_from_food = sliders[1].value
        settings.energy_loss = sliders[2].value
        settings.reproduction_chance = sliders[3].value
        settings.fight_death_chance = sliders[4].value
        settings.food_spawn_chance = sliders[5].value
        settings.human_max_age = sliders[6].value
        settings.elf_max_age = sliders[7].value
        settings.dwarf_max_age = sliders[8].value
        settings.orc_max_age = sliders[9].value
        settings.human_strength = sliders[10].value
        settings.elf_strength = sliders[11].value
        settings.dwarf_strength = sliders[12].value
        settings.orc_strength = sliders[13].value
        settings.human_speed = sliders[14].value
        settings.elf_speed = sliders[15].value
        settings.dwarf_speed = sliders[16].value
        settings.orc_speed = sliders[17].value

        if not paused and not show_menu:
            for agent in agents[:]:
                agent.move(terrain)
                agent.eat(food)
                agent.reproduce(agents, terrain)
                if random.random() < settings.village_build_chance:
                    agent.build_village(villages, terrain)
                if agent.energy <= 0 or agent.age >= agent.max_age:
                    agents.remove(agent)
                    if agent.village:
                        agent.village.population -= 1
            if random.random() < settings.fight_chance:
                for i, agent1 in enumerate(agents[:]):
                    for agent2 in agents[i + 1:]:
                        if agent1.x == agent2.x and agent1.y == agent2.y:
                            loser = agent1.fight(agent2)
                            if loser and loser in agents:
                                agents.remove(loser)
            if len(food) < settings.max_food and random.random() < settings.food_spawn_chance:
                x = random.randint(0, WIDTH // CELL_SIZE - 1)
                y = random.randint(0, HEIGHT // CELL_SIZE - 1)
                if terrain.is_walkable(x, y):
                    food.append(Food(x, y))
            for village in villages[:]:
                village.population = sum(1 for a in agents if a.village == village)
                if village.population == 0:
                    villages.remove(village)
                else:
                    village.grow()
            if random.random() < settings.disaster_chance:
                x = random.randint(0, WIDTH // CELL_SIZE - 1)
                y = random.randint(0, HEIGHT // CELL_SIZE - 1)
                if random.random() < 0.5:
                    Disaster.meteor_strike(x, y, agents, terrain)
                else:
                    Disaster.lightning_strike(x, y, agents)

        screen.fill(BLACK)

        if not show_menu:
            for y in range(len(terrain.grid)):
                for x in range(len(terrain.grid[0])):
                    color = terrain.get_color(terrain.grid[y][x])
                    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            for f in food:
                pygame.draw.rect(screen, YELLOW, (f.x * CELL_SIZE, f.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            for v in villages:
                size = v.level * 2
                village_color = ORANGE if v.race == Agent.HUMAN else (
                    GREEN if v.race == Agent.ELF else (BROWN if v.race == Agent.DWARF else PURPLE))
                pygame.draw.rect(screen, village_color,
                                 (v.x * CELL_SIZE - size, v.y * CELL_SIZE - size, CELL_SIZE + 2 * size,
                                  CELL_SIZE + 2 * size), 2)
            for a in agents:
                pygame.draw.rect(screen, a.color, (a.x * CELL_SIZE, a.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            y_offset = 10
            race_counts = {race: sum(1 for a in agents if a.race == race) for race in
                           [Agent.HUMAN, Agent.ELF, Agent.DWARF, Agent.ORC]}
            race_colors = {Agent.HUMAN: RED, Agent.ELF: GREEN, Agent.DWARF: BROWN, Agent.ORC: PURPLE}

            for race, count in race_counts.items():
                pygame.draw.rect(screen, race_colors[race], (10, y_offset + 3, 15, 15))
                text = font.render(f"{race}: {count}", True, WHITE)
                screen.blit(text, (30, y_offset))
                y_offset += 25

            text = font.render(f"Celkem: {len(agents)}", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 25
            text = font.render(f"Vesnice: {len(villages)}", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 25
            text = font.render(f"Jídlo: {len(food)}", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 30
            text = font.render("Nástroje: 1-Human 2-Elf 3-Dwarf 4-Orc", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 20
            text = font.render("M-Meteor L-Blesk F-Jídlo", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 20
            text = font.render("SPACE-Pauza TAB-Menu", True, YELLOW)
            screen.blit(text, (10, y_offset))

            if selected_tool:
                text = font.render(f"Vybrán: {selected_tool}", True, YELLOW)
                screen.blit(text, (WIDTH - 250, 10))
            if paused:
                text = font.render("PAUZA", True, RED)
                screen.blit(text, (WIDTH // 2 - 40, HEIGHT // 2))
        else:
            title = font.render("=== NASTAVENÍ PARAMETRŮ (TAB pro zavření) ===", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - 250, 30))
            for slider in sliders:
                slider.draw(screen, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
