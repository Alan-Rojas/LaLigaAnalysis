# -*- coding: utf-8 -*-
"""LaLiga_Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YUvpd8LG_7_xBUrs4V-Vq5Udya0PA7U-
"""

# We start by loading the libraries used

import pandas as pd
import numpy as np
from google.colab import files
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
import plotly.express as px
from scipy.stats import pearsonr
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
import statsmodels.api as sm
import statsmodels.formula.api as smf

df = pd.read_csv('LaLigaPlayers_2.0-20222023.csv')

df.head()

# Since there are market values that hold value 0, we will input the mean.
df.Market_Value.replace(0,np.mean(df.Market_Value), inplace=True )
df.describe()

"""# We procede to drop outlier values that may ruin our analysis
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1

# This is the distance from the outside quartiles that we tolerate before calling a value an outlier.
QR_tolerance = 2.5


outliers = ((df < (Q1 - QR_tolerance * IQR)) | (df > (Q3 + QR_tolerance * IQR))).any(axis=1)
df = df[~outliers]
df.head()"""

# We are going to start by trying to see if by sight there appears to be a relation with any variable and the market value.
# first, we will separate non-numeric columns from the df, and form a new numeric-df.
n_df = df.drop(['Player_Name', 'Squad'], axis=1)
n_df.describe()

# Detecting Outlyers
# Boxplots
x_columns = list(n_df.columns) # Numeric Variables
x_columns.pop(-1) #Eliminating target variable
x_columns

# Boxplots

for element in x_columns:
  plt.boxplot(n_df[element])
  plt.title(str(element))
  plt.show()

# We will begin with scatter plots

for element in x_columns:
  plt.scatter(n_df[element], n_df['Market_Value'])
  plt.xlabel(str(element))
  plt.ylabel('Market_Value')
  plt.title(str(element)+' x Market Value')
  plt.show()

market_value = n_df['Market_Value']
n_df = n_df.drop('Market_Value', axis=1)

# We notice here that the Red Cards have a compressed box plot; meaning that all non-oulyer values are the same.
# Hence, we can drop Red Cards as a information source (columns) since all values (non-outlyers) have it in common.
x_columns.pop(6)
n_df = n_df.drop('RC', axis=1)
x_columns

# We see that there is not that much evidence to show that a single factor contributes the most to the player market value.
# What then?
# Perhaps we might consider that all the factors combined together create the market value, yet this is only a hypotesis.
# Meanwhile, since we have some attributes that seem to be not related at all to the market value (Red cards, Yellow cards, MOTM)
# a PCA might just be fit.

# We have now revised the possible relaion of our variables with our target variable, nvertheless, we might want to explore the possibility
# we are giving the program redundant information. Therefore, a heatmap of the correlation matrix is a great approach to knowing if two
# variables are correlated, and thus giving redundant information.

sns.heatmap(data = n_df.corr(), cmap ='Greens', linewidths = 0.30, annot =True, fmt='0.1f')

# We see that the correlation within App and MinP is really high (1), meaning that information will not be lost if one column in droppes
n_df = n_df.drop('App', axis=1)
x_columns.pop(1)
x_columns

# The first step to the PCA is to standarize all the variables, so the weight function in the PCA can work propperly.
# The basic function for standarizing a variable x into a standarized variable z is the following: z = (x - x.mean())/x.std()
# We will create a std_df:
scaler = StandardScaler()

std_df = pd.DataFrame(scaler.fit_transform(n_df), columns = n_df.columns)

std_df.head()

std_df.describe()

# The next step for the PCA is to create a Covariance matrix within the variables to see if there is any correlation within them.
# This is relevant because if the correlation of two variables (x,y) is high, we could assume that the info they both provide is redundant:
# In other words: info(x) ≈ info(y)
cov_matrix= np.cov(np.transpose(std_df))
cov_matrix
# Excellent

# We will procede to get the eigenvectors and eigenvalues of this matrix.
# Why? Well, the eigenvectors provide the direction of the components that carry information, the higher the eigenvalue
# of a vector, the more relevant the vector is.
e_values, e_vectors = np.linalg.eig(cov_matrix)
e_vectors

top_e_vals_indexes = np.argsort(e_values)[::-1]
e_values = e_values[top_e_vals_indexes]
e_vectors = e_vectors[top_e_vals_indexes]

e_values_sum = e_values.sum()
e_values_sum

# We will graph the % of the eigenvalues to see which contain the most information.
# For that we will only divide by the sum of all the values. Giving a value between 0 and 1.
e_values_sum = e_values.sum()
percentage_e_values = e_values/e_values_sum
percentage_e_values

