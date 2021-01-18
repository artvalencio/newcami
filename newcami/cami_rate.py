def cami_rate(x,y,symbolic_type='equal-divs',n_symbols=2,tau=1,L_limit=6,units='bits',make_plot=False,verbose=False):
    ''' Calculates the Causal Mutual Information Rate
        between two variables given their
        observable time-series.

    Parameters
    ----------
    x: list, tuple, np.array, pd.Series
        The first time-series
    y: list, tuple, np.array, pd.Series
        The second time-series
    symbolic-type: str, optional
        Type of symbolic encoding. Options:
            - 'equal-divs': equal-sized divisions are
                applied across the range of x and y, i.e.
                uniform-length marginal partitions (default)
            - 'equal-points': divisions are selected such
                that the same number of points is present
                in each box, i.e. uniform-density
                partition
            - 'equal-growth': equal-sized divisions are
                applied according to the growth (first
                derivative) of the data
            - 'equal-growth-points': divisions are selected
                such that each growth box has the same number
                of points
            - 'equal-concavity': equal-sized divisions are
                applied according to the concavity (second
                derivative) of the data
            - 'equal-concavity-points': divisions are selected
                such that each concavity box has the same
                number of points
    n_symbols: int, optional
        Number of symbolic symbols, or marginal partition
        resolution. If n_symbols=2, the partition is
        binary (0,1) (default). If n_symbols=3, it is ternary
        (0,1,2), and so on.
    L_limit: int, optional
        Limit maximum of the symbolic sequence length to calculate
        Causal Mutual Information from. It should be sufficient to
        enable identification of linear CaMI x L section, but values
        too high come with computational cost without significant
        benefits. Default: 6.
    units: str, optional
        Units to be used (base of the logarithm). Options:
            - 'bits': log2 is adopted (default)
            - 'nat': ln is adopted
            - 'ban': log10 is adopted
    make_plot: bool, optional
        Whether to plot CaMI x L graph. Default: False.
    verbose: bool, optional
        Displays extra information about the calculation. Default: False.
    
    Returns
    -------
    camir: float
        The value of the Causal Mutual Information Rate in the direction X->Y

    See Also
    --------
    mutual_info_rate: calculates the Mutual Information Rate
        between two variables from time-series data
    cami: calculates the Causal Mutual Information
        from time-series data
    transfer_entropy: calculates the Transfer Entropy
        from time-series data
    multithread_causality: calculates information-theory
        measures from many individual short time-series
        of the same phenomena instead of using a single
        long time-series
    mi_rate: calculates the Mutual Information Rate
        with respect to the symbolic length
    pointwise: calculates the pointwise contributions to
        the information measurements
    total_correlation: calculates the ammount of mutual
        of a set of variables

    Example
    -------
    cami_rate(x,y,symbolic_type='equal-points',n_symbols=10,units='bits')
    '''
    #import libraries
    import numpy as np
    import pandas as pd
    import newcami as cami
    from scipy.stats import linregress

    #checking if minimum L_limit is satified
    if L_limit<3:
        raise ValueError('L_limit must be equal or greater than 3')

    #interpolate missing data or trim if its in the edges
    x,y=pd.to_numeric(x,errors='coerce'),pd.to_numeric(y,errors='coerce')
    while np.isnan(x[0]) or np.isnan(y[0]):
        x,y=x[1:],y[1:]
    while np.isnan(x[-1]) or np.isnan(y[-1]):
        x,y=x[:-1],y[:-1]
    def interp_func(data):
        idx_bads=np.isnan(data)
        idx_goods=np.logical_not(idx_bads)
        data_good=data[idx_goods]
        interp_data=np.interp(idx_bads.nonzero()[0],idx_goods.nonzero()[0],data_good)
        data[idx_bads]=interp_data
        return data
    x,y=interp_func(x),interp_func(y)

    #calculate cami as a function of symbolic length
    cami_val=np.zeros(L_limit)
    for L in range(1,L_limit+1):
        cami_val[L-1]=cami.cami(x,y,symbolic_type=symbolic_type,n_symbols=n_symbols,symbolic_length=L,tau=tau,units=units)

    #finding the linear part (or the closest to linear)
    cami_diff2=np.diff(np.diff(cami_val))
    a=min(abs(cami_diff2))
    find_a=np.where(cami_diff2==a)
    find_b=np.where(cami_diff2==-a)
    if len(find_a[0])>0:
        idx=find_a[0][0]
    else:
        idx=find_b[0][0]
    #perform linear regression
    camir=linregress(np.arange(3)+idx+1,cami_val[idx:idx+3]).slope
    #display result
    if verbose==True:
        print('Causal Mutual Information Rate based on fitting from L=',idx+1,' to L=',idx+3,': ', camir)

    #plot CaMI vs L
    if make_plot==True:
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(np.arange(L_limit)+1,cami_val)
        plt.xlabel('Symbolic length (L)')
        plt.ylabel('Causal Mutual Information ['+units+']')
        plt.show()

    #return results
    return camir
