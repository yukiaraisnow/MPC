class MPCCounter:
    def __init__(self):
        self.and_count = 0
        self.mul_count = 0
        self.depth = 0
        self.current_depth = 0
        self.rounds = 0

    def add_and(self, deps=1):
        self.and_count += 1
        self.mul_count += 1
        self.current_depth = max(self.current_depth + 1, deps)
        self.depth = max(self.depth, self.current_depth)
        self.rounds += 1

    def reset_depth(self):
        self.current_depth = 0

def and_(a, b, mpc: MPCCounter):
    mpc.add_and()
    return a & b

def xor_(a, b):
    return a ^ b

def aes_sbox_mpc(x, mpc: MPCCounter):
    x0, x1, x2, x3, x4, x5, x6, x7 = x

    t1  = and_(x0, x1, mpc)
    t2  = and_(x0, x2, mpc)
    t3  = and_(x0, x3, mpc)
    t4  = and_(x0, x4, mpc)
    t5  = and_(x0, x5, mpc)
    t6  = and_(x0, x6, mpc)
    t7  = and_(x0, x7, mpc)

    t8  = and_(x1, x2, mpc)
    t9  = and_(x1, x3, mpc)
    t10 = and_(x1, x4, mpc)
    t11 = and_(x1, x5, mpc)
    t12 = and_(x1, x6, mpc)
    t13 = and_(x1, x7, mpc)

    t14 = and_(x2, x3, mpc)
    t15 = and_(x2, x4, mpc)
    t16 = and_(x2, x5, mpc)
    t17 = and_(x2, x6, mpc)
    t18 = and_(x2, x7, mpc)

    t19 = and_(x3, x4, mpc)
    t20 = and_(x3, x5, mpc)
    t21 = and_(x3, x6, mpc)
    t22 = and_(x3, x7, mpc)

    t23 = and_(x4, x5, mpc)
    #t24 = and_(x4, x6, mpc)
    #t25 = and_(x4, x7, mpc)

    #t26 = and_(x5, x6, mpc)
    #t27 = and_(x5, x7, mpc)

    #t28 = and_(x6, x7, mpc)


    y0 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x0, t1), t2), t3), t4), t5), t6), t7)
    y1 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x1, t1), t8), t9), t10), t11), t12), t13)
    y2 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x2, t2), t8), t14), t15), t16), t17), t18)
    y3 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x3, t3), t9), t14), t19), t20), t21), t22)
    y4 = xor_(xor_(xor_(xor_(xor_(x4, t4), t10), t15), t19), t23)
    y5 = xor_(xor_(xor_(xor_(xor_(x5, t5), t11), t16), t20), t23)
    y6 = xor_(xor_(xor_(xor_(x6, t6), t12), t17), t21)
y7 = xor_(xor_(xor_(xor_(x7, t7), t13), t18), t22)






    
    # y0 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x0, t1), t2), t3), t4), t5), t6), t7)
    # y1 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x1, t1), t8), t9), t10), t11), t12), t13)
    # y2 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x2, t2), t8), t14), t15), t16), t17), t18)
    # y3 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x3, t3), t9), t14), t19), t20), t21), t22)
    # y4 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x4, t4), t10), t15), t19), t23), t24), t25)
    # y5 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x5, t5), t11), t16), t20), t23), t26), t27)
    # y6 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x6, t6), t12), t17), t21), t24), t26), t28)
    # y7 = xor_(xor_(xor_(xor_(xor_(xor_(xor_(x7, t7), t13), t18), t22), t25), t27), t28)

    return y7, y6, y5, y4, y3, y2, y1, y0

def lowmc_sbox_mpc(u0, u1, u2, mpc: MPCCounter):
    w0 = and_(u1, u2, mpc)
    w1 = and_(u0, u2, mpc)
    w2 = and_(u0, u1, mpc)

    v0 = xor_(u0, w0)
    v1 = xor_(xor_(u0, u1), w1)
    v2 = xor_(xor_(xor_(u0, u1), u2), w2)

    return v0, v1, v2

def bytes_to_bits(byte):
    return tuple((byte >> i) & 1 for i in reversed(range(8)))

def bits_to_bytes(bits):
    v = 0
    for b in bits:
        v = (v << 1) | b
    return v


def aes_round(state, mpc: MPCCounter):
    new_state = []
    for byte in state:
        x = bytes_to_bits(byte)
        y = aes_sbox_mpc(x, mpc)
        new_state.append(bits_to_bytes(y))
    return new_state

def aes_encrypt(state, mpc: MPCCounter, rounds=14):
    for _ in range(rounds):
        state = aes_round(state, mpc)
        mpc.reset_depth()
    return state

def lowmc_round(state_bits, mpc: MPCCounter):
    new_bits = []
    n = len(state_bits) // 3

    for i in range(n):
        u0, u1, u2 = state_bits[3*i:3*i+3]
        v0, v1, v2 = lowmc_sbox_mpc(u0, u1, u2, mpc)
        new_bits.extend([v0, v1, v2])

    new_bits.extend(state_bits[n*3:])
    return new_bits


def lowmc_encrypt(state_bits, mpc: MPCCounter, rounds=30):
    for _ in range(rounds):
        state_bits = lowmc_round(state_bits, mpc)
        mpc.reset_depth()
    return state_bits

mpc = MPCCounter()

state = [
    0x32, 0x43, 0xF6, 0xA8,
    0x88, 0x5A, 0x30, 0x8D,
    0x31, 0x31, 0x98, 0xA2,
    0xE0, 0x37, 0x07, 0x34
]

out = aes_encrypt(state, mpc)
print(out)
print(mpc.and_count, mpc.depth)


mpc = MPCCounter()
state_bits = [
    0,1,0,1,1,0,1,0,
    1,0,0,1,0,1,1,0,
    1,1,0,0,1,0,1,1,
    0,1,1,0,0,1,0,0,

    1,0,1,1,0,0,1,0,
    0,1,0,0,1,1,0,1,
    1,0,1,0,0,1,1,0,
    0,0,1,1,1,0,0,1,

    1,1,0,1,0,0,1,0,
    0,1,1,0,1,0,0,1,
    1,0,0,1,1,1,0,0,
    0,1,0,1,0,1,1,1,

    1,0,1,0,1,1,0,0
    0,1,1,0,0,1,1,0,
    1,0,0,1,0,1,0,1,
    0,1,0,0,1,0,1,1
]

out = lowmc_encrypt(state_bits, mpc)
print([int(''.join(map(str, out[i:i+8])), 2) for i in range(0, len(out), 8)])
print(mpc.and_count, mpc.depth)