plt.bar(list(range(0,11)),percentage_e_values, color = 'blue', width = 0.2)
plt.xlabel('Eigenvalues')
plt.ylabel('Info contained')
plt.title('Eigen_Values x Info')
plt.show()

# From here we can analyze some really interesting information: we can use the first 7 eigenvalues with the first 7 eigenvectors to keep
# Up to 90% of the information.
relevant_e_values = e_values[0:8]
relevant_e_vectors = pd.DataFrame(e_vectors)
relevant_e_vectors.drop(relevant_e_vectors.index[0:4], axis = 1, inplace=True)
relevant_e_vectors = relevant_e_vectors.values

relevant_e_vectors

x_columns

#After considering the relevant evectors for the analysis, we want to see and analyse how these new Principal Components describe the data.
# Hence, we are going to create a dataframe of eigenvectors that will be the principal components in a matrix form.
# We are going to name the component, based on the information provided by it, and give an interpretation from it.

# As the first step, we are going to add the column of the percentage each component represents to the dataframe.
eigenvectors_df = pd.DataFrame(relevant_e_vectors)
eigenvectors_df = np.transpose(eigenvectors_df) #Transpose the vectors so it becomes easier to analyse each variable.

#Changing the name of the components of the vectors
for i in range(len(x_columns)):
  eigenvectors_df.rename(columns={i:x_columns[i]}, inplace = True)

eigenvectors_df

# Adding the percentage they represent of the variance of the data:
eigenvectors_df['Relevance %'] = percentage_e_values[0:7]*100

eigenvectors_df

# Lets analyse these components with information that might help us to describe the players!
# The most relevant component is going to be called youth. Why? Age is the heavier variable that explains this component; followed by negative rating;  followed by the yellow ca ards which affect negatively.
# This makes sense because young players tend to have a high market value. And, players that perform badly (negative rating), are not as valuable.


# The second component will be called the supersub. This is because the components that affect the most are subapp; yellow cards, and rating.
# Both subbApp and rating are of high relevance; meanig that substitute players that perform well on the pitch, are more relevant.

# The third component will be called: no.9. This is the pure deffinition of a classical 9 striker. Low shots per game, high goals and many aerial duels won. The definition of
# Accuracy and efficiency in the goal making.

# The fourth component is called: The veteran. The component that affects the most is MinP: meaning experience on the field, followed by goals, and aerial duels won (negative).

# The fifth component is called the centre back. The components that affect the most are: AerialDuelsWon, Rating(negatively), MOTM (negatively) and assists (negatively).

# The component number 6 is called the offensive: With assists, shots per game and MOTM (negative), being the principal components.

# The last component is called the playmaker: With assists and rating being the more relevant components.

eigenvectors_df['Relevance %'].sum()
# qw

relevant_e_vectors.shape

std_df.shape

# In order to get the final df, we want to multiply the vector times the std_df. This so we can now decribe the info with the better info.
# Note: the vector must be transposed so it matches the number of columns, that way multiplicaton of matrices is possible.
# Resulting in the final dataframe:
PCA_df = std_df@relevant_e_vectors
#PCA_df['Player_Name'] = df['Player_Name']
PCA_df

# Creating ScatterPlots of the Principal Components: Looking for clusters.
Principal_C = list(PCA_df.columns)
#Principal_C.pop(-1)

for component in Principal_C:
  for i in range(len(Principal_C)):
    if (i < len(Principal_C)-1):
      fig = px.scatter(PCA_df, x=component, y=Principal_C[i+1], title=('Componente '+str(component) + ' x Componente '+str(Principal_C[i+1])))
      fig.update_traces(textposition='top right')
      fig.show()

# Since no clusters can be formed, we will perform a linear regression to see if there is a way to predict our target_variable ('Market_Value'), using our principal components.

x_reg = PCA_df
y_reg = market_value

Reg = linear_model.LinearRegression()
Reg.fit(x_reg,y_reg)

print('Intercept: \n', Reg.intercept_)
print('Coefficients: \n', Reg.coef_)
Reg.score(x_reg,y_reg)

# We have seen that the linear regression has failed to peredict a relevant amount
# of the data: 29%
# Therefore, we will proceed to the eigenanalysis to try and predict the target variable
# according to components: meaning, a regression of principal components with the target variable.

market_value.describe()

PCA_df['Market_Value'] = market_value

PCA_df.to_csv('LaLigaPlayers_PCA-20222023.csv', index = False)
files.download('LaLigaPlayers_PCA-20222023.csv')