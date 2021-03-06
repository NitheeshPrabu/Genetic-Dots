# PyGame handles the on-screen graphics
import pygame
# Numpy handles the array manipulation
import numpy as np
# Gauss used to generate random vectors and uniform used to select parents
from random import gauss, seed, uniform
# Sleep used to set the frame rate and time used to do timing analysis for debugging
from time import sleep, time


# Configurables
swarm_size = 50         # Number of dots in the swarm - as this increases, time taken to start new iteration increases
mutation_rate = 0.01    # Sets the likelihood of a gene/vector getting randomly mutated when generating offspring
dot_max_velocity = 15   # Velocity limit for each dot - if too high it can overshoot the goal or get embedded in barrier
frame_rate = 100        # Frequency of screen redraw - also increases algorithm call rate (dots appear to move faster)

# Initialise screen
screen = 0

# Define screen resolution
height = 800
width = 1600

# Define rectangle sizes
rect_1 = (0, 200, width/2.5, 50)
rect_2 = (width/2, 500, width, 50)

# Define goal
goal = np.array([20, width/2], dtype=np.int64)

# Define some colours
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
darkBlue = (0, 0, 128)
grey = (192, 192, 192)
yellow = (255, 255, 0)

# Stat Trackers
dead_count = 0
goal_count = 0


class Brain:

    def __init__(self, size):
        # This function runs when class gets initialised

        # Series of vectors which get the dot to the goal
        self.directions = np.zeros((size, 2))

        # Record of how many steps have been taken so far
        self.step = 0

        # Randomize the initialised array with random vectors
        self.randomize()

    def randomize(self):
        # Generate a random unit vector for each vector in directions
        for i in range(self.directions.__len__()):
            # Generate a random vector
            seed(time())
            vec = np.array([gauss(0, 1), gauss(0, 1)])

            # Get magnitude of vector using pythagoras
            mag = (vec**2).sum()**0.5

            # Divide vector by magnitude to get unit vector
            self.directions[i] = vec/mag

    def clone(self):
        # Return a copy of the current brain object with identical direction vectors
        # The direction vectors are analogous to genes

        # Create an instance of this class
        clone_brain = Brain(self.directions.__len__())

        # Copy over the direction vectors to the cloned brain
        np.copyto(clone_brain.directions, self.directions)

        return clone_brain

    def mutate(self):
        # Mutates the brain by randomizing some of the vectors

        for i in range(self.directions.__len__()):
            # Iterate through all the vectors in directions

            # Generate a random number between 0 and 1 (all numbers equally likely)
            rand = uniform(0, 1)

            # If the number generated is lower than mutation rate, then the vector should be mutated
            if rand < mutation_rate:
                # Set this direction to be a random direction

                # Generate a random vector
                seed(time())
                vec = np.array([gauss(0, 1), gauss(0, 1)])

                # Get magnitude of vector using pythagoras
                mag = (vec ** 2).sum() ** 0.5

                # Divide vector by magnitude to get unit vector
                self.directions[i] = vec / mag


