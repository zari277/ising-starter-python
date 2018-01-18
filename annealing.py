def T_anneal(T, ii, num_steps, num_burnin):

    #implement annealing code here

    if ii<(num_burnin):
        T_a = T - (ii/(num_burnin)) + 1;

    else:
        T_a = T;

    return float(T_a)

def B_anneal(B, ii, num_steps, num_burnin):

    #implement annealing code here

    B_a = B

    return float(B_a)
