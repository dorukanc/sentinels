from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__, template_folder='templates')

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulation():
    # Retrieve parameters from the UI form
    population_size = int(request.form['population_size'])
    initial_infected = int(request.form['initial_infected'])
    transmission_rate = float(request.form['transmission_rate'])
    mortality_rate = float(request.form['mortality_rate'])
    recovery_time = int(request.form['recovery_time'])

    simulation = virus_simulation(population_size, initial_infected, transmission_rate, mortality_rate, recovery_time)

    simulation_data_list = []

    while simulation.population_state.count('infected') > 0 and ('healthy' in simulation.population_state or 'infected' in simulation.population_state):
        new_infections, new_deaths = simulation.simulate_day()
        print(f"Day {simulation.days_elapsed}: {new_infections:.0f} new infections, {new_deaths:.0f} new deaths")
        infected_count = simulation.population_state.count('infected')
        print(f"Infected people: {infected_count:.0f}")

        # Simulation data to send the user interface
        simulation_data = {
        'days_elapsed' : simulation.days_elapsed,
        'new_infections' : new_infections,
        'new deaths' : new_deaths,
        'total_infected' : infected_count
        }

        simulation_data_list.append(simulation_data)

    return jsonify(simulation_data_list)

if __name__ == "__main__":
    app.run(debug=True)