class Dot:

    def __init__(self):
        # Will hold all the directions (analogous to genes) for this dot
        self.brain = Brain(400)

        # A vector holding the current position, initialised to where all dots should start from
        self.pos = np.array([height - 125, width * 0.95])

        # A vector to hold the velocity of the dot
        self.vel = np.array([0, 0], dtype=np.float64)

        # A vector to hold the acceleration of the dot
        self.acc = np.array([0, 0], dtype=np.float64)

        # Is the dot still active, or dead?
        self.dead = 0

        # Fitness measures how well the dot performed (closer to the target or fewer steps yield higher fitness)
        self.fitness = 0

        # Has the dot reach the goal?
        self.reached_goal = 0

        # Set to 1 if this dot is the best dot in the swarm
        self.is_best = 0

    def show(self, display_screen):
        # Draw this dot on the screen

        if self.is_best:
            # If this dot is the best, draw it in green
            pygame.draw.circle(display_screen, green, (self.pos.astype(int)[1], self.pos.astype(int)[0]), 10, 0)

        else:
            # If this is not the best, then draw it in red
            pygame.draw.circle(display_screen, red, (self.pos.astype(int)[1], self.pos.astype(int)[0]), 10, 0)

    def move(self):
        global dead_count

        if self.brain.directions.__len__() > self.brain.step:
            # If there are directions left set the acceleration as the next vector in the directions array
            self.acc = self.brain.directions[self.brain.step]
            # Increment the step counter to retrieve the next direction vector in the next iteration
            self.brain.step += 1
        else:
            # If the end of directions array has been reached, the dot is dead
            self.dead = 1
            dead_count += 1
            print("Out of moves")

        # Update velocity
        self.vel += self.acc

        # Limit the magnitude of velocity to 15 (tweakable - too high and dot can be embedded in barrier and not edge)
        velocity_mag = (self.vel**2).sum()**0.5
        if velocity_mag > dot_max_velocity:
            self.vel = dot_max_velocity * self.vel / velocity_mag

        # Update position
        self.pos += self.vel

    def update(self):
        global dead_count
        global goal_count
        # Call the move function and check for collisions

        if (not self.dead) and (not self.reached_goal):
            # Move if the dot is still within the window and hasn't reached the goal
            self.move()

            if self.pos[0] < 2 or self.pos[1] < 2 or self.pos[0] > (height - 2) or self.pos[1] > (width - 2):
                # Dot is dead if it reached within 2 pixels of the edge of the window
                self.dead = 1
                dead_count += 1
                # print("Out of bounds")

            elif np.linalg.norm(goal - self.pos) < 20:
                # If the dot reached the goal
                self.reached_goal = 1
                goal_count += 1

            elif rect_1[1] < self.pos[0] < (rect_1[1] + rect_1[3]) and rect_1[0] < self.pos[1] < (
                        rect_1[0] + rect_1[2]):

                # If the dot hits the first rectangle
                self.dead = 1
                dead_count += 1

            elif rect_2[1] < self.pos[0] < (rect_2[1] + rect_2[3]) and rect_2[0] < self.pos[1] < (
                        rect_2[0] + rect_2[2]):

                # If the dot hits the second rectangle
                self.dead = 1
                dead_count += 1

    def calculate_fitness(self):
        # Calculate fitness, with a higher value being assigned for better performing dots
        # Preference given to dots that reached goal, over dots that came close but died
        if self.reached_goal:
            # If the dot reached the goal then the fitness is based on the amount of steps it took to get there
            self.fitness = 1.0/16.0 + 1000.0/(self.brain.step**2)
        else:
            # If the dot didn't reach the goal then the fitness is based on how close it is to the goal
            distance_to_goal = np.linalg.norm(goal - self.pos)
            self.fitness = 1/(distance_to_goal ** 2)

    def get_baby(self):
        # Clone the parent
        baby = Dot()
        # Babies have the same brain as their parent
        baby.brain = self.brain.clone()
        return baby


class Population:

    def __init__(self, size):
        # Sum of all population fitnesses combined
        self.fitness_sum = 0

        # Keep track of population generation
        self.gen = 1

        # Index of the best performing dot
        self.best_dot = 0

        # Min number of steps taken by a dot to reach the goal
        self.min_step = 400

        # Array to hold all the dots in the population
        self.dots = np.zeros(size, dtype=object)

        # Assign the dot object to each element
        for i in range(size):
            self.dots[i] = Dot()

    def show(self, display_screen):
        # Show all the dots on the screen
        for i in range(1, self.dots.__len__()):
            self.dots[i].show(display_screen)

        # To Check: Why is the best dot shown separately
        self.dots[0].show(display_screen)

    def update(self):
        global dead_count
        # Update all dots with their new positions

        for i in range(self.dots.__len__()):
            if self.dots[i].brain.step > self.min_step:
                # If the dots have exceeded the minimum number of steps, then they should be killed
                self.dots[i].dead = 1
                dead_count += 1
            else:
                # Update the dots with their new positions
                self.dots[i].update()

    def calculate_fitness(self):
        # Calculate the fitness values for each of the dots
        for i in range(self.dots.__len__()):
            self.dots[i].calculate_fitness()

    def all_dots_dead(self):
        # Check if all the dots are dead or have reached the goal already (i.e. no dots active)
        for i in range(self.dots.__len__()):
            if (not self.dots[i].dead) and (not self.dots[i].reached_goal):
                return 0

        return 1

    def natural_selection(self):
        # Gets the next generation of dots

        # New array of dots for babies
        new_dots = np.zeros(self.dots.__len__(), dtype=object)

        # Find and set the best dot in current population
        self.set_best_dot()

        # Let the best dot live without getting mutated
        new_dots[0] = self.dots[self.best_dot].get_baby()
        new_dots[0].is_best = 1

        # Calculate the sum of all the fitness values
        self.calculate_fitness_sum()

        baby_time = 0   # temp variable to measure processing times
        for i in range(1, new_dots.__len__()):
            # Set each element in the array to a Dot() object
            new_dots[i] = Dot()

            # Select parent based on fitness
            parent = self.select_parent()

            # Get baby from them
            wait_time = time()  # temp variable to measure processing times
            new_dots[i] = parent.get_baby()
            baby_time += time() - wait_time  # temp variable to measure processing times

        print("Baby: ", baby_time)  # temp: print processing time to get babies

        # Set the current dots to be the new baby dots
        self.dots = new_dots

        # Increment generation counter
        self.gen += 1

    def calculate_fitness_sum(self):
        self.fitness_sum = 0
        for i in range(self.dots.__len__()):
            self.fitness_sum += self.dots[i].fitness

    def select_parent(self):
        # Chooses dot from the population to return randomly(considering fitness)

        # this function works by randomly choosing a value between 0 and the sum of all the fitnesses then go
        # through all the dots and add their fitness to a running sum and if that sum is greater than the random
        # value generated that dot is chosen since dots with a higher fitness function add more to the running
        # sum then they have a higher chance of being chosen

        # Get a random number that is within the range of fitness_sum
        rand = uniform(0, self.fitness_sum)

        running_sum = 0

        # Go through the fitnesses, and when the running sum exceeds rand, return the dot at which this occurred
        for i in range(self.dots.__len__()):
            running_sum += self.dots[i].fitness
            if running_sum > rand:
                return self.dots[i]

        # Should never get to this point
        return 0

    def mutate_babies(self):
        # Mutates the brains of all the babies
        for i in range(1, self.dots.__len__()):
            self.dots[i].brain.mutate()

    def set_best_dot(self):
        # Finds the dot with the highest fitness, and sets it as the best dot

        max_fitness = 0
        max_index = 0
        for i in range(self.dots.__len__()):
            if self.dots[i].fitness > max_fitness:
                max_fitness = self.dots[i].fitness
                max_index = i

        self.best_dot = max_index

        # If the best dot reached the goal, then reset min number of steps needed to reach goal
        if self.dots[self.best_dot].reached_goal:
            self.min_step = self.dots[self.best_dot].brain.step


