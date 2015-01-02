import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import scipy.stats

def twoSampZ(X1, X2, mudiff, sd1, sd2, n1, n2):
    from numpy import sqrt, abs, round
    from scipy.stats import norm
    pooledSE = sqrt(sd1**2/n1 + sd2**2/n2)
    z = ((X1 - X2) - mudiff)/pooledSE
    pval = 2*(1 - norm.cdf(abs(z)))
    # print abs(z), norm.cdf(abs(z))
    # print pval
    return round(z, 3), round(pval, 4)

c = pd.read_csv("../cities.csv", encoding="latin-1")
county_population = c.groupby('County')['Population'].agg(sum).reset_index().\
                    rename(columns={'Population':'CountyPopulation'})

is_urban = (c.groupby('County')['Population'].agg(max) > 50000).astype(int).reset_index().\
           rename(columns={'Population':'IsUrban'})

c = pd.merge(pd.merge(c, county_population), is_urban)
d = pd.read_csv("../dataset0.csv", encoding="latin-1")

dset = pd.merge(d, c, left_on='ResolvedCity', right_on='City')

dset_noberk = dset[dset['County'] != 'Alameda']

def ex1():
    m = dset[dset['IsMobile'] == 1]['Population'].values
    d = dset[dset['IsPC'] == 1]['Population'].values

    # df = pd.DataFrame(d) #{'mobile': m, 'desktop': d})
    # plt.figure();
    # df.plot(kind='hist')
    # plt.show()

    print twoSampZ(np.mean(m), np.mean(d), 0,
                   np.std(m), np.std(d), len(m), len(d))

    m = dset[dset['IsMobile'] == 1]['CountyPopulation'].values
    d = dset[dset['IsPC'] == 1]['CountyPopulation'].values

    print twoSampZ(np.mean(m), np.mean(d), 0,
                   np.std(m), np.std(d), len(m), len(d))

def ex2():
    M_u =  dset[dset['IsMobile'] == 1 and dset['IsUrban'] == 1]
    M_nu = dset[dset['IsMobile'] == 1 and dset['IsUrban'] == 0]

    D_u =  dset[dset['IsMobile'] == 0 and dset['IsUrban'] == 1]
    D_nu = dset[dset['IsMobile'] == 0 and dset['IsUrban'] == 0]

ex2()
    

