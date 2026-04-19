import random

class VanEmdeBoas:
    def __init__(self, u):
        if u < 2 or (u & (u - 1)) != 0:
            raise ValueError("u must be a power of 2 >= 2")

        self.u = u
        self.min = None
        self.max = None

        if u == 2:
            self.summary = None
            self.cluster = None
        else:
            k = u.bit_length() - 1
            lower_bits = k // 2
            upper_bits = k - lower_bits

            self.lower = 2 ** lower_bits
            self.upper = 2 ** upper_bits

            self.summary = VanEmdeBoas(self.upper)
            self.cluster = [None] * self.upper

    def high(self, x):
        return x // self.lower

    def low(self, x):
        return x % self.lower

    def index(self, h, l):
        return h * self.lower + l

    def find(self, x):
        if self.min is None:
            return False

        if x == self.min or x == self.max:
            return True

        if self.u == 2:
            return False

        h = self.high(x)

        if self.cluster[h] is None:
            return False

        return self.cluster[h].find(self.low(x))

    def insert(self, x):
        if self.min is None:
            self.min = self.max = x
            return

        if x < self.min:
            x, self.min = self.min, x

        if self.u > 2:
            h = self.high(x)
            l = self.low(x)

            if self.cluster[h] is None:
                self.cluster[h] = VanEmdeBoas(self.lower)

            if self.cluster[h].min is None:
                self.summary.insert(h)
                self.cluster[h].min = self.cluster[h].max = l
            else:
                self.cluster[h].insert(l)

        if x > self.max:
            self.max = x

    def successor(self, x):
        if self.min is None:
            return None

        if self.u == 2:
            if x == 0 and self.max == 1:
                return 1
            return None

        if x < self.min:
            return self.min

        h = self.high(x)
        l = self.low(x)
        cluster = self.cluster[h]

        if cluster is not None and l < cluster.max:
            offset = cluster.successor(l)
            return self.index(h, offset)

        succ_cluster = self.summary.successor(h)

        if succ_cluster is None:
            return None

        offset = self.cluster[succ_cluster].min
        return self.index(succ_cluster, offset)

    def delete(self, x): # assume the element is in the structure
        if self.min == self.max:
            self.min = self.max = None
            return

        if self.u == 2:
            self.min = 1 - x
            self.max = self.min
            return

        if x == self.min:
            first_cluster = self.summary.min
            x = self.index(first_cluster, self.cluster[first_cluster].min)
            self.min = x

        h = self.high(x)
        l = self.low(x)
        cluster = self.cluster[h]

        cluster.delete(l)

        if cluster.min is None:
            self.summary.delete(h)
            self.cluster[h] = None

            if x == self.max:
                summary_max = self.summary.max

                if summary_max is None:
                    self.max = self.min
                else:
                    self.max = self.index(
                        summary_max,
                        self.cluster[summary_max].max
                    )

        elif x == self.max:
            self.max = self.index(h, cluster.max)


def randomized_test():
    U = 64
    v = VanEmdeBoas(U)
    s = set()

    for _ in range(2000):
        op = random.choice(["insert", "delete", "find", "succ"])
        x = random.randrange(U)

        if op == "insert":
            if x not in s:
                v.insert(x)
                s.add(x)

        elif op == "delete":
            if x in s:
                v.delete(x)
                s.remove(x)

        elif op == "find":
            if v.find(x) != (x in s):
                print("Mismatch in find:", x)
                print("Set:", sorted(s))
                return

        elif op == "succ":
            sorted_s = sorted(s)
            expected = None

            for val in sorted_s:
                if val > x:
                    expected = val
                    break

            got = v.successor(x)

            if got != expected:
                print("Mismatch in successor:", x)
                print("Set:", sorted_s)
                print("Expected:", expected)
                print("Got:", got)
                return


def run_multiple_tests(n=100):
    success_count = 0

    for i in range(1, n + 1):
        try:
            randomized_test()
            success_count += 1
        except Exception as e:
            print(f"Test {i} failed with exception:", e)
            continue

    print(f"{success_count}/{n} randomized tests passed!")


run_multiple_tests(100)
