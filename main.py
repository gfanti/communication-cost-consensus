'''
	This script tests Dandelion spreading on random regular graphs.
	There are several variants, including quasi-regular constructions.
'''


from sim import *


import numpy as np
import matplotlib.pyplot as plt
import collections
import math
import scipy.io as sio
from config import *
import cProfile, pstats, io
from pstats import SortKey


def run(n, protocol, p=0.6, ticks=100, C = 10):
    ''' Run simulation'''
    if protocol == "simple":
        sim = SimpleSim(n, p, ticks, C)
    else:
        sim = Sim(n, p, ticks)
    metrics = sim.run_sim()
    return metrics


if __name__=='__main__':

    pr = cProfile.Profile()
    pr.enable()

    for C in Cs:
        print("C is ", C)
        for protocol_name in protocols:
            print("Processing protocol ", protocol_name)
            for p in ps:
                print("p value", p)

                total_comms = []
                total_stds = []
                total_time = []
                total_converged = []
                for n in ns:
                    n = int(n)
                    print("n is ", n)
                    res = []
                    conv = 0
                    time = []
                    num_experts_tot = []
                    for i in range(trials):
                        metrics = run(n, protocol_name, p, ticks, C)
                        if protocol_name == "simple":
                            (comms, converged, time_elapsed, timeseries, type_timeseries) = metrics
                        else:
                            (comms, converged, time_elapsed, timeseries) = metrics
                        # print("Comms:", comms, "Converged to correct bit?", converged,
                            #   "Time elapsed", time_elapsed)
                        if converged:
                            res += [comms]
                            conv += 1
                            time += [time_elapsed]

                    print("Total comms: ", res)
                    print("Standard deviation: ", np.std(res))
                    total_comms += [np.mean(res)]
                    total_stds += [np.std(res)]
                    total_converged += [float(conv)/trials]
                    total_time += [np.mean(time)]

                    if save_results:
                        filename = f"results/c{C}/{protocol_name}_p_{p}.mat"
                        results = {
                            'ns': ns,
                            'comms': total_comms,
                            'stds': total_stds,
                            'converged': total_converged,
                            'time': total_time
                        }
                        if plot_timeseries:
                            results['timeseries'] =  timeseries
                            if protocol_name == "simple":
                                results['type_timeseries'] = type_timeseries
                        sio.savemat(filename, results)


                print("n:", ns)
                print("Communications:", total_comms)
                print("Std devs:", total_stds)
                print("Fraction converged:", total_converged)
                print("Time elapsed:", total_time)


                if plot_timeseries:
                    plt.figure()
                    ax = plt.gca()
                    ratio = 0.5
                    beliefs = ["0", "1"]
                    for k in timeseries.keys():
                        plt.plot(timeseries[k], label = beliefs[k])
                    plt.legend(loc='center')
                    plt.ylim(0,n)
                    ax.set_aspect(1.0/ax.get_data_ratio()*ratio)
                    # plt.title(f"Belief Bit Timeseries {protocol_name}")
                    plt.savefig(f"results/c{C}/{protocol_name}_beliefs.pdf")
                    plt.pause

                    if protocol_name == "simple":
                        types = ['Aspirant','Expert (Estimation Phase)', 'Expert (Pushing Phase)',
                                'Regular', 'Terminal']
                        plt.figure()
                        for k in type_timeseries.keys():
                            plt.plot(np.divide(np.arange(len(type_timeseries[k])),n), np.divide(type_timeseries[k],n), label = types[k])
                        plt.legend(loc='center',fontsize=14)
                        plt.ylim(0,1)
                        plt.xlabel('Time (s)', fontsize=14)
                        plt.ylabel('Fraction of nodes', fontsize=14)
                        # plt.title("Node type distribution, Simple protocol")
                        ax = plt.gca()
                        ax.set_aspect(1.0/ax.get_data_ratio()*ratio)
                        plt.savefig(f"results/c{C}/{protocol_name}_types.pdf")
                        plt.pause
                        plt.show()
    # ... do something ...
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(20)
    # print(s.getvalue())


