from flask import Flask, render_template, request
import os 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from mlProject.pipeline.prediction import PredictionPipeline

# Feature Engineering
def categorize_blood_pressure(RestingBP):
    if RestingBP < 90:
        return "Low"
    elif 90 <= RestingBP <= 120:
        return "Normal"
    else:
        return "High"
    
def categorize_cholesterol(Cholesterol):
    if Cholesterol < 195:
        return "Desirable"
    elif 195 <= Cholesterol <= 240:
        return "High Cholesterol"
    else:
        return "Excessive Cholestrol"

def Max_Heart_Rate(MaxHR):
    if 60 <MaxHR < 100:
        return "Normal"
    elif 100 <= MaxHR <= 200:
        return "High MaxHR"
    else:
        return "Excessive MaxHR"

def assign_age_group(age):

    age_groups = {
    (0, 40): 'Young',
    (41, 60): 'Middle-aged',
    (61, 80): 'Elderly',
    (81, float('inf')): 'Very Elderly'
    }

    for age_range, group in age_groups.items():
        if age_range[0] <= age <= age_range[1]:
            return group
app = Flask(__name__) # initializing a flask app
def heart_prediction_scratch(age, sex, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope):
    numeric_columns = ['Age', 'RestingBP', 'Cholesterol','MaxHR', 'Oldpeak']
    features = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope']
    
    df = pd.read_csv('source/data_set.csv')
    # Create a DataFrame with the user inputs
    input_row = pd.DataFrame([[age, sex, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope]], columns=features)
    
    # Append the input row to the input_data DataFrame
    df = df._append(input_row, ignore_index=True)
    
    df['blood_pressure_group'] = df['RestingBP'].apply(categorize_blood_pressure)
        
    df['Cholestoral_group'] = df['Cholesterol'].apply(categorize_cholesterol)
        
    df['HR_Groups'] = df['MaxHR'].apply(Max_Heart_Rate)

    df['age_group'] = df['Age'].apply(assign_age_group)

    # One Hot Encoding
    Categorical_coulmns_with_multiple_uniques = ['ChestPainType','RestingECG','ST_Slope']
    OneHotEncoding = OneHotEncoder(sparse_output=False, drop='first')
    Encoded_df = pd.DataFrame(OneHotEncoding.fit_transform(df[Categorical_coulmns_with_multiple_uniques]), columns = OneHotEncoding.get_feature_names_out())

    # Mapping the categorical columns
    df_Mapped = pd.DataFrame()
    df_Mapped['FastingBS'] = df['FastingBS']
    df_Mapped['age_group'] = df['age_group'].map({"Young": 0, "Middle-aged": 1, "Elderly": 2, "Very Elderly":3})
    df_Mapped['Cholestoral_group'] = df['Cholestoral_group'].map({"Desirable": 0, "High Cholesterol": 1, "Excessive Cholestrol": 2})
    df_Mapped['HR_Groups'] = df['HR_Groups'].map({"Normal": 0, "High MaxHR": 1, "Excessive MaxHR": 2})
    df_Mapped['blood_pressure_group'] = df['blood_pressure_group'].map({"Low": 0, "Normal": 1, "High": 2})
    df_Mapped['Sex'] = df['Sex'].map({'M': 1, 'F': 0})
    df_Mapped['ExerciseAngina'] = df['ExerciseAngina'].map({'N': 0, 'Y': 1})

    # Scaling the numeric columns
    numeric_columns = ['Age', 'RestingBP', 'Cholesterol','MaxHR', 'Oldpeak']
    df_numeric = df[numeric_columns]
    scaler = MinMaxScaler()
    scaled_df = pd.DataFrame(scaler.fit_transform(df_numeric), columns = scaler.get_feature_names_out())

    # Resetting the index of the dataframes
    scaled_df = scaled_df.reset_index(drop=True)
    Encoded_df = Encoded_df.reset_index(drop=True)
    df_Mapped = df_Mapped.reset_index(drop=True)

    # Concatenating the dataframes
    final_df = pd.concat([scaled_df, Encoded_df, scaled_df], axis=1)

    # Adding the target column
    final_df['HeartDisease'] = df['HeartDisease'].reset_index(drop=True)

    # Copy the last row to a new DataFrame
    input_data = final_df.iloc[[-1]].copy()

    # Drop the target column from the input data
    input_data = input_data.drop('HeartDisease', axis=1)

    # Remove the last row from the original DataFrame
    final_df = final_df.iloc[:-1]

    X_input = input_data


    # Load the model
    from joblib import load

    # Split the data into input and target
    from sklearn.model_selection import train_test_split\
        
    X = final_df.drop('HeartDisease', axis=1)
    y = final_df['HeartDisease']
    X_train, X_test, y_train, y_test = train_test_split(X,y,stratify=y, test_size=.3, random_state=42)

    # print(model)
    # Creating The Model Selector
    
    selected_model = LogisticRegression(C=0.2976351441631313, class_weight='balanced', l1_ratio=0.4,max_iter=2500, penalty='elasticnet', solver='saga',tol=0.01)
    
    # Training the Model
    selected_model.fit(X_train,y_train)

    y_pred = selected_model.predict(X_input)

    return int(y_pred[0])

@app.route('/',methods=['GET'])  # route to display the home page
def homePage():
    return render_template("index.html")


@app.route('/train',methods=['GET'])  # route to train the pipeline
def training():
    os.system("python main.py")
    return "Training Successful!" 


@app.route('/predict',methods=['POST','GET']) # route to show the predictions in a web UI
def index():
    if request.method == 'POST':
        try:
            #  reading the inputs given by the user
            age = int(request.form['age'])
            sex = request.form['sex']
            chest_pain_type = request.form['chest_pain_type']
            resting_bp = int(request.form['resting_bp'])
            cholesterol = int(request.form['cholesterol'])
            fasting_bs = request.form['fasting_bs']
            resting_ecg = request.form['resting_ecg']
            max_hr = int(request.form['max_hr'])
            exercise_angina = request.form['exercise_angina']
            oldpeak = float(request.form['oldpeak'])
            st_slope = request.form['st_slope']
       
            predict = heart_prediction_scratch(age, sex, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope)
            return render_template('results.html', prediction = str(predict))

        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'

    else:
        return render_template('index.html')



if __name__ == "__main__":
	# app.run(host="0.0.0.0", port = 8080, debug=True)
	app.run(host="0.0.0.0", port = 8083)