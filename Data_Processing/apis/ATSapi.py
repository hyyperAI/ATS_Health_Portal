from flask import Flask, jsonify,request, render_template, redirect 
import pandas as pd
from flask_cors import CORS
import json

#   ----------------------- READ DATA FILES --------------
# patient_list=pd.read_csv("../csv/hospital.patients.csv")
user_details=pd.read_csv("../csv/user_data.csv")
# # 10000115
# # #  Care unit preprocessor
# care_units=pd.read_csv("csv/care_unit.csv")
# care_units["date"]=pd.to_datetime(care_units["start_time"]).dt.date
# care_units["time"]=pd.to_datetime(care_units["start_time"]).dt.time
# care_units["date"]=care_units["date"].astype(str)
# care_units["time"]=care_units["time"].astype(str)
# care_units["date"]


# # #  ICU patient details preprocessor
# icu_pat_detail=pd.read_csv("csv/ml_dataset_icu.csv")
# icu_pat_detail["average_los"]=icu_pat_detail["average_los"].round(3)
# icu_pat_detail["date"]=pd.to_datetime(icu_pat_detail["shift_start_time"]).dt.date
# icu_pat_detail["time"]=pd.to_datetime(icu_pat_detail["shift_start_time"]).dt.time
# icu_pat_detail["date"]=icu_pat_detail["date"].astype(str)
# icu_pat_detail["time"]=icu_pat_detail["time"].astype(str)
# icu_pat_detail["shift_type"]


# #  graphs preprocessor
# daily_aggregate=pd.read_csv("csv/Daily_Agreagates_Trend.csv")
# daily_aggregate["average_los"]=daily_aggregate["average_los"].round(3)
# daily_aggregate["date"]=pd.to_datetime(daily_aggregate["shift_date"]).dt.date
# daily_aggregate["date"]=daily_aggregate["date"].astype(str)

# patient_journey=pd.read_csv("../csv/hospital.transfers.csv")
# x=pd.to_datetime(patient_journey["updated_intime"])
# patient_journey["date"]=x.dt.date
# patient_journey["time"]=x.dt.time
# patient_journey['date'] = patient_journey['date'].astype(str)

# diagnoses_=pd.read_csv("../csv/hospital.patients.diagnoses.csv")

# patient intake prediction
import pickle
filename = 'pi_xgboost.pkl'
model_intake = pickle.load(open('pi_xgboost.pkl',"rb"))

model_los=pickle.load(open("los_xgboost.pkl",'rb'))


#  ------------------- REQUIRED COLUMN PER CSV FILE --------------------------

patient_journey_col=["eventtype","careunit","date","time","updated_intime"]
pat_cu_cycle=["first_careunit","last_careunit","updated_intime","los","subject_id"]
patient_columns=["gender","anchor_age","dod_updated","start_year","subject_id"]
care_unit_list=["Trauma SICU (TSICU)","Cardiac Vascular Intensive Care Unit (CVICU)","Coronary Care Unit (CCU)","Medical Intensive Care Unit (MICU)",
                "Medical/Surgical Intensive Care Unit (MICU/SICU)","Surgical Intensive Care Unit (SICU)","Neuro Surgical Intensive Care Unit (Neuro SICU)",
                "Neuro Stepdown","Neuro Intermediate","start_time"]
icu_patient_col=["average_los","patient_intake_count","patient_out_count","total_icu_patients"]
diagnoses_table=["subject_id","seq_num","icd_code","long_title"]



# --------------------------------- INITIALIZE FLASK APP ----------------------
app=Flask(__name__)
CORS(app, origins="*")




# ------------------------  Enable CORS so that request from html can be accepted -----------------------------

def past_future_date(date_str):
    """ to return 6-PAST and 6-FUTURE values via present date with 4H gap in between"""
    date_time_list=[]
    for item in pd.date_range(pd.Timestamp(date_str) - pd.Timedelta(hours=24),freq='4H',periods=6):
        x=item.strftime("%Y/%m/%d %H:%M:%S")
        date_time_list.append(x)
    for item in pd.date_range(pd.Timestamp(date_str),freq='4H',periods=6):
        x=item.strftime("%Y/%m/%d %H:%M:%S")
        date_time_list.append(x)    
    return date_time_list


@app.after_request
def add_cors_headers(response):
    """ pre-requistic of flask """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response
        
    
#  ----------------------------------- APIS CREATION -------------------------------

@app.route("/patient/",methods=["POST","GET"])
def pat_det():
    """ Api , Routte function for patient details """
    if request.method=="GET":
        id=request.args.get("sub_id")
        filtered_data = patient_list[patient_list["subject_id"] == int(id)][patient_columns].to_json(orient='records')
        data_structure = json.loads(filtered_data)
        return jsonify(data_structure)
    else:
        return "Error in Arguments"


