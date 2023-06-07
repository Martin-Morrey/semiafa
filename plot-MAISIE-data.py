import pandas as pd
import sys
import matplotlib.pyplot as plt
import semiafa
import maisie


if __name__ == "__main__":

    # Read the MAISIE CSV file into a Pandas DataFrame

    # get file path from config or command line argument
    if len(sys.argv) < 2:
        maisie_df = maisie.readMaisie() # config
    else:
        csv_file_path = sys.argv[1] # command line
        maisie_df = maisie.readMaisie(csv_file_path)


    fig, ax = plt.subplots()

    # ice and sea extent
    ax.plot(maisie_df['date'], maisie_df['Marginal and Central Normalised'], label='MAISIE Central and Marginal Seas')

    # add the model data
    model_data = semiafa.runModel(18)
    ax.plot(model_data['date'],model_data['sie'], label='model SIE')
    #ax.plot(model_data['date'],model_data['solar_heat'], label='model Solar Heat')

    # To Do
    # normalise MAISIE data based on mean yearly-maximum, or by dropping outliers
    # - Return mean square difference between MAISIE and model results for optimiser
    # - - get yyyyddd keys out of maisie_df, and use to filter model_data
    # - - put SIE from both into a single dataframe, diff values, and square
    # - - calc mean value of the column

    # Set plot title and labels
    plt.title('MAISIE Data vs Ice Melt Model')
    plt.xlabel('month/year')
    plt.ylabel('normalised value')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()
