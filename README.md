This repository contains the code for the simulations in "Communication cost of consensus for nodes with limited memory" (Fanti, Holden, Peres, Ranade), 2019.

## Dependencies:
- python3
- numpy
- matplotlib
- collections
- cProfile

## Experiments
By default, the config file produces Figure 4. Instructions on how to produce Figures 4 and 5 are included below.

### Figure 4
1) Uncomment the configurations in section 'Figure 4' of config.py, and comment out the configurations for 'Figure 5'.
2) Run `python main.py`

### Figure 5
1) Uncomment the configurations in section 'Figure 5' of config.py.
2) Create a directory called `./results/c7`.
3) Run `python main.py`
