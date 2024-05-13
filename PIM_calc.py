import math
import numpy as np


def main(args):

    # calculate the number times the col/row will change
    row_changes = int(args['mat_k']/args['bank_row_size'])
    col_changes = args['mat_k']

    # Latency to perform a single MAC
    op_time_ss = args["MAC_op_cycle"] / (1e+6 * args["accel_freq"])
    op_latency = args["MAC_latency"] / (1e+6 * args["accel_freq"])
    # Latency to activate row
    RAS_time = args["t_RAS"] / (1e+6 * args["DDR_freq"])
    # Latency to activate/select column
    CAS_time = args["t_CAS"] / (1e+6 * args["DDR_freq"])
    # Latency to precharge a row
    RP_time = args["t_RP"] / (1e+6 * args["DDR_freq"])

    print("steady state OP TIME:", op_time_ss)
    print("single OP TIME:", op_latency)
    print("RAS TIME:", RAS_time)
    print("CAS TIME:", CAS_time)
    print("RP TIME:", RP_time)
    print("Row changes", row_changes)
    print("Col changes", col_changes)
    # reuse_factor is the number of vectors stored in the global buffer.
    matmul_time = []
    for reuse_factor in range(1, 50):
        # pipelined is no bueno
        # mac_time = (reuse_factor-1) * op_time_ss + op_latency
        mac_time = (reuse_factor) * op_latency
        # print("MAC TIME:", mac_time)
        # calculate the total delay from the row changes
        t_row = max(row_changes * mac_time, row_changes * (RAS_time + RP_time))

        # calculate the total delay from the col changes
        t_col = max(col_changes * mac_time, col_changes * CAS_time)

        # matrix vector multiplication latency. If there are multiple vectors
        # in the global buffer, multiple mv ops may be done in one mv_time.
        mv_time = (t_row + t_col)
        num_iterations = math.ceil(
            args["mat_m"]/16) * math.ceil(args["mat_n"]/reuse_factor)
        matmul_time.append(mv_time * num_iterations *
                           1e3)  # time in ms (x1000)

    # print("Matmultimes:", np.around(matmul_time, 3))
    print("Best reuse factor:", np.argmin(matmul_time) +
          1, matmul_time[np.argmin(matmul_time)])

    with open("times.csv", "w") as f:
        for idx, entry in enumerate(matmul_time):
            f.write(str(idx + 1) + "," + str(entry) + "\n")


# Timings for DRAM are in CAS-RCD-PRE-RAS. Ours is 16-18-18-36
if __name__ == "__main__":
    args = {
        # Matrix dimensions. A * B = C. A: M x N, B: N x K, C: M x K
        "mat_m": 2000,
        "mat_n": 2000,
        "mat_k": 2000,
        "DDR_freq": 1600,           # 1600 MHz (DDR4-3200)
        "accel_freq": 1600,          # 800 MHz
        # 1 Op per cycle at steady state. (assuming initiation interval of 1)
        "MAC_op_cycle": 1,
        "MAC_pipeline_stages": 4,
        "MAC_latency": 4,
        "t_RAS": 36,  # DRAM timings are in cycles.
        "t_RCD": 18,
        "t_RP": 18,
        "t_CAS": 16,
        # 1024 matrix elements per row (2kB, 2B per element)
        "bank_row_size": 1024,
        "num_banks": 16
    }

    main(args)
