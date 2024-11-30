# -*- coding: utf-8 -*-
"""cell_network_analysis_forecasting

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1s59Jx6whe2L0ICJ6w_NBQEz71o4cVJaa

#**Task 1**

#importing libraries
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np


from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score



import warnings
warnings.filterwarnings('ignore')

"""# mounting Drive"""

from google.colab import drive
drive.mount('/content/drive')

"""# reading the csv files"""

data_dir = '/content/drive/MyDrive/task 1/'
data_list = []

# Load each file into a DataFrame and store it in the list
for day in range(1, 16):
    file_path = os.path.join(data_dir, f'features_day{day}.csv')
    df = pd.read_csv(file_path)
    data_list.append(df)

#concatenate all DataFrames into a single DataFrame
all_data = pd.concat(data_list, keys=range(1, 16), names=['Day'])

df = pd.DataFrame(all_data)
df

"""#**EDA**

Initial Data Inspection
"""

# Check the first few rows of the combined data
print(df.head())

"""Data Type Check"""

print(df.info())

print(df.describe())

"""check null values"""

# Check for missing values
print(df.isnull().sum())

"""check duplicates"""

# Check for duplicate rows
duplicates = df[df.duplicated()]

# Display the number of duplicate rows
print(f"Number of duplicate rows: {len(duplicates)}")

# Display the duplicate rows if any
print(duplicates.head())

"""drop duplicates"""

# Remove duplicate rows
df = df.drop_duplicates()

# Verify the removal
print(f"Number of rows after removing duplicates: {len(df)}")

"""apply featur engineering"""

#apply feature engineering (eucleadian distance on cell_x ,cell_y ,  cell_z )
# Calculate the Euclidean distance
df['euclidean_distance'] = np.sqrt(df['cell_x']**2 + df['cell_y']**2 + df['cell_z']**2)
df

"""Column Arrangement"""

# List of columns in the original order
cols = list(df.columns)

# Remove feature_11 and feature_12 from the current position
cols.remove('feature_11')
cols.remove('feature_12')

# Add feature_11 and feature_12 at the end
cols += ['feature_11', 'feature_12']

# Rearrange the DataFrame with the new column order
df = df[cols]

# Display the rearranged DataFrame
print(df.head())

# Check data types of each column
print(df.dtypes)

"""check the outliers"""

from itertools import count
Q1 = df.select_dtypes(include='float64').quantile(0.25)
Q3 = df.select_dtypes(include='float64').quantile(0.75)
IQR = Q3 - Q1
outliers = ((df.select_dtypes(include='float64') < (Q1 - 1.5 * IQR)) | (df.select_dtypes(include='float64') > (Q3 + 1.5 * IQR)))

"""#visualization

Box plot :  to visualize the outliers
"""

plt.figure(figsize=(15, 10))
sns.boxplot(data=df.select_dtypes(include='float64'))
plt.xticks(rotation=90)
plt.show()

"""Pair Plots: For visualizing relationships between multiple features"""

sns.pairplot(df.select_dtypes(include='float64'))
plt.show()

"""- identify the relationship between feature & target
- Calculate correlation coefficients between the features and (feature 11 ,feature 12)
"""

# Compute correlation matrix between feature and targets (feature 11 , feature 12)
corr_matrix = df.corr()

# Plot heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix[['feature_11', 'feature_12']], annot=True, cmap='coolwarm')
plt.title('Correlation Matrix with Target Features')
plt.show()

"""Scatter plots : to idetify the relationship between features and target"""

# Scatter plots
features = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5',
            'feature_6', 'feature_7', 'feature_8', 'feature_9', 'feature_10',
            'feature_13', 'feature_14', 'feature_15', 'feature_16', 'feature_17',
            'feature_18', 'feature_19' , 'euclidean_distance']

for feature in features:
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=df, x=feature, y='feature_11')
    plt.title(f'{feature} vs. feature_11')

    plt.subplot(1, 2, 2)
    sns.scatterplot(data=df, x=feature, y='feature_12')
    plt.title(f'{feature} vs. feature_12')

    plt.tight_layout()
    plt.show()

# feature importance
from sklearn.ensemble import RandomForestRegressor

# Prepare data for modeling
X = df[features]
y = df[['feature_11', 'feature_12']]

# Train model for feature importance
rf = RandomForestRegressor(n_estimators=100)
rf.fit(X, y['feature_11'])  # Example for feature_11

# Feature importance
importance = rf.feature_importances_
feature_importance = pd.DataFrame({'Feature': features, 'Importance': importance})
feature_importance = feature_importance.sort_values(by='Importance', ascending=False)

print(feature_importance)

"""check the distribution of data"""

#check the distribution of the data using histogram
df.hist(bins=50, figsize=(20,15))
plt.show()

"""#apply scalling (standarization)"""

#applying data standarization
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df[features] = scaler.fit_transform(df[features])
df

!pip install category_encoders

"""apply one hot encoding

"""

# Apply label encoding to 'feature_11'
df['feature_11'] = df['feature_11'].astype(int)

# Check the first 50 rows to confirm
print(df)

"""#split the data set"""

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df[features], df[['feature_11', 'feature_12']], test_size=0.2, random_state=42)

"""#modeling

Random forest tree
"""

