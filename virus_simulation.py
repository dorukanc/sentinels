import random

class virus_simulation:
    def __init__(self, population_size, initial_infected, transmission_rate, mortality_rate, recovery_time):
        self.population_size = population_size
        self.transmission_rate = transmission_rate
        self.infected_count = initial_infected
        self.mortality_rate = mortality_rate
        self.recovery_time = recovery_time
        self.population_state = ['healthy'] * population_size

        # Randomly distribute initial infected to the population
        for i in random.sample(range(population_size), initial_infected):
            self.population_state[i] = 'infected'
        self.days_elapsed = 0

    def simulate_day(self):
        new_infections = 0
        new_deaths = 0

        for i in range(self.population_size):
            if self.population_state[i] == 'infected':
                if random.random() < self.mortality_rate:
                    self.population_state[i] = 'dead'
                    new_deaths += 1
                else:
                    if self.days_elapsed - self.recovery_time >= 0 and self.population_state[self.days_elapsed - self.recovery_time] == 'infected':
                        self.population_state[i] = 'healthy'
                        new_infections -= 1
            elif self.population_state[i] == 'healthy':
                # infecting nearby people
                for j in range(max(0, i-2), min(self.population_size, i+3)):
                    if self.population_state[j] == 'infected' and random.random() < self.transmission_rate:
                        self.population_state[j] = 'infected'
                        new_infections += 1
                        break

        # Update infected count after processing each individual
        self.infected_count += new_infections
        self.infected_count -= new_deaths

        self.days_elapsed +=1
        return new_infections, new_deaths
"""
    def apply_event(self, event_type):
        if event_type == 'lockdown':
            self.transmission_rate *= 0.7 # spread rate decreased by 30%
        elif event_type == 'vaccine':
            self.transmission_rate *= 0.5 # spread rate decreased by 50%
        elif event_type == 'mutation':
            self.transmission_rate *= 1.5 # spread rate increased by 50%
        elif event_type == 'mask':
            self.transmission_rate *= 0.82 # spread rate decreased by 18%
"""
def main():

    population_size = 1000000
    initial_infected = 10
    transmission_rate = 0.1 # Initial r value
    mortality_rate = 0.1
    recovery_time = 14 # Two weeks for recovery

    simulation = virus_simulation(population_size, initial_infected, transmission_rate, mortality_rate, recovery_time)

    while simulation.population_state.count('infected') > 0 and ('healthy' in simulation.population_state or 'infected' in simulation.population_state):
        new_infections, new_deaths = simulation.simulate_day()
        print(f"Day {simulation.days_elapsed}: {new_infections:.0f} new infections, {new_deaths:.0f} new deaths")
        infected_count = simulation.population_state.count('infected')
        print(f"Infected people: {infected_count:.0f}")

if __name__ == "__main__":
    main()