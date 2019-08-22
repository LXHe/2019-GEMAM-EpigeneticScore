# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 09:37:56 2019

@author: u0105352

Linear plot in real and estimated muscular values.
"""
#%% Import libraries and raw dataset
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

raw_path = r'.\muscle_epi_gps.xlsx'
raw = pd.read_excel(raw_path, sheet_name = 'muscle_epi_gps', usecols = 'C,F,I:L,BX,CG,CO')
raw = raw.rename(columns = {'all_total_sum': 'MS_sar', 'sum_cpg_avg': 'MS_snp', 'snp_sum': 'GPS_snp'})
    
#%% Create a class function for two MS adjusted for GPS

class ScoreFunction:
    '''
        Linear regression, plotting of specified scores
    '''
    
    # Set global variables that can be used in all methods
    global dep_var, score_dict
    # Define dependent variables
    dep_var = ['BCP_THK', 'VL_ACSA', 'EBTQ', 'KNTQ']
    # Set score dictionary for annotation
    score_dict = {'MS_sar': 'MS$_\mathrm{SAR}$',
                  'MS_snp': 'MS$_\mathrm{SNP}$',
                  'GPS_snp': 'GPS$_\mathrm{SNP}$'}
    
    # Initialize score name
    def __init__(self, score_name):
        self.score_name = score_name
        
    # OLS method
    def ols_function(self, *args):
        '''
            Linear regression function.
            With selected covariates.
            Returns ols results and score values used in each calculation
        '''

        pred_value = []
        x_value = []
        y_value = []

        for i in dep_var:
            # Create a dataset with the corresponding muscular parameter
            # Convert tuple args into a list
            ana_df = raw[list(args) + [self.score_name] + [i]]
            
            # Drop missing values
            ana_df.dropna(inplace = True)
            
            # Build a linear model
            X = ana_df.drop(columns = [i]).values
            y = ana_df[i].values
            
            X = sm.add_constant(X)
            ols_model = sm.OLS(y, X)
            results = ols_model.fit()
            pred_rlt = results.predict(X)
            
            pred_value.append(pred_rlt)
            x_value.append(ana_df[self.score_name].values)
            y_value.append(y)
            
            # Create result dictionary by dependent variables
            pred_value_dict = dict(zip(dep_var, pred_value))
            x_value_dict = dict(zip(dep_var, x_value))
            y_value_dict = dict(zip(dep_var, y_value))
            
            self.pred_value_dict = pred_value_dict
            self.x_value_dict = x_value_dict
            self.y_value_dict = y_value_dict
            
        return self.pred_value_dict, self.x_value_dict, self.y_value_dict
    
    # Plotting method
    def create_plot(self):
        '''
            Create scatter plot for actual and predicted values
        '''
        
        fig, ax = plt.subplots(
            figsize = (12, 6), dpi = 150, nrows = 2, ncols = 2
        )
        
        plt.rcParams['font.sans-serif'] = ['Arial']
        plt.rcParams['font.size'] = 8
        
        msl_anno = ['THK$_\mathrm{BB}$(cm)',
                    'ACSA$_\mathrm{VL}$(cm$^\mathrm{2}$)',
                    'MVC$_\mathrm{EF}$(N·m)',
                    'MVC$_\mathrm{KE}$(N·m)']
        
        for idx in range(len(msl_anno)):
            
            ax[idx//2][idx%2].scatter(
                x = self.x_value_dict[dep_var[idx]], 
                y = self.y_value_dict[dep_var[idx]],
                label = 'Actual', alpha = 0.7, 
                marker = 'o', edgecolors = 'none'
            )
            ax[idx//2][idx%2].scatter(
                x = self.x_value_dict[dep_var[idx]], 
                y = self.pred_value_dict[dep_var[idx]], 
                label = 'Predicted', alpha = 0.7, 
                marker = '*', edgecolors = 'none'
            )
            
            # Legend outside a plot
            ax[idx//2][idx%2].legend(loc = 1, bbox_to_anchor = (1.25, 1.04))
            
            ax[idx//2][idx%2].set_xlabel(score_dict[self.score_name])
            ax[idx//2][idx%2].set_ylabel(msl_anno[idx])
            ax[idx//2][idx%2].set_title('Actual and predicted values of {}'.format(msl_anno[idx].split("(")[0]))
              
        plt.subplots_adjust(top = 0.87, wspace = 0.4, hspace = 0.4)
        plt.suptitle('Actual and predicted muscular values given {}'.format(score_dict[self.score_name] + ' (GPS$_\mathrm{SNP}$ adjusted)'),
            fontsize = 12)
        
        plt.show()
        
        plt.savefig("muscular_values_{}_GPS_adjusted.png".format(self.score_name), bbox_inches='tight')
#%% Main function with GPS_snp as a covariate  
def main():
    '''
        The main function, asking for input score values
    '''
    score_name = input("Please enter score name (MS_sar or MS_snp).\nOr enter quit:")
    if score_name == 'quit':
        print('Program stops now.')
    else:
        score = ScoreFunction(score_name)
        score.ols_function('Age', 'BMI', 'GPS_snp')
        score.create_plot()
        print('Plot is completed.')
    
if __name__ == '__main__':
    main()