@app.route('/care_unit/',methods=["POST","GET"])
def care_unit_():
    """ Api , Route function for careunit details """
    if request.args.get("shift_time"):
        if request.method=="GET":
            shift_date=request.args.get("shift_date")
            shift_start_timing=request.args.get("shift_time")
            filtered_data = care_units[(care_units["date"] ==str(shift_date)) &( care_units["time"]==shift_start_timing)][care_unit_list]
            
            json_data = filtered_data.to_json(orient='records')
            data_structure = json.loads(json_data)
            return jsonify(data_structure)
    else:
        return "Error in Arguments"


        
@app.route("/icu_detail/",methods=["POST","GET"])
def icu_det():
    """ Give ICU  details about  {Average_los,patient_INTAKE, discharge , Total_patient }"""

    if request.args.get("shift_id"):
        if request.method=="GET":
            id=request.args.get("shift_id")
            shift_time=request.args.get("shift_time")

            filtered_data = icu_pat_detail[(icu_pat_detail["date"] ==str(id)) &( icu_pat_detail["time"]==shift_time)][icu_patient_col].to_json(orient='records')
            data_structure = json.loads(filtered_data)
            return jsonify(data_structure)
    else:
        return "Error in Arguments"
    
    
@app.route("/pat_journey/",methods=["POST","GET"])
def pat_journey():

    if request.args.get("sub_id"):
        if request.method=="GET":
            id=request.args.get("sub_id")
            filtered_data =patient_journey[patient_journey["subject_id"]==int(id)][patient_journey_col].sort_values(by="date").to_json(orient='records')
            data_structure = json.loads(filtered_data)
            return jsonify(data_structure)
    else:
        return "Error in Arguments"
    

   
@app.route("/pat_diagnoses/",methods=["POST","GET"])
def pat_diagnoses():
    """ detail of patient diagnoses is returned """
    if request.args.get("sub_id"):
        if request.method=="GET":
            id=request.args.get("sub_id")
            filtered_data =diagnoses_[diagnoses_["subject_id"]==int(id)][diagnoses_table].sort_values(by="seq_num").to_json(orient='records')
            data_structure = json.loads(filtered_data)
            return jsonify(data_structure)
    else:
        return "Error in Arguments"

# prediction of patient intake
 
@app.route("/prediction/", methods=["POST", "GET"])
def intake_pred():
    """ Prediction for 2 week before and after particular date """
    if request.method == "GET":
        date_str = request.args.get("date")

        patient_los_result=[]
        patient_intake_result = []
        date_time_list = past_future_date(date_str)
    
        for single_date in date_time_list:
            date = pd.to_datetime(single_date)
    
            morning, day, night = 0, 0, 0
            year, month, day, hour = date.year, date.month, date.day, date.hour
    
            if 0 <= hour < 8:
                morning = 1
            elif 8 <= hour < 16:
                day = 1
            elif 16 <= hour < 24:
                night = 1
            else:
                pass
            
            X_test = [year, month, day, hour, morning, day, night]
            patient_intake = model_intake.predict([X_test])
            patient_los = model_los.predict([X_test])
      
            if patient_intake:
                patient_intake_result.append((round(patient_intake[0])))
                patient_los_result.append(str(round(patient_los[0],3)))
             
    
        prediction_intake_result_dict = {"patient_intake":dict(enumerate(patient_intake_result)) }
        patient_los_result_dict ={"patient_los": dict(enumerate(patient_los_result)) }
        
        final_dict=[prediction_intake_result_dict , patient_los_result_dict]
        response=jsonify(final_dict)
        return response

 
@app.route("/single_prediction/", methods=["POST", "GET"])
def single_intake_pred():
    """ return single prediction for date and shift of a particular date and time """
    if request.method == "GET":
        date_str = request.args.get("date")
        date = pd.to_datetime(date_str)
        morning, day, night = 0, 0, 0
        year, month, day, hour = date.year, date.month, date.day, date.hour
        if 0 <= hour < 8:
            morning = 1
        elif 8 <= hour < 16:
            day = 1
        elif 16 <= hour < 24:
            night = 1
        else:
            pass
        X_test = [year, month, day, hour, morning, day, night]
        result_int = model_intake.predict([X_test])
        result_los=model_los.predict([X_test])
        final_pat_int=str(int(round(result_int[0])))
        final_pat_los=str(round(result_los[0],3))
        final={"intake":final_pat_int,"los":final_pat_los}
    return final