# Create and train the Random Forest model
model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
model_rf.fit(X_train, y_train)

# Make predictions on the test set
y_pred_rf = model_rf.predict(X_test)

# Evaluate the model
mse_rf = mean_squared_error(y_test, y_pred_rf)
r2_rf = r2_score(y_test, y_pred_rf)

print("Random Forest Mean Squared Error:", mse_rf)
print("Random Forest R-squared:", r2_rf)

"""XGBoost"""

# Create and train the XGBoost model
model_xgb = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
model_xgb.fit(X_train, y_train)

# Make predictions on the test set
y_pred_xgb = model_xgb.predict(X_test)

# Evaluate the model
mse_xgb = mean_squared_error(y_test, y_pred_xgb)
r2_xgb = r2_score(y_test, y_pred_xgb)

print("XGBoost Mean Squared Error:", mse_xgb)
print("XGBoost R-squared:", r2_xgb)

"""K-Nearest Neighbors (KNN)"""

# Create and train the KNN model
model_knn = KNeighborsRegressor(n_neighbors=5)  # You can adjust the number of neighbors
model_knn.fit(X_train, y_train)

# Make predictions on the test set
y_pred_knn = model_knn.predict(X_test)

# Evaluate the model
mse_knn = mean_squared_error(y_test, y_pred_knn)
r2_knn = r2_score(y_test, y_pred_knn)

print("KNN Mean Squared Error:", mse_knn)
print("KNN R-squared:", r2_knn)

"""Multi-Layer Perceptron (MLP)"""

# Create and train the MLP model
model_mlp = MLPRegressor(hidden_layer_sizes=(100, 50), activation='relu', solver='adam', random_state=42)
model_mlp.fit(X_train, y_train)

# Make predictions on the test set
y_pred_mlp = model_mlp.predict(X_test)

# Evaluate the model
mse_mlp = mean_squared_error(y_test, y_pred_mlp)
r2_mlp = r2_score(y_test, y_pred_mlp)

print("MLP Mean Squared Error:", mse_mlp)
print("MLP R-squared:", r2_mlp)

"""Gated Recurrent Unit (GRU)"""

# Reshape the data for GRU
X_train_gru = np.reshape(X_train.values, (X_train.shape[0], 1, X_train.shape[1]))
X_test_gru = np.reshape(X_test.values, (X_test.shape[0], 1, X_test.shape[1]))

# Create the GRU model
model_gru = Sequential()
model_gru.add(GRU(units=50, input_shape=(X_train_gru.shape[1], X_train_gru.shape[2])))
model_gru.add(Dense(2))  # Output layer with 2 units for 'feature_11' and 'feature_12'

# Compile the model
model_gru.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model_gru.fit(X_train_gru, y_train, epochs=50, batch_size=32)

# Make predictions
y_pred_gru = model_gru.predict(X_test_gru)

# Evaluate the model
mse_gru = mean_squared_error(y_test, y_pred_gru)
r2_gru = r2_score(y_test, y_pred_gru)

print("GRU Mean Squared Error:", mse_gru)
print("GRU R-squared:", r2_gru)

"""apply CNN"""

# Reshape the data for CNN
X_train_cnn = np.reshape(X_train.values, (X_train.shape[0], X_train.shape[1], 1))
X_test_cnn = np.reshape(X_test.values, (X_test.shape[0], X_test.shape[1], 1))

# Create the CNN model
model_cnn = Sequential()
model_cnn.add(Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=(X_train_cnn.shape[1], 1)))
model_cnn.add(MaxPooling1D(pool_size=2))
model_cnn.add(Flatten())
model_cnn.add(Dense(50, activation='relu'))
model_cnn.add(Dense(2))  # Output layer with 2 units for 'feature_11' and 'feature_12'

# Compile the model
model_cnn.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model_cnn.fit(X_train_cnn, y_train, epochs=50, batch_size=32)

# Make predictions
y_pred_cnn = model_cnn.predict(X_test_cnn)

# Evaluate the model
mse_cnn = mean_squared_error(y_test, y_pred_cnn)
r2_cnn = r2_score(y_test, y_pred_cnn)

print("CNN Mean Squared Error:", mse_cnn)
print("CNN R-squared:", r2_cnn)

"""linear regression"""

#apply linear regression model to predict feature_11 and feature_12
# Create and train the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
accuracy = model.score(X_test, y_test)

print("Mean Squared Error:", mse)
print("R-squared:", r2)
print("accuracy:",accuracy)

"""#Performance Summary:
- Random Forest:
MSE: 4.83e-05
R-squared: 0.99948

- XGBoost:
MSE: 0.00069
R-squared: 0.99517

- KNN:
MSE: 153.40
R-squared: 0.96065

- MLP:
MSE: 5090.20
R-squared: -0.636

- GRU:
MSE: 992322.41
R-squared: -36.26

- CNN:
MSE: 10097.13
R-squared: -0.461

#Random Forest is Better in this proplem:
-  it gives Best Accuracy : it produced the lowest MSE and the highest R-squared value.
- Robustness: perform well even in complex datasets with noise or outliers.
- Interpretability: Although not as complex as XGBoost, Random Forest still provides strong performance with easier interpretability, especially with feature importance measures.

"""
