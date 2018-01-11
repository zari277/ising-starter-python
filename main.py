import sys
import os
import time
import csv
import click
import numpy as np
import logging
import matplotlib.pyplot as plt
from tqdm import tqdm #fancy progress bar generator
from ising import run_ising #import run_ising function from ising.py

#simulation options (enter python main.py --help for details)
@click.command()
@click.option('--t_min', default=2.0, prompt='Minimum Temp', help='Minimum Temperature (inclusive)', type=float)
@click.option('--t_max', default=2.6, prompt='Maximum Temp', help='Maximum Temperature (inclusive)', type=float)
@click.option('--t_step', default=0.1, prompt='Temp Step Size', help='Temperature Step Size', type=float)

@click.option('--n', prompt='Lattice Size', help='Lattice Size (NxN)',type=int)
@click.option('--num_steps', default=100000, help='Total Number of Steps',type=int)
@click.option('--num_analysis', default=50000, help='Number of Steps used in Analysis',type=int)
@click.option('--num_burnin', default=0, help='Total Number of Burnin Steps',type=int)

@click.option('--j', default=1.0, help='Interaction Strength',type=float)
@click.option('--b', default=0.0, help='Applied Magnetic Field',type=float)
@click.option('--flip_prop', default=0.1, help='Proportion of Spins to Consider Flipping per Step',type=float)

def main(t_min,t_max,t_step,n,num_steps,num_analysis,num_burnin,j,b,flip_prop):

    filename = get_filename()

    check_step_values(num_steps, num_analysis, num_burnin)

    T = np.arange(t_min,t_max,t_step)

    temp_arr, M_mean_arr, E_mean_arr, M_std_arr, E_std_arr = [],[],[],[],[] #for plotting values

    #Write simulation parameters to file
    with open(filename,'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        #Write simulations parameters to CSV file
        writer.writerow(['Lattice Size (NxN)','Total Steps','Steps Used in Analysis','Burnin Steps','Interaction Strength','Applied Mag Field','Spin Prop'])
        writer.writerow([n,num_steps,num_analysis,num_burnin,j,b,flip_prop])
        writer.writerow([])

    print('\nSimulation Started! Data will be written to ' + filename + '\n')

    temp_range = tqdm(T) #set fancy progress bar range
    for index, temp in enumerate(temp_range):

        #show current temperature
        temp_range.set_description("Simulation Progress");

        try:
            #run the Ising model
            Msamp, Esamp = run_ising(n,temp,num_steps,num_burnin,flip_prop,j,b)

            try:
                #calculate statistical values
                M_mean = np.average(Msamp[-num_analysis:])
                E_mean = np.average(Esamp[-num_analysis:])
                M_std = np.std(Msamp[-num_analysis:])
                E_std = np.std(Esamp[-num_analysis:])

                #write data to CSV file
                header_array = ['Temperature','Magnetization Mean','Magnetization Std Dev','Energy Mean','Energy Std Dev']
                data_array = [temp,M_mean,M_std,E_mean,E_std]

                append_data_to_file(filename, temp, header_array) if index == 0 else None
                append_data_to_file(filename, temp, data_array)

                #for plotting
                temp_arr.append(temp)
                M_mean_arr.append(M_mean)
                E_mean_arr.append(E_mean)
                M_std_arr.append(M_std)
                E_std_arr.append(E_std)

            except:
                logging.error("Temp="+str(temp)+": Statistical Calculation Failed. No Data Written.")

        except KeyboardInterrupt:
            print("\n\nProgram Terminated. Good Bye!")
            sys.exit()

        except:
            logging.error("Temp="+str(temp)+": Simulation Failed. No Data Written")

    print('\n\nSimulation Finished! Data written to '+filename)
    plot_graphs(temp_arr, M_mean_arr, E_mean_arr, M_std_arr, E_std_arr)

def get_filename(dirname='data'):
    #Make data folder if doesn't exist, then specify filename
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    filename = os.path.join(dirname,str(time.strftime("%Y%m%d-%H%M%S"))+".csv")
    return filename

def append_data_to_file(filename, temp, data_array):
    try:
        with open(filename,'a') as csv_file: #appends to existing CSV File
            writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
            writer.writerow(data_array)
    except:
        logging.error("Temp="+str(temp)+": Error Writing to File")

def check_step_values(num_steps, num_analysis, num_burnin):
    #simulation size checks and exceptions
    if (num_burnin > num_steps):
        raise ValueError('num_burning cannot be greater than available num_steps')
        sys.exit()

    if (num_analysis > num_steps - num_burnin):
        raise ValueError('num_analysis cannot be greater than available num_steps after burnin')
        sys.exit()

def plot_graphs(temp_arr, M_mean_arr, E_mean_arr, M_std_arr, E_std_arr):

    plt.figure(1)
    plt.errorbar(temp_arr, M_mean_arr, yerr=M_std_arr, fmt='o')
    plt.xlabel('Temperature')
    plt.ylabel('Magnetization')

    plt.figure(2)
    plt.errorbar(temp_arr, E_mean_arr, yerr=E_std_arr, fmt='o')
    plt.xlabel('Temperature')
    plt.ylabel('Energy')

    plt.show()

if __name__ == "__main__":
    print("\n2D Ising Model Simulation\n")
    main()
