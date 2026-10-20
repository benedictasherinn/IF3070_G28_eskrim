import random
import time
from src.core import (Problem, State, Objective, random_state, random_neighbor, make_result)
import matplotlib.pyplot as plt

class GeneticAlgorithm():
    def __init__(self, problem: Problem, population: int, iteration: int, seed: int):
        self.problem = problem
        self.population = population
        self.iteration = iteration
        self.seed = seed
        self.rng = random.Random(seed)
        self.objective = Objective(problem)

    #Fitness function
    def fitness_function(self, state):
            return self.objective.value(state)

    #Initial population
    def create_initial_population(self):
        population = []
        for _ in range(self.population):
            population.append(random_state(self.problem, self.rng))
        return population

    #Selection function
    def selection(self, population, fitness):
        selected = []
        for _ in range (len(population)):
            idx = self.rng.sample(range(len(population)), 3)
            winner = max(idx, key=lambda i: fitness[i])
            selected.append(population[winner])
        return selected

    #Crossover function
    def crossover(self, parent1, parent2):
        child1 = {}
        child2 = {}
        for vehicle_id in self.problem.ids:
            if self.rng.random() < 0.5:
                child1[vehicle_id] = parent1.p[vehicle_id]
                child2[vehicle_id] = parent2.p[vehicle_id]
            else:
                child1[vehicle_id] = parent2.p[vehicle_id]
                child2[vehicle_id] = parent1.p[vehicle_id]
        return State(self.problem, child1), State(self.problem, child2)
        
    #Mutation function
    def mutation(self, state):
        return random_neighbor(state, self.rng)
    
    #Main loop
    def run(self):
        self.rng = random.Random(self.seed)
        start = time.time()

        #Buat populasi
        population = self.create_initial_population()
        fitness = [self.fitness_function(s) for s in population]

        #State awal
        initial_idx = max(range(self.population), key=lambda i: fitness[i])
        initial_state = population[initial_idx] 
        initial_fitness = fitness[initial_idx]
        initial_average = sum(fitness) / self.population

        max_history = [max(fitness)]
        average_history = [initial_average]

        #Generation Loop
        for _ in range (self.iteration):
            best_idx = max(range(self.population), key=lambda i: fitness[i])
            best_individual = population[best_idx]

            selected = self.selection(population, fitness)
            next_population = []
            for i in range (0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[(i + 1) % len(selected)]
                child1, child2 = self.crossover(parent1, parent2)
                next_population.append(self.mutation(child1))
                next_population.append(self.mutation(child2))
            next_population = next_population[:self.population]

            next_population[0] = best_individual.copy()
            population = next_population
            fitness = [self.fitness_function(s) for s in population]
            max_history.append(max(fitness))
            average_history.append(sum(fitness)/self.population)

        #State akhir
        final_idx = max(range(self.population), key=lambda i: fitness[i])
        final_state = population[final_idx]
        duration = time.time() - start

        return make_result("Genetic Algorithm", self.objective, initial_state, final_state, history=max_history, iterations=self.iteration, duration=duration, 
                           extra={"population": self.population, "seed": self.seed,
                                  "max_history": max_history, "average_history": average_history})


def plot_history(result, path=None):
    extra = result["extra"]
    generations = range(len(extra["max_history"]))

    fig = plt.figure()
    plt.plot(generations, extra["max_history"], label="Maximum")
    plt.plot(generations, extra["average_history"], label="Average")

    plt.xlabel("Generation")
    plt.ylabel("Objective Value")
    plt.title(
        f"Genetic Algorithm: Population={extra['population']}, "
        f"Iterations={result['iterations']}"
    )
    plt.legend()

    if path:
        plt.savefig(path, dpi=120)
        plt.close()

    return fig
