import pygame
import matplotlib
import mesa
import random
import pandas as pd
import enum
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector


class HealthStatus:
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    VACCINATED = 3


# Init the agents
class CovidAgent(Agent):
    def __init__(self, unique_id, model, xInit, yInit, destinations=[]):
        super().__init__(unique_id, model)
        self.initial_position = (xInit, yInit)
        self.health_status = HealthStatus.SUSCEPTIBLE
        self.target_position = None
        self.destinations = destinations
        self.infection_time = 0
        self.infected_at = 0
        self.stay_at_home = None

    def step(self):
        self.check()
        self.interact()
        self.move()

    def check(self):
        np.random.seed = self.random.seed
        # random recover time
        rand_treatment = random.randint(self.model.incubation_period, self.model.treatment_period)
        if self.health_status == HealthStatus.INFECTED:
            mortality_rate = self.model.mortality_rate
            if np.random.choice([0, 1], p=[mortality_rate, 1 - mortality_rate]) == 0:
                self.model.schedule.remove(self)
            elif self.model.schedule.time - self.infected_at >= rand_treatment:
                self.health_status = HealthStatus.RECOVERED

    def move(self):
        self.set_target_position()
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.move_position(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def interact(self):
        neighbors = self.model.grid.get_cell_list_contents([self.pos])
        for n in neighbors:
            if self.health_status == HealthStatus.INFECTED and n.health_status != HealthStatus.INFECTED:
                if n.health_status == HealthStatus.VACCINATED:
                    infect = random.random() <= self.model.infection_prob * 0.05
                else:
                    infect = random.random() <= self.model.infection_prob
                if infect:
                    n.health_status = HealthStatus.INFECTED
                    n.infected_at = self.model.schedule.time

    def set_target_position(self):
        if self.pos == self.initial_position:
            self.target_position = self.random.choice(self.destinations)
        elif self.pos == self.target_position:
            self.target_position = self.initial_position

    def move_position(self, possible_steps):
        if self.health_status == HealthStatus.INFECTED:
            symptoms = self.model.schedule.time - self.infection_time >= self.model.incubation_period
            if self.pos == self.initial_position and symptoms and self.stay_at_home:
                return self.initial_position
            elif self.pos != self.initial_position and symptoms and self.stay_at_home:
                self.target_position = self.initial_position
        return random.choice(possible_steps)


class CovidModel(Model):
    def __init__(self, P, width, height, infection_prob, mortality_rate, incubation_period, treatment_period,
                 stay_at_home, destination_size, vaccination_interval, vaccination_batch_size, vaccination_start,
                 seed=None):
        self.population_size = P
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.infection_prob = infection_prob
        self.mortality_rate = mortality_rate
        self.incubation_period = incubation_period
        self.treatment_period = treatment_period
        self.stay_at_home = stay_at_home
        self.vaccination_interval = vaccination_interval
        self.vaccination_batch_size = vaccination_batch_size
        self.vaccination_start = vaccination_start
        self.deaths = 0
        self.running = True

        self.destinations = []
        for _ in range(destination_size):
            self.destinations.append((self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))

        first_infected_index = random.randint(0, self.population_size - 1)
        for i in range(self.population_size):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            agent_gen = CovidAgent(i, self, x, y, self.destinations)
            if i == first_infected_index:
                agent_gen.health_status = HealthStatus.INFECTED
            self.schedule.add(agent_gen)
            self.grid.place_agent(agent_gen, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"S": compute_S, "I": compute_I, "R": compute_R, "V": compute_V, "D": compute_D},
            agent_reporters={"Status": "health_status", "Position": "pos"}
        )

    def step(self):
        if self.schedule.time >= self.vaccination_start and self.schedule.time % self.vaccination_interval == 0:
            self.perform_vaccination_drive()

        self.datacollector.collect(self)
        self.schedule.step()

    def perform_vaccination_drive(self):
        susceptible_agents = [agent for agent in self.schedule.agents if
                              agent.health_status == HealthStatus.SUSCEPTIBLE]
        if len(susceptible_agents) > 0:
            batch_size = min(self.vaccination_batch_size, len(susceptible_agents))
            vaccinated_agents = self.random.sample(susceptible_agents, batch_size)
            for agent in vaccinated_agents:
                agent.health_status = HealthStatus.VACCINATED

    def draw_star(self, screen, x, y, size, color):
        points = [
            (x, y - size),
            (x + size * 0.2, y - size * 0.2),
            (x + size, y - size * 0.2),
            (x + size * 0.4, y + size * 0.2),
            (x + size * 0.6, y + size),
            (x, y + size * 0.4),
            (x - size * 0.6, y + size),
            (x - size * 0.4, y + size * 0.2),
            (x - size, y - size * 0.2),
            (x - size * 0.2, y - size * 0.2)
        ]
        pygame.draw.polygon(screen, color, points)
    def draw(self, screen, cell_size):
        for destination in self.destinations:
            x, y = destination
            self.draw_star(screen, x * cell_size + cell_size // 2, y * cell_size + cell_size // 2, cell_size // 2, (255, 215, 0))  # Gold star

        for agent in self.schedule.agents:
            x, y = agent.pos
            if agent.health_status == HealthStatus.SUSCEPTIBLE:
                color = (0, 0, 255)  # Blue
            elif agent.health_status == HealthStatus.INFECTED:
                color = (255, 0, 0)  # Red
            elif agent.health_status == HealthStatus.RECOVERED:
                color = (0, 255, 0)  # Green
            elif agent.health_status == HealthStatus.VACCINATED:
                color = (255, 255, 0)  # Yellow
            pygame.draw.circle(screen, color, (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2),
                               cell_size // 2)


def compute_S(model):
    return len(
        [agent.health_status for agent in model.schedule.agents if agent.health_status == HealthStatus.SUSCEPTIBLE])


def compute_I(model):
    return len([agent.health_status for agent in model.schedule.agents if agent.health_status == HealthStatus.INFECTED])


def compute_R(model):
    return len(
        [agent.health_status for agent in model.schedule.agents if agent.health_status == HealthStatus.RECOVERED])


def compute_V(model):
    return len(
        [agent.health_status for agent in model.schedule.agents if agent.health_status == HealthStatus.VACCINATED])


def compute_D(model):
    return model.population_size - len(model.schedule.agents)


def run_simulation(batch, steps, pop_size, width, height, inf_prob, mort_rate, inc_period, treat_period, stay_home,
                   dest_size, vacc_interval, vacc_batch_size, vacc_start):
    model = CovidModel(pop_size, width, height, inf_prob, mort_rate, inc_period, treat_period, stay_home, dest_size,
                       vacc_interval, vacc_batch_size, vacc_start, seed=batch)
    for _ in range(steps):
        model.step()
    return model.datacollector.get_model_vars_dataframe()


# Parameters
simulation_steps = 100
simulation_population_size = 175
maximum_X = 20
maximum_Y = 20
simulation_infection_prob = 0.7
simulation_mortality_rate = 0.005
simulation_incubation_period = 8
simulation_treatment_period = 14
simulation_stay_at_home = False
simulation_destination_size = 10
vaccination_interval = 10
vaccination_batch_size = 10
vaccination_start = 50
num_batches = 50

# Pygame setup
pygame.init()
cell_size = 20
width, height = maximum_X * cell_size, maximum_Y * cell_size
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Run the simulation with visualization
model = CovidModel(simulation_population_size, maximum_X, maximum_Y, simulation_infection_prob,
                   simulation_mortality_rate, simulation_incubation_period, simulation_treatment_period,
                   simulation_stay_at_home, simulation_destination_size, vaccination_interval,
                   vaccination_batch_size, vaccination_start)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    model.step()
    screen.fill((255, 255, 255))
    model.draw(screen, cell_size)
    pygame.display.flip()
    clock.tick(10)  # Adjust the speed as needed

pygame.quit()