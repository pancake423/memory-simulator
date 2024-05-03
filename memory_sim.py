from memory import Memory
from scheduler import Scheduler

# get memory capacity, process text file, and algorithm from user
# no input validation, please be nice
mem_cap = int(input("How much memory should the system have?\n>>> "))
alg = int(input("Which algorithm should the system use to allocate memory?\n\t0. First Fit\n\t1. Next Fit\n\t2. Best "
                "Fit\n\t3. Worst Fit\n>>> "))
process_file = input("What file should the system read processes from?\n>>> ")

# create memory and scheduler
memory = Memory(mem_cap, alg)  # first fit
sys = Scheduler(process_file)

# display the initial state of the system
sys.display(memory)

# loop until all processes are complete
while sys.has_processes():
    # get number of steps to simulate for this iteration
    user_choice = input("Press enter to simulate 1 step, or enter a number of steps:\n>>> ")
    n = 1 if user_choice == '' else int(user_choice)

    # run simulation
    sys.step(memory, n)
print("Done!")
print(f"Final system time: {sys.sys_time}")
print(f"Number of coalesce operations performed: {memory.n_coalesce}")
print(f"Number of compact operations performed: {memory.n_compact}")