@app.route("/daily_agg2/", methods=["POST", "GET"])
def daily_agg2():

    if request.args.get("year"):
        if request.method == "GET":
            month = request.args.get("month")
            
            year = request.args.get("year")
            past_year=int(year)-1
            metric = request.args.get("metric")
            daily_aggregate["month"]=pd.to_datetime(daily_aggregate["shift_date"]).dt.month
            daily_aggregate["year"]=pd.to_datetime(daily_aggregate["shift_date"]).dt.year
        
            present_year_data = daily_aggregate[metric][(daily_aggregate["year"].astype(str) == year) & (daily_aggregate["month"].astype(str) == month)].to_list()
            past_year_data = daily_aggregate[metric][(daily_aggregate["year"].astype(str) == str(past_year)) & (daily_aggregate["month"].astype(str) == month)].to_list()

            filtered_data = {"past_values": past_year_data, "present_values": present_year_data}
            return jsonify(filtered_data)
    else:
        return "Error in Arguments"


# predict result with date time

@app.route("/prediction2/", methods=["POST", "GET"])
def intake_pred2():
    """ Prediction about dasy before and after """
    if request.method == "GET":
        date_str = request.args.get("date")

        patient_los_result=[]
        patient_intake_result = []
        date_time_list = past_future_date(date_str)
    
        for single_date in date_time_list:
            date = pd.to_datetime(single_date)
    
            morning, day, night = 0, 0, 0
            year, month, day, hour = date.year, date.month, date.day, date.hour
    
            if 0 <= hour < 8:
                morning = 1
            elif 8 <= hour < 16:
                day = 1
            elif 16 <= hour < 24:
                night = 1
            else:
                pass
            
            X_test = [year, month, day, hour, morning, day, night]
            # Assuming 'model_intake' is your trained machine learning model_intake
            patient_intake = model_intake.predict([X_test])
            patient_los = model_los.predict([X_test])
            if patient_intake:
                patient_intake_result.append((round(patient_intake[0])))
                patient_los_result.append(str(round(patient_los[0],3)))
        prediction_intake_result_dict = {"patient_intake":dict(zip(date_time_list, patient_intake_result)) }
        patient_los_result_dict ={"patient_los": dict(zip(date_time_list,patient_los_result)) }
        
        final_dict=[prediction_intake_result_dict , patient_los_result_dict]
        x=jsonify(final_dict)
        response = {
        "predictions": [prediction_intake_result_dict, patient_los_result_dict]
        }   
        return x
    

@app.route("/pages/signin", methods=["GET", "POST"])
def signin():
    """ sing_in and authentication function """
    if request.method == "GET":
        return render_template("pages/signin.html")

    elif request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        matching_row = user_details[(user_details['email'] == email)| (user_details['password'] == password)]

        if not matching_row.empty:
            return redirect("http://127.0.0.1:8000/index.html")

        else:
           return "ERROR"

        


@app.route("/pages/sign_up",methods=["GET","POST"])
def sign_up():
    """ signup and save the user_date in csv """
    if request.method=="GET":
            return render_template("pages/sign_up.html")
    elif request.method=="POST":
        first_name=request.form["first_name"]
        last_name=request.form["last_name"]
        email = request.form['email']
        password = request.form['password']
        add_dict={
            "first_name":first_name,
            "last_name":last_name,
            "email":email,
            "password":password,
        }
        new_index = len(user_details)
        user_details.loc[new_index] = add_dict
        user_details.to_csv("../csv/user_data.csv",sep=",")
        return render_template("pages/signin.html")


    


#  ----------------------    PATH FOR TEMPLATES ---------------------


@app.route("/")
def home():
    """ DEFAULT """
    return render_template("pages/signin.html")



@app.route("/index.html")
def index():
    """ home page  """
    return render_template("index.html")

@app.route("/components/dashboard_icu.html")
def dashboard_icu():
    """ dashboard of icu portal """
    return render_template("components/dashboard_icu.html")

@app.route("/components/datatable.html")
def datatable():
    """ Patient diagnoses sequence table """
    return render_template("components/datatable.html")

@app.route("/components/open_mail.html")
def open_mail():
    """ template row of email page """
    return render_template("open_mail.html")

@app.route("/components/bot.html")
def bot():
    """ responsible for bot.html cause this is passed through here """
    return render_template("components/bot.html")

@app.route("/components/patientjourney.html")
def patient_journeys():
    """ responsible for patiend_journeys template """
    return render_template("components/patientjourney.html")

@app.route("/components/prediction.html")
def prediction():
    """ responsible for patient prediction template """
    return render_template("components/prediction.html")


@app.route("/pages/notifications.html")
def notifications():
    return render_template("pages/notifications.html")

@app.route("/pages/profile.html")
def profile():
    return render_template("pages/profile.html")

@app.route("/components/email.html")
def email():
    return render_template("components/email.html")
# s



if __name__=="__main__":
    app.run(host="127.0.0.1", port=8000,debug=True)
        
        
        
        