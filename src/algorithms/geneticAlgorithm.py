import random
import time
from core import (Problem, State, Objective, random_state, random_neighbor, make_result)

class GeneticAlgorithm():
    def __init__(self, problem: Problem, population: int, iteration: int, seed: int, prob_mutation: float = 0.1):
        self.problem = problem
        self.population = population        #jumlah individu di setiap generasi
        self.iteration = iteration          #jumlah iterasi yang dijalankan
        self.seed = seed                    #nilai acak agar hasil bisa diulang
        self.prob_mutation = prob_mutation  #peluang mutasi anak
        self.rng = random.Random(seed)
        self.objective = Objective(problem)

    #Fitness function
    def fitness_function(self, state):
            """Menghitung nilai fitness untuk mengevaluasi kualitas solusi"""
            return self.objective.value(state)

    #Initial population
    def create_initial_population(self):
        """Membuat state acak sebagai populasi awal"""
        population = []
        for _ in range(self.population):
            population.append(random_state(self.problem, self.rng))
        return population

    #Selection function
    def selection(self, population, fitness):
        """Memilih individu sebagai parent menggunakan Tournament Selection(mengambil 3 individu acak dan memilih individu dengan nilai fitness tertinggi)"""
        selected = []
        tournament_size = min(3, len(population))
        for _ in range (self.population):
            idx = self.rng.sample(range(len(population)), tournament_size)
            winner = max(idx, key=lambda i: fitness[i])
            selected.append(population[winner])
        return selected

    #Crossover function
    def crossover(self, parent1, parent2):
        """Melakukan uniform crossover: memilih induk secara acak"""
        ship = self.problem.ship
        children = []
        for p1, p2 in ((parent1, parent2), (parent2, parent1)):
            child = {vehicle_id: None for vehicle_id in self.problem.ids}
            occupied = set()
            weight = 0
            order = list(self.problem.ids)
            self.rng.shuffle(order)
            for vehicle_id in order:
                parents = [p1,p2]
                if self.rng.random() < 0.5:
                    parents.reverse()
                vehicle = self.problem.by[vehicle_id]
                for parent in parents:
                    if parent.p[vehicle_id] is None:
                        continue
                    cells = parent.cells(vehicle_id)
                    if (all(0 <= x < ship.cols and 0 <= y < ship.rows for x, y in cells)
                        and weight + vehicle.weight <= ship.cap
                        and occupied.isdisjoint(cells)):
                        child[vehicle_id] = parent.p[vehicle_id]
                        occupied.update(cells)
                        weight += vehicle.weight
                        break
            children.append(State(self.problem, child))
        return children[0], children[1]

    #Mutation function
    def mutation(self, state: State):
        """Melakukan mutasi dengan swap kendaraan secara random"""
        if self.rng.random() < self.prob_mutation:
            return random_neighbor(state, self.rng)
        return state

    def get_best(self, population, fitness):
        """Individu terbaik dari populasi"""
        best = max(range(len(population)), key=lambda i: fitness[i])
        return population[best], fitness[best]
    
    #Main loop
    def run(self):
        self.rng = random.Random(self.seed)
        start = time.time()

        #Buat populasi
        population = self.create_initial_population()
        fitness = [self.fitness_function(state) for state in population]

        #State awal
        initial_idx = max(range(self.population), key=lambda i: fitness[i])
        initial_state, initial_fitness = self.get_best(population, fitness)
        initial_state = initial_state.copy()
        global_best_state = initial_state.copy()
        global_best_fitness = initial_fitness

        max_history = [global_best_fitness]
        average_history = [sum(fitness)/len(fitness)]

        #Generation Loop
        for _ in range (self.iteration):
            selected = self.selection(population, fitness)
            next_population = []
            for i in range (0, self.population, 2):
                parent1 = selected[i]
                parent2 = selected[(i + 1) % self.population]
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutation(child1)
                child2 = self.mutation(child2)
                next_population.append(child1)
                next_population.append(child2)
            next_population = next_population[:self.population]

            next_population[0] = global_best_state.copy()
            population = next_population
            fitness = [self.fitness_function(state) for state in population]

            generation_best_state, generation_best_fitness = self.get_best(population, fitness)
            if generation_best_fitness > global_best_fitness:
                global_best_state = generation_best_state.copy()
                global_best_fitness = generation_best_fitness

            max_history.append(global_best_fitness)
            average_history.append(sum(fitness)/len(fitness))

        #State akhir
        final_state = global_best_state
        duration = time.time() - start

        return make_result("Genetic Algorithm", self.objective, initial_state, final_state, history=max_history, iterations=self.iteration, duration=duration, 
                           extra={"population": self.population, "seed": self.seed,
                                  "max_history": max_history, "average_history": average_history})