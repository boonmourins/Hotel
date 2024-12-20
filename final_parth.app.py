import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


from google.colab import files

# Upload file from local machine
uploaded = files.upload()


# Load the dataset
file_path = "Hotel.csv"
  # Replace with your file path
df = pd.read_csv(file_path)

print(df.head())
print(df.info())

# Ensure 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Drop rows with invalid dates
df = df.dropna(subset=['Date'])
df= df.dropna(subset=['Booking Channel'])

# Aggregate booking volume by Date
booking_volume = df.groupby('Date').size().reset_index(name='Booking_Volume')

# Sort the data by Date
booking_volume = booking_volume.sort_values('Date')

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(booking_volume['Date'], booking_volume['Booking_Volume'])
plt.title('Booking Volume Over Time')
plt.xlabel('Date')
plt.ylabel('Volume')
plt.show()


# Create features and target variables for supervised learning
def create_features(data, lag=7):
    features, targets = [], []
    for i in range(lag, len(data)):
        features.append(data[i-lag:i])
        targets.append(data[i])
    return np.array(features), np.array(targets)

# Normalize the data
scaler = MinMaxScaler()
booking_volume['Normalized'] = scaler.fit_transform(booking_volume[['Booking_Volume']])

# Create lagged features
lag = 7  # Number of previous days to use
features, targets = create_features(booking_volume['Normalized'].values, lag)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.2, random_state=42)



# Reshape input to be [samples, time steps, features]
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Define the LSTM model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    LSTM(50, return_sequences=False),
    Dense(25),
    Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, batch_size=32, epochs=20, validation_data=(X_test, y_test))


# Make predictions
predictions = model.predict(X_test)

# Reverse normalization for interpretation
predicted_volume = scaler.inverse_transform(predictions)
actual_volume = scaler.inverse_transform(y_test.reshape(-1, 1))

# Plot predictions vs actual
plt.figure(figsize=(12, 6))
plt.plot(actual_volume, label='Actual Volume')
plt.plot(predicted_volume, label='Predicted Volume')
plt.title('Predicted vs Actual Booking Volume')
plt.xlabel('Time')
plt.ylabel('Booking Volume')
plt.legend()
plt.show()



import pickle

# Save the scaler
with open('scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

# Save the LSTM model
model.save('booking_volume_model.h5')


!pip install streamlit



import streamlit as st
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import pickle

# Load the model and scaler
model = load_model('booking_volume_model.h5')
with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

# Streamlit App Interface
st.title('Booking Volume Prediction')

st.write("Enter the last 7 days of booking volume:")

# Input boxes for the last 7 days of booking volume
day_1 = st.number_input('Day 1', min_value=0)
day_2 = st.number_input('Day 2', min_value=0)
day_3 = st.number_input('Day 3', min_value=0)
day_4 = st.number_input('Day 4', min_value=0)
day_5 = st.number_input('Day 5', min_value=0)
day_6 = st.number_input('Day 6', min_value=0)
day_7 = st.number_input('Day 7', min_value=0)

# Button to predict
if st.button('Predict'):
    # Prepare the input data
    input_data = np.array([day_1, day_2, day_3, day_4, day_5, day_6, day_7]).reshape(1, 7, 1)

    # Predict booking volume
    prediction = model.predict(input_data)

    # Reverse normalization
    predicted_volume = scaler.inverse_transform(prediction)

    # Display the result
    st.write(f"Predicted Booking Volume: {predicted_volume[0][0]}")


!streamlit run app.py

from tensorflow.keras.models import load_model
model.save('booking_volume_model.h5')

import pickle
with open('scaler.pkl', 'wb') as file:
 pickle.dump (scaler, file)


model = load_model('booking_volume_model.h5')
with open('scaler.pkl', 'rb') as file:
 scaler = pickle.load(file)

# Test data
input_data = np.array([[50, 60, 70, 80, 90, 100, 110]]).reshape(1, 7, 1)
prediction = model.predict(input_data)
predicted_volume = scaler.inverse_transform(prediction)
print(f"Predicted Booking Volume: {predicted_volume[0][0]}")

pip install streamlit

import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
import pickle

# Load the trained model and scaler
model = load_model('booking_volume_model.h5')
with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

# Streamlit app layout
st.title("Booking Volume Prediction App")
st.write("Predict the booking volume for a given time period.")

# Collect user inputs
st.header("Input Features")
inputs = []
for i in range(7):  # Assuming 7 days of data are required as input
    value = st.number_input(f"Enter bookings for day {i+1}", min_value=0, max_value=1000, step=1)
    inputs.append(value)

# Prediction button
if st.button("Predict"):
    # Preprocess inputs
    input_array = np.array(inputs).reshape(1, 7, 1)  # Reshape for LSTM model
    input_scaled = scaler.transform(input_array.reshape(-1, 1)).reshape(1, 7, 1)
    
# Predict and display
    prediction = model.predict(input_scaled)
    predicted_volume = scaler.inverse_transform(prediction)
    st.success(f"Predicted Booking Volume: {predicted_volume[0][0]:.2f}")

# Footer
st.write("Created with Streamlit and TensorFlow")

