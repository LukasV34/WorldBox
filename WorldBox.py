import pygame
import random
import math

# --- NASTAVENÍ ---
WIDTH, HEIGHT = 1500, 1000
CELL_SIZE = 10
FPS = 30

# --- BARVY ---
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


# --- TŘÍDY ---

class Terrain:
    # Třída pro různé typy terénu
    GRASS = 0
    WATER = 1
    SAND = 2
    MOUNTAIN = 3

    def __init__(self):
        # Konstruktor třídy - inicializuje terén
        self.grid = [[Terrain.GRASS for _ in range(WIDTH // CELL_SIZE)]
                     for _ in range(HEIGHT // CELL_SIZE)]
        self.generate_terrain()  # Generování terénu

    def generate_terrain(self):
        """Generuje náhodný terén s vodou, pískem a horami - méně překážek"""
        # Přidání vodních ploch
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

        # Přidání pouště
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

        # Přidání hor
        for _ in range(15):
            x = random.randint(15, WIDTH // CELL_SIZE - 15)
            y = random.randint(15, HEIGHT // CELL_SIZE - 15)
            if self.grid[y][x] != Terrain.WATER:
                self.grid[y][x] = Terrain.MOUNTAIN

    def get_color(self, terrain_type):
        """Vrací barvu podle typu terénu"""
        colors = {
            Terrain.GRASS: DARK_GREEN,
            Terrain.WATER: BLUE,
            Terrain.SAND: SAND,
            Terrain.MOUNTAIN: GRAY
        }
        return colors.get(terrain_type, BLACK)

    def is_walkable(self, x, y):
        """Kontroluje, zda je terén průchozí"""
        if 0 <= x < WIDTH // CELL_SIZE and 0 <= y < HEIGHT // CELL_SIZE:
            return self.grid[y][x] not in [Terrain.WATER, Terrain.MOUNTAIN]
        return False


class Food:
    """Třída pro potravu"""

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Village:
    """Třída pro vesnice - centrum civilizace"""

    def __init__(self, x, y, race):
        self.x = x
        self.y = y
        self.race = race  # rasa, která vesnici založila
        self.population = 1
        self.level = 1  # úroveň rozvoje (1-3)

    def grow(self):
        """Růst vesnice podle populace - lehčí růst"""
        if self.population > 5 and self.level < 2:
            self.level = 2
        elif self.population > 12 and self.level < 3:
            self.level = 3


class Agent:
    """Třída pro agenty - různé rasy s vlastnostmi"""
    # Různé rasy
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    ORC = "Orc"

    def __init__(self, x, y, race=None):
        self.x = x
        self.y = y
        self.race = race or random.choice([Agent.HUMAN, Agent.ELF, Agent.DWARF, Agent.ORC])
        self.energy = 100  # Zvýšená počáteční energie
        self.age = 0
        self.max_age = self.get_max_age()
        self.village = None  # příslušnost k vesnici
        self.color = self.get_race_color()
        self.strength = self.get_race_strength()
        self.speed = self.get_race_speed()

    def get_max_age(self):
        """Maximální věk podle rasy - delší životy"""
        ages = {
            Agent.HUMAN: 500,
            Agent.ELF: 800,
            Agent.DWARF: 600,
            Agent.ORC: 400
        }
        return ages.get(self.race, 500)

    def get_race_color(self):
        """Barva podle rasy"""
        colors = {
            Agent.HUMAN: RED,
            Agent.ELF: GREEN,
            Agent.DWARF: BROWN,
            Agent.ORC: GRAY
        }
        return colors.get(self.race, WHITE)

    def get_race_strength(self):
        """Síla podle rasy (pro boj)"""
        strength = {
            Agent.HUMAN: 5,
            Agent.ELF: 4,
            Agent.DWARF: 6,
            Agent.ORC: 7
        }
        return strength.get(self.race, 5)

    def get_race_speed(self):
        """Rychlost podle rasy"""
        speed = {
            Agent.HUMAN: 1.0,
            Agent.ELF: 1.2,
            Agent.DWARF: 0.8,
            Agent.ORC: 1.1
        }
        return speed.get(self.race, 1.0)

    def move(self, terrain):
        """Pohyb agenta s respektováním terénu"""
        for _ in range(int(self.speed)):
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            new_x = (self.x + dx) % (WIDTH // CELL_SIZE)
            new_y = (self.y + dy) % (HEIGHT // CELL_SIZE)

            # Pohyb pouze po průchozím terénu
            if terrain.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y

        self.energy -= 1.6  # úbytek energie
        self.age += 1

    def eat(self, food_list):
        """Konzumace potravy - větší dohled"""
        for food in food_list[:]:
            # Hledání jídla v okolí 3 políček
            if abs(self.x - food.x) <= 3 and abs(self.y - food.y) <= 3:
                self.energy = min(self.energy + 35, 120)  # Více energie z jídla, max 120
                food_list.remove(food)
                break

    def reproduce(self, agents_list, terrain):
        """Rozmnožování agentů - lehčí podmínky"""
        if self.energy >= 40 and self.age < self.max_age * 0.9 and self.age > 20:
            # Kontrola, aby nedošlo k přelidnění
            nearby_agents = sum(
                1 for a in agents_list if abs(a.x - self.x) <= 5 and abs(a.y - self.y) <= 5 and a.race == self.race)

            if nearby_agents < 15 and random.random() < 0.08:  # Omezení růstu populace
                self.energy -= 15  # Menší úbytek energie
                # Potomek stejné rasy
                child = Agent(self.x, self.y, self.race)
                child.village = self.village
                agents_list.append(child)

    def fight(self, other_agent):
        """Souboj mezi agenty různých ras - méně smrtelné"""
        if self.race != other_agent.race:
            # Nižší šance na smrt v boji
            if random.random() < 0.3:  # Pouze 30% šance na smrt
                my_power = self.strength + random.randint(0, 3)
                enemy_power = other_agent.strength + random.randint(0, 3)

                if my_power > enemy_power:
                    return other_agent
                elif enemy_power > my_power:
                    return self
        return None

    def build_village(self, villages, terrain):
        """Zakládání vesnice - lehčí podmínky"""
        if self.energy >= 30 and not self.village:  # Nižší požadavek na energii
            if terrain.is_walkable(self.x, self.y):
                # Kontrola, zda není poblíž jiná vesnice
                for v in villages:
                    dist = math.sqrt((self.x - v.x) ** 2 + (self.y - v.y) ** 2)
                    if dist < 6:  # Menší minimální vzdálenost
                        return

                # Založení nové vesnice
                village = Village(self.x, self.y, self.race)
                villages.append(village)
                self.village = village
                self.energy -= 15  # Menší úbytek energie


class Disaster:
    """Třída pro přírodní katastrofy"""
    METEOR = "Meteor"
    LIGHTNING = "Lightning"

    @staticmethod
    def meteor_strike(x, y, agents, terrain):
        """Dopad meteoru - ničí agenty v oblasti"""
        casualties = []
        radius = 3
        for agent in agents[:]:
            dist = math.sqrt((agent.x - x) ** 2 + (agent.y - y) ** 2)
            if dist < radius:
                casualties.append(agent)

        for agent in casualties:
            agents.remove(agent)

        # Poškození terénu
        for dx in range(-radius, radius):
            for dy in range(-radius, radius):
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH // CELL_SIZE and 0 <= ny < HEIGHT // CELL_SIZE:
                    if (dx * dx + dy * dy) < radius * radius:
                        terrain.grid[ny][nx] = Terrain.SAND

        return len(casualties)

    @staticmethod
    def lightning_strike(x, y, agents):
        """Blesk - zabíjí agenta na pozici"""
        for agent in agents[:]:
            if agent.x == x and agent.y == y:
                agents.remove(agent)
                return True
        return False


# --- HLAVNÍ HRA ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WorldBox Simulátor")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Inicializace světa
    terrain = Terrain()
    agents = []
    food = []
    villages = []

    # Počáteční populace - každá rasa v jednom rohu
    races_positions = [
        (Agent.HUMAN, 5, 5),  # Levý horní roh
        (Agent.ELF, WIDTH // CELL_SIZE - 6, 5),  # Pravý horní roh
        (Agent.DWARF, 5, HEIGHT // CELL_SIZE - 6),  # Levý dolní roh
        (Agent.ORC, WIDTH // CELL_SIZE - 6, HEIGHT // CELL_SIZE - 6)  # Pravý dolní roh
    ]

    for race, base_x, base_y in races_positions:
        # Vytvoření 12 agentů každé rasy v jejich rohu
        for _ in range(12):
            x = base_x + random.randint(-3, 3)
            y = base_y + random.randint(-3, 3)
            x = max(0, min(WIDTH // CELL_SIZE - 1, x))
            y = max(0, min(HEIGHT // CELL_SIZE - 1, y))
            if terrain.is_walkable(x, y):
                agents.append(Agent(x, y, race))

    # Počáteční potrava - mnohem více
    for _ in range(400):
        x = random.randint(0, WIDTH // CELL_SIZE - 1)
        y = random.randint(0, HEIGHT // CELL_SIZE - 1)
        if terrain.is_walkable(x, y):
            food.append(Food(x, y))

    # Herní proměnné
    running = True
    paused = False
    selected_tool = None
    frame_count = 0

    # Nástroje pro interakci
    TOOLS = {
        "add_human": "1",
        "add_elf": "2",
        "add_dwarf": "3",
        "add_orc": "4",
        "meteor": "M",
        "lightning": "L",
        "food": "F"
    }

    while running:
        # --- UDÁLOSTI ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Pauza
                if event.key == pygame.K_SPACE:
                    paused = not paused

                # Výběr nástrojů
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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Použití nástroje
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

        # --- LOGIKA (pokud není pauza) ---
        if not paused:
            frame_count += 1

            # Akce agentů
            for agent in agents[:]:
                agent.move(terrain)
                agent.eat(food)
                agent.reproduce(agents, terrain)

                # Zakládání vesnic (častěji)
                if random.random() < 0.005:  # 5x vyšší šance
                    agent.build_village(villages, terrain)

                # Smrt stářím nebo hladem
                if agent.energy <= 0 or agent.age >= agent.max_age:
                    agents.remove(agent)
                    if agent.village:
                        agent.village.population -= 1

            # Boje mezi agenty různých ras - méně časté a méně smrtelné
            if random.random() < 0.3:  # Pouze 30% času probíhají boje
                for i, agent1 in enumerate(agents[:]):
                    for agent2 in agents[i + 1:]:
                        if agent1.x == agent2.x and agent1.y == agent2.y:
                            loser = agent1.fight(agent2)
                            if loser and loser in agents:
                                agents.remove(loser)

            # Regenerace potravy - rychlejší a více
            if len(food) < 500 and random.random() < 0.7:  # Vyšší limit a šance
                x = random.randint(0, WIDTH // CELL_SIZE - 1)
                y = random.randint(0, HEIGHT // CELL_SIZE - 1)
                if terrain.is_walkable(x, y):
                    food.append(Food(x, y))

            # Růst vesnic
            for village in villages[:]:
                village.population = sum(1 for a in agents if a.village == village)
                if village.population == 0:
                    villages.remove(village)
                else:
                    village.grow()

            # Náhodné katastrofy (mnohem vzácnější)
            if random.random() < 0.0001:  # 10x méně časté
                x = random.randint(0, WIDTH // CELL_SIZE - 1)
                y = random.randint(0, HEIGHT // CELL_SIZE - 1)
                if random.random() < 0.5:
                    Disaster.meteor_strike(x, y, agents, terrain)
                else:
                    Disaster.lightning_strike(x, y, agents)

        # --- VYKRESLENÍ ---
        screen.fill(BLACK)

        # Vykreslení terénu
        for y in range(len(terrain.grid)):
            for x in range(len(terrain.grid[0])):
                color = terrain.get_color(terrain.grid[y][x])
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Vykreslení potravy
        for f in food:
            pygame.draw.rect(screen, YELLOW, (f.x * CELL_SIZE, f.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Vykreslení vesnic
        for v in villages:
            size = v.level * 2
            village_color = ORANGE if v.race == Agent.HUMAN else (
                GREEN if v.race == Agent.ELF else (BROWN if v.race == Agent.DWARF else PURPLE))
            pygame.draw.rect(screen, village_color,
                             (v.x * CELL_SIZE - size, v.y * CELL_SIZE - size, CELL_SIZE + 2 * size,
                              CELL_SIZE + 2 * size), 2)

        # Vykreslení agentů
        for a in agents:
            pygame.draw.rect(screen, a.color, (a.x * CELL_SIZE, a.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # --- UI ---
        y_offset = 10

        # Statistiky podle ras
        race_counts = {race: sum(1 for a in agents if a.race == race)
                       for race in [Agent.HUMAN, Agent.ELF, Agent.DWARF, Agent.ORC]}

        for race, count in race_counts.items():
            text = font.render(f"{race}: {count}", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 25

        # Celkový počet
        text = font.render(f"Celkem: {len(agents)}", True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 25

        text = font.render(f"Vesnice: {len(villages)}", True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 25

        text = font.render(f"Jídlo: {len(food)}", True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 30

        # Nástroje
        text = font.render("Nástroje: 1-Human 2-Elf 3-Dwarf 4-Orc", True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 20

        text = font.render("M-Meteor L-Blesk F-Jídlo SPACE-Pauza", True, WHITE)
        screen.blit(text, (10, y_offset))

        # Vybraný nástroj
        if selected_tool:
            text = font.render(f"Vybrán: {selected_tool}", True, YELLOW)
            screen.blit(text, (WIDTH - 200, 10))

        # Pauza
        if paused:
            text = font.render("PAUZA", True, RED)
            screen.blit(text, (WIDTH // 2 - 40, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()