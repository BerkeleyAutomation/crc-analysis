from __future__ import division
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

def dict_to_df(d):
    return pd.DataFrame(dict([ (k, pd.Series(v)) for k,v in d.iteritems() ]))

def twoSampZProp(x1, x2, n1, n2):
    p_hat = float(x1 + x2)/(n1 + n2)
    z, pval = _twoSampZ(x1/n1, x2/n2, 0, 1, 1, n1, n2)
    z = z * 1.0/np.sqrt(p_hat * (1-p_hat))
    pval = 2*(1 - scipy.stats.norm.cdf(np.abs(z)))
    return z, pval

def twoSampZ(Y1, Y2, mudiff=0):
    return _twoSampZ(np.mean(Y1), np.mean(Y2),
                     mudiff,
                     np.std(Y1), np.std(Y2),
                     len(Y1), len(Y2))

def _twoSampZ(X1, X2, mudiff, sd1, sd2, n1, n2):
    pooledSE = np.sqrt(sd1**2/n1 + sd2**2/n2)
    z = ((X1 - X2) - mudiff)/pooledSE
    pval = 2*(1 - scipy.stats.norm.cdf(np.abs(z)))
    # print abs(z), norm.cdf(abs(z))
    # print pval
    return np.round(z, 3), np.round(pval, 4)

def num_slider_interactions(dset):
    return sum([dset['Event: slider_set ' + str(i+1)] for i in range(6)])

def num_sliders_interacted_with(dset):
    return sum([dset['Event: slider_set ' + str(i+1)].astype(bool).astype(int)
                for i in range(6)])

def level(row):
    # Begin, Grade, Rate, Suggestion
    level = 0
    if row['Event: first time']: level = 1
    if row['NumSliderInteractions']: level = 2
    if row['Event: rated']: level = 3
    if row['Event: comment submitted']: level = 4
    return level

c = pd.read_csv("../census.csv")[['zip', 'primary_city', 'county', 'estimated_population',]]
c2 = pd.read_csv("../2010census.csv")
c = pd.merge(c, c2, how='left')

city_population = c.groupby('primary_city')['2010Census'].agg(sum).reset_index().\
                    rename(columns={'2010Census':'CityPopulation'})
county_population = c.groupby('county')['2010Census'].agg(sum).reset_index().\
                    rename(columns={'2010Census':'CountyPopulation'})
is_urban = (c.groupby('county')['2010Census'].agg(max) > 50000).astype(int).reset_index().\
           rename(columns={'2010Census':'IsUrban'})

c = pd.merge(pd.merge(c, pd.merge(county_population, is_urban)), city_population)
c.to_csv("census_fixed.csv")

data = [pd.read_csv("../dataset0.csv"),
        pd.read_csv("../dataset1.csv")]

for i, d in enumerate(data):
    dset = pd.merge(d, c, left_on='ResolvedZip', right_on='zip')
    dset['NumSliderInteractions'] = num_slider_interactions(dset)
    dset['NumSlidersIteractedWith'] = num_sliders_interacted_with(dset)
    # dset['ToClean'] = dset.apply(to_clean, axis=1)
    dset['Level'] = dset.apply(level, axis=1)
    dset['UrbanCity'] = (dset['CityPopulation'] > 50000).astype(int)
    data[i] = dset
    dset.to_csv("joined" + str(i) + ".csv")

dset = data[0]
d0 = data[0]
d1 = data[1]

def ex0():
    df = dict_to_df({ "v1": d0['DeviceType'].value_counts(),
                      "v2": d1['DeviceType'].value_counts()})
    x, y = df.plot(kind='pie', subplots=True, autopct='%.2f', legend=False, title='Device Type')
    x.axis('equal')
    y.axis('equal')
    plt.savefig('DeviceType.png', bbox_inches='tight')
    
    def cleanup_os(dset):
        os = dset['OS'].map(lambda x: x if not x.startswith("Windows") else "Windows")
        os = os.value_counts(normalize=True)
        # print os
        os, other = os[os > 0.05],sum(os[os < 0.05])
        os['Other'] = other
        return os

    df = dict_to_df({ "v1": cleanup_os(d0),
                      "v2": cleanup_os(d1)})

    plt.close()
    fig = plt.figure()
    x, y = df.plot(kind='pie', subplots=True, autopct='%.2f', legend=False, title='Device OS')
    x.axis('equal')
    y.axis('equal')
    fig.subplots_adjust(hspace=100)
    plt.savefig('OS.png')

    
def ex1_prop(dset, urban='IsUrban'):
    # rural desktop, rural total, urban desktop, urban total

    x1 = len(dset[ (dset[urban] == 0) & (dset['IsPC'] == 1) ])
    n1 = len(dset[dset[urban] == 0])
    x2 = len(dset[ (dset[urban] == 1) & (dset['IsPC'] == 1) ])
    n2 = len(dset[dset[urban] == 1])
    print x1, n1, x2, n2
    print twoSampZProp(x1, x2, n1, n2)
    
