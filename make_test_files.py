from random import randint

n_files = 10
range_processes = (10, 20)
range_memory = (10, 500)
range_start = (0, 1000)
range_duration = (10, 200)


def rand(range_vals, round_to=1):
    return (randint(*range_vals)//round_to)*round_to


for i in range(n_files):
    filename = f'demo_{i}.txt'
    with open(filename, "w") as f:
        lines = []
        for i in range(randint(*range_processes)):
            lines.append(f"{i},{rand(range_memory, 10)},{rand(range_start, 10)},{rand(range_duration, 10)}\n")
        f.writelines(lines)
