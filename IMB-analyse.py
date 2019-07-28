import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse


sns.set(style='ticks')

parser = argparse.ArgumentParser()
parser.add_argument('-f','--files', nargs=2, help='log files', required=True)
parser.add_argument('-o','--output', default='results-out.png')
my_vars = parser.parse_args()


log_bench = my_vars.files
output_f = my_vars.output
data = []

for log in log_bench :

  with open(log) as f_input :
    print("Processing log file: {}".format(log))
    launcher = 'mpirun' if 'mpirun' in log else 'srun'
    lines = f_input.readlines()

    for line in lines:
        if "Benchmarking" in line:
          benchmark = line.strip().split(" ")[2]
        if '#' not in line[0]:
          values = [float(number) for number in re.findall(r'\d+\.?\d*',line)]
          if len(values) == 5:
            data.append({'launcher': launcher,'benchmark': benchmark,'bytes': values[0], 'repetitions': values[1], 't_min': values[2], 't_max': values[3],'t_avg':values[4]})


df = pd.DataFrame(data)

bench_df = df[df.benchmark.isin(['Bcast','Reduce','Gather','Allgatherv','Alltoallv'])]

data_fg = sns.FacetGrid(bench_df, row='benchmark',hue='launcher',aspect=3,sharey=False)#,margin_titles=True)
data_fg.map(plt.scatter,"bytes","t_avg")

ax = data_fg.axes[0,0]
ax.set_xscale('log',basex=2)
ax.set_yscale('log')
data_fg.set(xlim=(1,4294304*2))
data_fg.add_legend(title='Launcher')
data_fg.set_titles('{row_name}')
data_fg.set_ylabels('Temps moyen [us]')
print("Saving figure in: {}".format(output_f))
data_fg.savefig(output_f)
