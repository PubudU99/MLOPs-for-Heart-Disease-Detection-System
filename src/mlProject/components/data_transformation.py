import os
import numpy as np
from mlProject import logger
from sklearn.model_selection import train_test_split
import pandas as pd
from mlProject.entity.config_entity import DataTransformationConfig
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.model_selection import train_test_split\


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    
    ## Note: You can add different data transformation techniques such as Scaler, PCA and all
    #You can perform all kinds of EDA in ML cycle here before passing this data to the model

    # I am only adding train_test_spliting cz this data is already cleaned up
    def splitting_encoding_and_mapping(self):

        numeric_columns = ['Age', 'RestingBP', 'Cholesterol','MaxHR', 'Oldpeak']
        features = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope']

        df = pd.read_csv(self.config.data_path)

        # Separate the features and target variable
        X = df.drop('HeartDisease', axis=1)
        y = df['HeartDisease']

        X_train, X_test, y_train, y_test = train_test_split(X,y,stratify=y, test_size=.2, random_state=42)
        
        logger.info("Splitting the data into training and testing sets(80% / 20%)")
        logger.info(X_train.shape)
        logger.info(X_test.shape)

        # For Feature Engineering
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


        # Feature Generation
        X_train['blood_pressure_group'] = X_train['RestingBP'].apply(categorize_blood_pressure)
        X_test['blood_pressure_group'] = X_test['RestingBP'].apply(categorize_blood_pressure)

        X_train['Cholestoral_group'] = X_train['Cholesterol'].apply(categorize_cholesterol)
        X_test['Cholestoral_group'] = X_test['Cholesterol'].apply(categorize_cholesterol)

        X_train['HR_Groups'] = X_train['MaxHR'].apply(Max_Heart_Rate)
        X_test['HR_Groups'] = X_test['MaxHR'].apply(Max_Heart_Rate)

        X_train['age_group'] = X_train['Age'].apply(assign_age_group)
        X_test['age_group'] = X_test['Age'].apply(assign_age_group)


        # One Hot Encoding
        Categorical_coulmns_with_multiple_uniques = ['ChestPainType','RestingECG','ST_Slope']
        OneHotEncoding = OneHotEncoder(sparse_output=False, drop='first')
        Encoded_df_TR = pd.DataFrame(OneHotEncoding.fit_transform(X_train[Categorical_coulmns_with_multiple_uniques]), columns = OneHotEncoding.get_feature_names_out())
        Encoded_df_TE = pd.DataFrame(OneHotEncoding.transform(X_test[Categorical_coulmns_with_multiple_uniques]), columns = OneHotEncoding.get_feature_names_out())

        # Mapping the categorical columns
        # Training Data
        Mapped_df_TR = pd.DataFrame()
        Mapped_df_TR['FastingBS'] = X_train['FastingBS']
        Mapped_df_TR['age_group'] = X_train['age_group'].map({"Young": 0, "Middle-aged": 1, "Elderly": 2, "Very Elderly":3})
        Mapped_df_TR['Cholestoral_group'] = X_train['Cholestoral_group'].map({"Desirable": 0, "High Cholesterol": 1, "Excessive Cholestrol": 2})
        Mapped_df_TR['HR_Groups'] = X_train['HR_Groups'].map({"Normal": 0, "High MaxHR": 1, "Excessive MaxHR": 2})
        Mapped_df_TR['blood_pressure_group'] = X_train['blood_pressure_group'].map({"Low": 0, "Normal": 1, "High": 2})
        Mapped_df_TR['Sex'] = X_train['Sex'].map({'M': 1, 'F': 0})
        Mapped_df_TR['ExerciseAngina'] = X_train['ExerciseAngina'].map({'N': 0, 'Y': 1})


        # Test Data
        Mapped_df_TE = pd.DataFrame()
        Mapped_df_TE['FastingBS'] = X_test['FastingBS']
        Mapped_df_TE['age_group'] = X_test['age_group'].map({"Young": 0, "Middle-aged": 1, "Elderly": 2, "Very Elderly":3})
        Mapped_df_TE['Cholestoral_group'] = X_test['Cholestoral_group'].map({"Desirable": 0, "High Cholesterol": 1, "Excessive Cholestrol": 2})
        Mapped_df_TE['HR_Groups'] = X_test['HR_Groups'].map({"Normal": 0, "High MaxHR": 1, "Excessive MaxHR": 2})
        Mapped_df_TE['blood_pressure_group'] = X_test['blood_pressure_group'].map({"Low": 0, "Normal": 1, "High": 2})
        Mapped_df_TE['Sex'] = X_test['Sex'].map({'M': 1, 'F': 0})
        Mapped_df_TE['ExerciseAngina'] = X_test['ExerciseAngina'].map({'N': 0, 'Y': 1})

        # Scaling the numeric columns using MinMaxScaler
        # Training Data
        numeric_columns = ['Age', 'RestingBP', 'Cholesterol','MaxHR', 'Oldpeak']
        numeric_df_TR = X_train[numeric_columns]
        scaler = MinMaxScaler()
        scaled_df_TR = pd.DataFrame(scaler.fit_transform(numeric_df_TR), columns=numeric_columns)

        # Test Data
        numeric_df_TE = X_test[numeric_columns]
        scaled_df_TE = pd.DataFrame(scaler.transform(numeric_df_TE), columns=numeric_columns)

        # Resetting the index of the  Training dataframes
        scaled_df_TR = scaled_df_TR.reset_index(drop=True)
        Encoded_df_TR = Encoded_df_TR.reset_index(drop=True)
        Mapped_df_TR = Mapped_df_TR.reset_index(drop=True)

        # Resetting the index of the Test dataframes
        scaled_df_TE = scaled_df_TE.reset_index(drop=True)
        Mapped_df_TE = Mapped_df_TE.reset_index(drop=True)
        Encoded_df_TE = Encoded_df_TE.reset_index(drop=True)
        y_train = y_train.reset_index(drop=True)
        y_test = y_test.reset_index(drop=True)
        # y_train = np.ravel(y_train)
        # y_test = np.ravel(y_test)
        # Concatenating the traing dataframes
        final_df_TR = pd.concat([scaled_df_TR, Encoded_df_TR, Mapped_df_TR], axis=1)

        # Concatenating the test dataframes
        final_df_TE = pd.concat([scaled_df_TE, Encoded_df_TE, Mapped_df_TE], axis=1)

        # print(final_df_TE.describe())
        train = pd.concat([final_df_TR, y_train], axis=1)

        # Combine the test data
        test = pd.concat([final_df_TE, y_test], axis=1)
        
        logger.info(f"Saved on the directory {self.config.root_dir}")
        
        train.to_csv(os.path.join(self.config.root_dir, "train.csv"),index = False)
        test.to_csv(os.path.join(self.config.root_dir, "test.csv"),index = False)

