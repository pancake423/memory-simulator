class MemoryBlock:
    def __init__(self, size, status=-1):
        self.size = size
        self.status = status
        self.offset = 0

    def free(self):
        self.status = -1

    def get_location(self):
        return [self.offset, self.offset+self.size-1]

    def is_free(self):
        return self.status == -1

    def allocate(self, size, pid):
        if size > self.size:
            raise ValueError(f"Cannot allocate {size} units of memory from block of size {self.size}.")
        if self.status != -1:
            raise ValueError(f"Block is already allocated (PID = {self.status})")

        if size != self.size:
            return [MemoryBlock(size, pid), MemoryBlock(self.size - size)]
        if size == self.size:
            return [MemoryBlock(size, pid)]

    def __str__(self, scale=10):
        if self.size < scale*2:
            return "|"
        n = (self.size - scale*2) // scale
        return f"[{(' ' if self.is_free() else 'x')*n}]"


class Memory:
    def __init__(self, capacity, algorithm):
        self.mem_capacity = capacity
        self.next_fit_pointer = 0
        self.alg = algorithm
        self.n_compact = 0
        self.n_coalesce = 0

        self.memory = [MemoryBlock(capacity)]

    def first_fit(self, amt):
        for i, block in enumerate(self.memory):
            if amt <= block.size and block.is_free():
                return i
        return -1

    def next_fit(self, amt):
        i = 0
        while i < len(self.memory):
            self.next_fit_pointer += 1
            if self.next_fit_pointer >= len(self.memory):
                self.next_fit_pointer = 0
            block = self.memory[self.next_fit_pointer]
            if amt <= block.size and block.is_free():
                return self.next_fit_pointer
            i += 1
        return -1

    def best_fit(self, amt):
        best_idx = -1
        best_size = self.mem_capacity

        for i, block in enumerate(self.memory):
            if block.is_free() and amt <= block.size <= best_size:
                best_idx = i
                best_size = block.size

        return best_idx

    def worst_fit(self, amt):
        largest_idx = -1
        largest_size = 0
        for i, block in enumerate(self.memory):
            if block.is_free() and block.size > largest_size:
                largest_idx = i
                largest_size = block.size

        if largest_size >= amt:
            return largest_idx
        return -1

    def allocate(self, amt, pid):
        algs = [
            lambda n: self.first_fit(n),
            lambda n: self.next_fit(n),
            lambda n: self.best_fit(n),
            lambda n: self.worst_fit(n),
        ]
        block_id = algs[self.alg](amt)

        if block_id == -1:
            return MemoryBlock(0), -1

        new_blocks = self.memory[block_id].allocate(amt, pid)
        self.memory = self.memory[:block_id] + new_blocks + self.memory[block_id+1:]
        self.calc_offset()
        return new_blocks[0], 0

    def coalesce(self):
        self.n_coalesce += 1
        print("Before:")
        print(self.display_block())
        new_mem = []
        i = 0
        while i < len(self.memory):
            if self.memory[i].is_free():
                j = i
                while j < len(self.memory) and self.memory[j].is_free():
                    j += 1
                # memory blocks [i, j) are free
                cap = 0
                for bid in range(i, j):
                    cap += self.memory[bid].size
                new_mem.append(MemoryBlock(cap))
                i = j-1

            else:
                new_mem.append(self.memory[i])
            i += 1
        self.memory = new_mem
        self.calc_offset()
        print("After:")
        print(self.display_block())

    def compact(self):
        self.n_compact += 1
        print("Before:")
        print(self.display_block())
        new_mem = []
        free_size = self.mem_capacity
        for block in self.memory:
            if not block.is_free():
                free_size -= block.size
                new_mem.append(block)
        new_mem.append(MemoryBlock(free_size))
        self.memory = new_mem
        print("After:")
        print(self.display_block())

    def calc_offset(self):
        offset = 0
        for block in self.memory:
            block.offset = offset
            offset += block.size

    def get_free(self):
        free = 0
        for block in self.memory:
            if block.is_free():
                free += block.size
        return free

    def get_allocated(self):
        return self.mem_capacity - self.get_free()

    def display_block(self):
        out = vis = ""
        for block in self.memory:
            vis += str(block)

        out += "-" * len(vis) + "\n"
        out += vis + "\n"
        out += "-" * len(vis)
        return out

    def __str__(self):
        out = "=====Memory=====\n"
        out += f"Memory Free: {self.get_free()}\n"
        out += f"Memory Allocated: {self.get_allocated()}\n\n"
        out += self.display_block() + "\n"

        return out
