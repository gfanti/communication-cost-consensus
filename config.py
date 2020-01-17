import numpy as np


''' ----------------------------------------- '''
''' --------------- Figure 4 ---------------- '''
''' ----------------------------------------- '''
# Number of nodes to experiment with
ns = [1_000]

# Initial fractions of majority bits to cycle through
ps  = [0.7]

# Which protocols to try
# Options:
#   "poll3" - best of 3 polling
#   "simple" - our simple protocol
protocols = ["simple"]

# C parameter from paper
Cs = [7]

# Number of repeated trials per setting
trials = 1
# Maximum number of events we want to allow
ticks = 1_000_000

# Plot a timeseries at the end of the different agent counts?
plot_timeseries = True

# Save the results to file?
save_results = False

''' ----------------------------------------- '''
''' --------------- Figure 5 ---------------- '''
''' ----------------------------------------- '''
# # Number of nodes to experiment with
# ns = np.logspace(4, 7, 7)

# # Initial fractions of majority bits to cycle through
# ps  = [0.7]

# # Which protocols to try
# # Options:
# #   "poll3" - best of 3 polling
# #   "simple" - our simple protocol
# protocols = ["poll3", "simple"]

# # C parameter from paper
# Cs = [7]

# # Number of repeated trials per setting
# trials = 50
# # Maximum number of events we want to allow
# ticks = 1_000_000

# # Plot a timeseries at the end of the different agent counts?
# plot_timeseries = False

# # Save the results to file?
# save_results = True