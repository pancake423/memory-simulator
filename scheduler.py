class Process:
    def __init__(self, pid, memory, start_time, run_time):
        self.pid = pid
        self.memory_amt = memory
        self.start_time = start_time
        self.time_remaining = run_time
        self.memory_block = None
        self.active = False

    def start(self, mem):
        self.memory_block = mem
        self.active = True

    def step(self, t):
        if not self.active:
            return
        self.time_remaining -= t
        if self.time_remaining <= 0:
            self.active = False
            self.memory_block.free()

    def __str__(self):
        return (f"{str(self.pid):<5}|{str(self.memory_block.get_location()):<15}|{str(self.time_remaining):<15}\n"
                + '-' * 37 + "\n")


class Scheduler:
    def __init__(self, filename):
        self.sys_time = 0
        self.increment = 10
        self.process_queue = []
        self.active_processes = []
        self.active_id = 0

        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                args = [int(arg) for arg in line.split(",")]
                self.process_queue.append(Process(*args))

        self.total_time = 0

    def step_internal(self, memory, print_output=True):
        # check if there are any processes in the queue that are ready to start
        for i in range(len(self.process_queue)):
            if i >= len(self.process_queue):
                break
            if self.process_queue[i].start_time <= self.sys_time:
                i -= self.try_start(memory, i)  # decrement index if process starts successfully

        # run the active process (round-robin scheduler)
        if len(self.active_processes) > 0:
            self.active_id += 1
            self.active_id %= len(self.active_processes)
            self.active_processes[self.active_id].step(self.increment)
            if not self.active_processes[self.active_id].active:
                self.active_processes.pop(self.active_id)
        self.sys_time += self.increment
        self.display(memory) if print_output else None

    def try_start(self, memory, idx):
        process = self.process_queue[idx]

        # if there isn't enough memory in the system, toss out this process
        if process.memory_amt > memory.mem_capacity:
            print("There isn't enough memory in the system to run this process.")
            self.process_queue.pop(idx)
            return 1

        # if there isn't enough memory available right now, try again later
        if process.memory_amt > memory.get_free():
            return 0
        print(f"Starting process {process.pid}")
        mem_block, status_code = memory.allocate(process.memory_amt, process.pid)

        # if allocation failed, coalesce and try again.
        if status_code == -1:
            print(f"No block available with size {process.memory_amt}. Coalescing memory...")
            memory.coalesce()
            mem_block, status_code = memory.allocate(process.memory_amt, process.pid)

            # if allocation still fails, compact memory and try again.
            if status_code == -1:
                print(f"No block available with size {process.memory_amt}. Compacting memory...")
                memory.compact()
                mem_block, status_code = memory.allocate(process.memory_amt, process.pid)
                # should be unreachable, since we already filter for processes where there isn't enough memory available
                if status_code == -1:
                    raise ValueError("How did you get here?")

        process.start(mem_block)
        self.active_processes.append(self.process_queue.pop(idx))
        return 1

    def step(self, memory, n=1):
        for i in range(n):
            if not self.has_processes():
                self.display(memory)
                return
            self.step_internal(memory, print_output=(i+1 == n))

    def has_processes(self):
        return len(self.active_processes) > 0 or len(self.process_queue) > 0

    def display(self, memory):
        print(self)
        print(memory)

    def __str__(self):
        out = "\n=====System=====\n"
        out += f'System Time: {self.sys_time}\n'
        out += 'Active Processes:\n'
        out += f"{'PID':<5}|{'Memory Location':<15}|{'Time Remaining':<15}\n"
        out += '-'*37 + "\n"
        for p in self.active_processes:
            out += str(p)
        return out
