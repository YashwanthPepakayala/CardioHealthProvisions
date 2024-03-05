from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def append_to_excel(file_name, data):
    # If the file exists, read the existing data
    if os.path.isfile(file_name):
        existing_data = pd.read_excel(file_name)
        updated_data = pd.concat([existing_data, data], ignore_index=True)
    else:
        updated_data = data

    # Write the updated data to the Excel file
    updated_data.to_excel(file_name, index=False)


# Route to render the contact page
@app.route('/')
def default_route():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/prognosis')
def prognosis():
    return render_template('solutions.html')


@app.route('/diet')
def diet():
    return render_template('diet.html')


@app.route('/cardioguide')
def cardioguide():
    return render_template('case.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/privacypolicy')
def privacypolicy():
    return render_template('privecy.html')


@app.route('/terms')
def terms():
    return render_template('terms-condition.html')


@app.route('/exercise')
def exercise():
    return render_template('exercise.html')


# Route to handle form submission
@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        msg_subject = request.form['msg_subject']
        message = request.form['message']

        # Process the form data (You can add your logic here)

        data = {
            'Name': [name],
            'Email': [email],
            'Phone Number': [phone_number],
            'Subject': [msg_subject],
            'Message': [message]
        }

        df = pd.DataFrame(data)
        file_name = 'contact_form.xlsx'
        append_to_excel(file_name, df)

        print(f"Name: {name}, Email: {email}, Phone: {phone_number}, Subject: {msg_subject}, Message: {message}")

        return jsonify({'message': 'Form submitted successfully!'})

    except Exception as e:
        print(f"Error processing form data: {str(e)}")
        return jsonify({'error': 'Error processing form data'}), 500  # Return an error response



# model = joblib.load('models/heart_disease_model1.pkl')
model = joblib.load('models/rfr_model.pkl')
feature_importances = joblib.load('models/feature_importances1.pkl')



# Route to handle form submission
@app.route('/submit_prognosis_form', methods=['POST'])
def submit_prognosis_form():
    try:
        # Get form data from the 'prognosis' page in the frontend
        gender = request.form['gender']
        age = request.form['age']
        chestpain_type = request.form['chestpain_type']
        resting_bp = request.form['resting_bp']
        cholesterol = request.form['cholesterol']
        fasting_bs = request.form['fasting_bs']
        resting_ecg = request.form['resting_ecg']
        max_hr = request.form['max_hr']
        exerciseAngina = request.form['exerciseAngina']
        old_Peak = float(request.form['old_peak'])
        STslope = request.form['STslope']


        if int(resting_bp) <= 90:
            bp = "Blood Pressure is low. "
        elif int(resting_bp) >= 135:
            bp = "Blood Pressure is high. "
        else:
            bp = "Blood Pressure is stable. "

        if int(fasting_bs) >= 250:
            bs = "Fasting Blood Sugar is High. "
        elif int(fasting_bs) <= 70:
            bs = "Fasting Blood Sugar is low. "
        else:
            bs = "Fasting Blood Sugar is stable. "

        if int(cholesterol) >= 240:
            cho = "Cholesterol is High. "
        elif int(cholesterol) <= 120:
            cho = "Cholesterol is low. "
        else:
            cho = "Cholesterol is stable. "


        # Function to convert gender to 1 if Male and 0 if Female
        def convert_gender(gender):
            return 1 if gender.lower() == 'male' else 0

        def convert_fasting_bs(fasting_bs):
            return 1 if int(fasting_bs) > 120 else 0
        
        # Function to convert chestpain_type
        def convert_chestpain_type(chestpain_type):
            if chestpain_type == 'ATA':
                return 1
            elif chestpain_type == 'NAP':
                return 2
            elif chestpain_type == 'ASY':
                return 0
            elif chestpain_type == 'TA':
                return 3

        # Function to convert resting_ecg
        def convert_resting_ecg(resting_ecg):
            if resting_ecg == 'Normal':
                return 1
            elif resting_ecg == 'ST':
                return 2
            elif resting_ecg == 'LVH':
                return 0

        # Function to convert exerciseAngina to 1 if Yes and 0 if No
        def convert_exercise_angina(exercise_angina):
            return 1 if exercise_angina.lower() == 'yes' else 0

        # Function to convert STslope
        def convert_st_slope(st_slope):
            if st_slope.lower() == 'up':
                return 2
            elif st_slope.lower() == 'flat':
                return 1
            elif st_slope.lower() == 'down':
                return 0

        gender = convert_gender(gender)
        chestpain_type = convert_chestpain_type(chestpain_type)
        resting_ecg = convert_resting_ecg(resting_ecg)
        exerciseAngina = convert_exercise_angina(exerciseAngina)
        STslope = convert_st_slope(STslope)
        fasting_bs = convert_fasting_bs(fasting_bs)

        input_data = [gender, int(age), chestpain_type, int(resting_bp), int(cholesterol), fasting_bs, resting_ecg, int(max_hr), exerciseAngina, old_Peak, STslope]
        input_data = np.array(input_data).reshape(1, -1)
        input_df = pd.DataFrame(input_data, columns=['Age', 'Gender', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope'])

        
        # Make a prediction using the loaded model
        prediction = model.predict(input_df)

        # Calculate heart risk based on feature importances
        # risk_percentage = (input_data * feature_importances).sum()
        
        risk_percentage = prediction[0]*100
        risk_percentage = round(risk_percentage, 2)
        # Return the calculated heart risk and suggested foods as JSON
    
        return jsonify({
            'heart_risk_percentage': risk_percentage,
            'blood_pressure': bp,
            'blood_sugar': bs,
            'cholesterol': cho,
        })

    except Exception as e:
        print(f"Error processing form data: {str(e)}")
        return jsonify({'error': 'Error processing form data'}), 500  # Return an error response


if __name__ == '__main__':
    app.run(debug=True)
