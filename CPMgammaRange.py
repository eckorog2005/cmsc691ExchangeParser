__author__ = 'roger'

import igraph as ig
import louvain
import pandas as pd
import matplotlib.pyplot as plt

G = ig.read("test.graphml")
res_parts = louvain.bisect(G, method='CPM', resolution_range=[0.004, 0.004])

res_df = pd.DataFrame({
         'resolution': res_parts.keys(),
         'bisect_value': [bisect.bisect_value for bisect in res_parts.values()]})
plt.step(res_df['resolution'], res_df['bisect_value'])
plt.xscale('log')
plt.title('CPM bisect for resolution parameter')
plt.show()