def draw_static_objects():
    # Draw 2 rectangle
    pygame.draw.rect(screen, white, rect_1, 0)
    pygame.draw.rect(screen, white, rect_2, 0)

    # Draw goal dot in blue
    pygame.draw.circle(screen, blue, (goal[1], goal[0]), 10, 0)


def main():
    # This function controls the whole script. First, it initialises PyGame and the swarm of dots
    # It has a loop which redraws the screen on each iteration and calls the necessary functions to update the
    # positions of dots and perform the natural selection and breeding when generating the next generation

    global screen
    global dead_count
    global goal_count

    # initialize the PyGame module
    pygame.init()

    pygame.display.set_caption("Genetic Dots")

    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((width, height))

    # Initialise fonts
    pygame.font.init()
    gen_font = pygame.font.SysFont('Droid Sans Mono', 20, True)
    stats_font = pygame.font.SysFont('Droid Sans Mono', 20, True)
    # Set screen colour
    screen.fill(black)

    # Draw rectangles
    draw_static_objects()

    # Create the swarm of dots
    swarm = Population(swarm_size)

    # define a variable to control the main loop
    running = True

    # Track the number of moves
    moves = 0

    # main loop
    while running:
        # Increment number of iterations of this loop
        moves += 1

        # Reset window with a black colour
        screen.fill(black)

        # Draw the rectangles and goal
        draw_static_objects()

        # Draw label to show current generation
        gen_label = gen_font.render("GEN: " + str(swarm.gen), False, yellow)
        screen.blit(gen_label, (width/2 - 60, height - 20))

        # Draw label to show credits
        stats_label = stats_font.render("Reached Goal: " + str(goal_count) + ", Dead: " + str(dead_count), False, white)
        screen.blit(stats_label, (width/2, height - 20))

        if swarm.all_dots_dead():
            # If all the dots are dead perform genetic algorithm

            # Update the screen to show the last position of dots
            pygame.display.update()

            # Print stats on dots that reached the goal or got killed
            print("Reached Goal: ", goal_count, "   Dead: ", dead_count)

            # Print the number of moves taken by this generation
            print("Moves: ", moves)

            # Reset trackers
            moves = 0
            dead_count = 0
            goal_count = 0

            # Perform genetic algorithms
            swarm.calculate_fitness()
            swarm.natural_selection()
            swarm.mutate_babies()

        else:
            # Update the dots' positions and status
            swarm.update()

            # Draw the dots on the screen
            swarm.show(screen)

        # Redraw the screen
        pygame.display.update()

        # Sleep for 10 ms (yielding ~ 100 FPS)
        sleep(1/frame_rate)

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()