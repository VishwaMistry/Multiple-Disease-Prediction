import numpy as np
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import re
import matplotlib.pyplot as plt

# Load the saved models
diabetes_model = pickle.load(open('C:/Users/Vishwa/DAIICT/DAIICT/saved models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open('C:/Users/Vishwa/DAIICT/DAIICT/saved models/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open('C:/Users/Vishwa/DAIICT/DAIICT/saved models/parkinsons_model.sav', 'rb'))


def create_table():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()


def add_user(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()


def login_user(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def password_check(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search("[a-z]", password):
        return "Password must contain a lowercase letter"
    if not re.search("[A-Z]", password):
        return "Password must contain an uppercase letter"
    if not re.search("[0-9]", password):
        return "Password must contain a digit"
    return None


def explain_risk_factors(model, input_data, feature_names):
    coef = model.coef_[0]
    contributions = coef * input_data[0]

    # Show breakdown of each feature's contribution
    st.subheader("Risk Factor Breakdown")
    for i, feature in enumerate(feature_names):
        st.write(f"{feature}: Contribution to Risk = {contributions[i]:.2f}")

    st.subheader("Personalized Health Tips")
    max_contributing_factor = feature_names[np.argmax(contributions)]
    if max_contributing_factor == "BMI":
        st.write("Consider maintaining a healthy BMI through diet and exercise.")
    elif max_contributing_factor == "Glucose":
        st.write("Monitor your blood sugar levels and consider a diet low in sugar.")
    elif max_contributing_factor == "Blood Pressure":
        st.write("Work on managing stress, reducing salt intake, and staying active to keep your blood pressure in check.")
    else:
        st.write(f"Focus on managing your {max_contributing_factor} to lower your risk.")


def plot_input_data(input_data, feature_names):
    plt.figure(figsize=(10, 6))
    plt.barh(feature_names, input_data[0], color='skyblue')
    plt.xlabel("Input Value")
    plt.ylabel("Features")
    plt.title("Feature Input Data Visualization")
    st.pyplot(plt)


def main():
    create_table()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    with st.sidebar:
        option = option_menu('Login/Signup', ['Login', 'Sign Up'], icons=['box-arrow-in-right', 'person-plus'],
                             menu_icon='key', default_index=0)

        if option == 'Sign Up':
            st.subheader('Create a new account')
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            confirm_password = st.text_input('Confirm Password', type='password')

            if st.button('Sign Up'):
                if password == confirm_password:
                    password_error = password_check(password)
                    if password_error:
                        st.warning(password_error)
                    else:
                        add_user(username, password)
                        st.success('Account created successfully!')
                else:
                    st.warning('Passwords do not match')

        elif option == 'Login':
            st.subheader('Login to your account')
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')

            if st.button('Login'):
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.success('Logged in successfully!')
                else:
                    st.warning('Incorrect username or password')

    if st.session_state.logged_in:
        selected = option_menu("Disease Prediction",
                               ['Diabetes Prediction', 'Heart Disease Prediction', "Parkinson's Prediction"],
                               icons=['activity', 'heart', 'person'], menu_icon="cast", default_index=0,
                               orientation="horizontal")

        # Diabetes Prediction
        if selected == 'Diabetes Prediction':
            st.title('Diabetes Prediction')
            col1, col2, col3 = st.columns(3)
            with col1:
                Pregnancies = st.number_input('Number of Pregnancies', min_value=0)
            with col2:
                Glucose = st.number_input('Glucose Level', min_value=0)
            with col3:
                BloodPressure = st.number_input('Blood Pressure value', min_value=0)
            with col1:
                SkinThickness = st.number_input('Skin Thickness value', min_value=0)
            with col2:
                Insulin = st.number_input('Insulin Level', min_value=0)
            with col3:
                BMI = st.number_input('BMI value', min_value=0.0)
            with col1:
                DiabetesPedigreeFunction = st.number_input('Diabetes Pedigree Function value', min_value=0.0)
            with col2:
                Age = st.number_input('Age of the Person', min_value=0)

            if st.button('Diabetes Test Result'):
                input_data = np.array([[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                                        BMI, DiabetesPedigreeFunction, Age]])

                # Prediction
                diab_prediction = diabetes_model.predict(input_data)

                if diab_prediction[0] == 1:
                    st.success(f'The person is diabetic')
                else:
                    st.markdown("<h5 style='color:red;'>The person is not diabetic</h5>", unsafe_allow_html=True)

                feature_names = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin',
                                 'BMI', 'DiabetesPedigreeFunction', 'Age']
                explain_risk_factors(diabetes_model, input_data, feature_names)

                plot_input_data(input_data, feature_names)

        # Heart Disease Prediction
        elif selected == 'Heart Disease Prediction':
            st.title('Heart Disease Prediction')
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.number_input('Age', min_value=0)
            with col2:
                sex = st.selectbox('Sex (1 = male; 0 = female)', [0, 1])
            with col3:
                cp = st.selectbox('Chest Pain types', [0, 1, 2, 3])
            with col1:
                trestbps = st.number_input('Resting Blood Pressure', min_value=0)
            with col2:
                chol = st.number_input('Serum Cholesterol in mg/dl', min_value=0)
            with col3:
                fbs = st.selectbox('Fasting Blood Sugar > 120 mg/dl (1 = true; 0 = false)', [0, 1])
            with col1:
                restecg = st.selectbox('Resting Electrocardiographic results', [0, 1, 2])
            with col2:
                thalach = st.number_input('Maximum Heart Rate achieved', min_value=0)
            with col3:
                exang = st.selectbox('Exercise Induced Angina (1 = yes; 0 = no)', [0, 1])
            with col1:
                oldpeak = st.number_input('ST depression induced by exercise', min_value=0.0)
            with col2:
                slope = st.selectbox('Slope of the peak exercise ST segment', [0, 1, 2])
            with col3:
                ca = st.selectbox('Major vessels colored by flourosopy', [0, 1, 2, 3])
            with col1:
                thal = st.selectbox('Thalassemia', [0, 1, 2, 3])

            if st.button("Heart Disease Test Result"):
                input_data = np.array(
                    [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]])

                # Prediction
                heart_prediction = heart_disease_model.predict(input_data)

                if heart_prediction[0] == 1:
                    st.success(f'The person has heart disease')
                else:
                    st.markdown("<h5 style='color:red;'>The person does not have heart disease</h5>", unsafe_allow_html=True)

                feature_names = ['Age', 'Sex', 'Chest Pain', 'Resting BP', 'Cholesterol', 'Fasting Blood Sugar',
                                 'Resting ECG', 'Max Heart Rate', 'Exercise Angina', 'ST Depression', 'Slope',
                                 'Major Vessels', 'Thalassemia']
                explain_risk_factors(heart_disease_model, input_data, feature_names)

                plot_input_data(input_data, feature_names)

        # Parkinson's Disease Prediction
        elif selected == "Parkinson's Prediction":
            st.title("Parkinson's Disease Prediction")
            col1, col2, col3 = st.columns(3)
            with col1:
                fo = st.number_input("MDVP:Fo(Hz)", min_value=0.0)
            with col2:
                fhi = st.number_input("MDVP:Fhi(Hz)", min_value=0.0)
            with col3:
                flo = st.number_input("MDVP:Flo(Hz)", min_value=0.0)
            with col1:
                Jitter_percent = st.number_input("MDVP:Jitter(%)", min_value=0.0)
            with col2:
                Jitter_Abs = st.number_input("MDVP:Jitter(Abs)", min_value=0.0)
            with col3:
                RAP = st.number_input("MDVP:RAP", min_value=0.0)
            with col1:
                PPQ = st.number_input("MDVP:PPQ", min_value=0.0)
            with col2:
                DDP = st.number_input("Jitter:DDP", min_value=0.0)
            with col3:
                Shimmer = st.number_input("MDVP:Shimmer", min_value=0.0)

            if st.button("Parkinson's Test Result"):
                input_data = np.array([[fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP, Shimmer]])

                # Prediction
                parkinsons_prediction = parkinsons_model.predict(input_data)

                if parkinsons_prediction[0] == 1:
                    st.success(f'The person has Parkinson\'s disease')
                else:
                    st.markdown("<h5 style='color:red;'>The person does not have Parkinson\'s disease</h5>", unsafe_allow_html=True)

                feature_names = ['Fo(Hz)', 'Fhi(Hz)', 'Flo(Hz)', 'Jitter(%)', 'Jitter(Abs)', 'RAP', 'PPQ', 'DDP', 'Shimmer']
                explain_risk_factors(parkinsons_model, input_data, feature_names)

                plot_input_data(input_data, feature_names)


if __name__ == '__main__':
    main()