def ex1(dset):
    #for i, dset in enumerate([d0, d1]):
    m0 = d0[d0['IsMobile'] == 1]['CountyPopulation'].values
    p0 = d0[d0['IsPC'] == 1]['CountyPopulation'].values

    m1 = d1[d1['IsMobile'] == 1]['CountyPopulation'].values
    p1 = d1[d1['IsPC'] == 1]['CountyPopulation'].values


    df = dict_to_df({'mobile-v1': m0, 'PC-v1': p0, 'mobile-v2':m1, 'PC-v2':p1})
    plt.figure();
    df.plot(kind='hist', subplots=1, sharey=1, title='County Population', layout=(2,2))
    plt.savefig('county' + '.png')

    print twoSampZ(m0, p0)
    print twoSampZ(m1, p1)

def ex2(dset, exclude_non_zero=False):
    M_u =  dset[(dset['IsMobile'] == 1) & (dset['IsUrban'] == 1)]
    M_nu = dset[(dset['IsMobile'] == 1) & (dset['IsUrban'] == 0)]

    D_u =  dset[(dset['IsMobile'] == 0) & (dset['IsUrban'] == 1)]
    D_nu = dset[(dset['IsMobile'] == 0) & (dset['IsUrban'] == 0)]

    M = dset[(dset['IsMobile'] == 1)]
    D = dset[(dset['IsMobile'] == 0)]

    for x in ['NumSlidersIteractedWith', 'Num Ratings Given']:
        plt.close()
        # m_u = M_u[M_u[x] != 0]
        # m_nu = M_nu[M_nu[x] != 0]

        # d_u = D_u[D_u[x] != 0]
        # d_nu = D_nu[D_nu[x] != 0]
        
        # print x
        # print "urban: ", twoSampZ(m_u[x].values, d_u[x].values)
        # print "non urban: ", twoSampZ(m_nu[x].values, d_nu[x].values)
        
        if exclude_non_zero:
            y, z = M[M[x] != 0], D[D[x] != 0]
        else:
            y, z = M, D

        if x == 'Num Ratings Given':
            y = y[y[x] < 12]
            z = z[z[x] < 12]
            
        print twoSampZ(y[x], z[x])

        df = dict_to_df({'mobile': y[x].values,
                         'desktop': z[x].values})
        # plt.figure();

#            df = dict_to_df({'mobile': filter(lambda x: x < 12, y[x].values),
 #                            'desktop': filter(lambda x: x< 12, z[x].values)})

        df.plot(kind='hist', subplots=1, sharey=1, title=x)
        plt.savefig(x + '.png')

def ex3(dset):
    M_u =  dset[(dset['IsMobile'] == 1) & (dset['IsUrban'] == 1)]
    M_nu = dset[(dset['IsMobile'] == 1) & (dset['IsUrban'] == 0)]

    D_u =  dset[(dset['IsMobile'] == 0) & (dset['IsUrban'] == 1)]
    D_nu = dset[(dset['IsMobile'] == 0) & (dset['IsUrban'] == 0)]

    M = dset[(dset['IsMobile'] == 1)]
    D = dset[(dset['IsMobile'] == 0)]

    for x, y in [(M,D)]: #[(M_u, D_u), (M_nu, D_nu), (M, D)]:
        x, y = x['Level'].values, y['Level'].values
        print scipy.stats.mannwhitneyu(x, y)
        df = dict_to_df({'mobile': x,
                     'desktop': y})
        plt.figure();
        df.plot(kind='hist', subplots=1, sharey=1, title='Level')
        plt.savefig('Level' + '.png')

def geo(dset, urbanf='IsUrban'):
    urban = dset[ (dset[urbanf] == 1) ]['IsMobile']
    rural = dset[ (dset[urbanf] == 0) ]['IsMobile']

    urban, rural = urban.value_counts(), rural.value_counts()
    obs = np.array([
        [urban.ix[0], urban.ix[1]],
        [rural.ix[0], rural.ix[1]],
    ])
    chi2, p, dof, expected = scipy.stats.chi2_contingency(obs)
    print chi2, p, # dof, expected

def pg1chart():
    for urban in ['IsUrban', 'UrbanCity']:
        print "======================================="
        print len(d0[ (d0[urban] == 1) & (d0['IsMobile'] == 1) ])
        print len(d0[ (d0[urban] == 0) & (d0['IsMobile'] == 1) ])
        print len(d1[ (d1[urban] == 1) & (d1['IsMobile'] == 1) ])
        print len(d1[ (d1[urban] == 0) & (d1['IsMobile'] == 1) ])
        print "--------------------------------"
        print len(d0[ (d0[urban] == 1) & (d0['IsMobile'] == 0) ])
        print len(d0[ (d0[urban] == 0) & (d0['IsMobile'] == 0) ])
        print len(d1[ (d1[urban] == 1) & (d1['IsMobile'] == 0) ])
        print len(d1[ (d1[urban] == 0) & (d1['IsMobile'] == 0) ])


def p1():
    joined = pd.concat([d0, d1])
    for d in [d0, d1, joined]:
        ex1(d)
        print ex1_prop(d)
        print geo(d)
        print "================"
    
