from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Medical, User, Ment, Profile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
import numpy as np
import os
from django.contrib import messages
import joblib as joblib
from django.contrib.auth.hashers import make_password



def about(request):
	return render(request, 'about.html')


def doctor_list(request):
	return render(request, 'doctors.html')


def home(request):
	return render(request, 'home.html')


def registerView(request):
	return render(request, 'register.html')


def registerUser(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		password = make_password(password)

		a = User(username=username, email=email, password=password, is_patient=True)
		a.save()
		messages.success(request, 'Account Was Created Successfully')
		return redirect('reg')
	else:
		messages.error(request, 'Failed To Register, Try Again Later')
		return redirect('reg')


def loginView(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
			if user.is_patient:
				return redirect('patient')
			elif user.is_doctor:
				return redirect('doctor')
			else:
				return redirect('login')
		else:
			messages.info(request, "Invalid Username Or Password")
			return redirect('login')
	else:
		return render(request, 'login.html')					



def doctor_home(request):
	doctor = User.objects.filter(is_doctor=True).count()
	patient = User.objects.filter(is_patient=True).count()
	appointment = Ment.objects.filter(approved=True).count()
	medical1 = Medical.objects.filter(medicine='See Doctor').count()
	medical2 = Medical.objects.all().count()
	medical3 = int(medical2) - int(medical1)
	
	context = {'doctor':doctor, 'ment':appointment, patient:'patient', 'drug':medical3}
	return render(request, 'doctor/home.html', context)



def patient_home(request):
	doctor = User.objects.filter(is_doctor=True).count()
	patient = User.objects.filter(is_patient=True).count()
	appointment = Ment.objects.filter(approved=True).count()
	medical1 = Medical.objects.filter(medicine='See Doctor').count()
	medical2 = Medical.objects.all().count()
	medical3 = int(medical2) - int(medical1)

	user_id = request.user.id
	user_profile = Profile.objects.filter(user_id=user_id)
	if not user_profile:
		context = {'profile_status':'Please Create Profile To Continue', 'doctor':doctor, 'ment':appointment, patient:'patient', 'drug':medical3}
		return render(request, 'patient/home.html', context)
	else:
		context = {'status':'1', 'doctor':doctor, 'ment':appointment, patient:'patient', 'drug':medical3}
		return render(request, 'patient/home.html', context)



def create_profile(request):
	if request.method == 'POST':
		birth_date = request.POST['birth_date']
		region = request.POST['region']
		country = request.POST['country']
		gender = request.POST['gender']
		user_id = request.user.id

		Profile.objects.filter(id = user_id).create(user_id=user_id, birth_date=birth_date, gender=gender, region=region)
		messages.success(request, 'Your Profile Was Created Successfully')
		return redirect('patient')
	else:
		user_id = request.user.id
		users = Profile.objects.filter(user_id=user_id)
		users = {'users':users}
		choice = ['1','0']
		gender = ["Male", "Female"]
		context = {"users": {"users":users}, "choice":{"choice":choice}, "gender":gender}
		return render(request, 'patient/create_profile.html', context)	



def diagnosis(request):
	symptoms = ['itching','skin_rash','none','nodal_skin_eruptions','continuous_sneezing','shivering','chills','joint_pain','stomach_pain','acidity','ulcers_on_tongue','muscle_wasting','vomiting','burning_micturition','spotting_ urination','fatigue','weight_gain','anxiety','cold_hands_and_feets','mood_swings','weight_loss','restlessness','lethargy','patches_in_throat','irregular_sugar_level','cough','high_fever','sunken_eyes','breathlessness','sweating','dehydration','indigestion','headache','yellowish_skin','dark_urine','nausea','loss_of_appetite','pain_behind_the_eyes','back_pain','constipation','abdominal_pain','diarrhoea','mild_fever','yellow_urine','yellowing_of_eyes','acute_liver_failure','fluid_overload','swelling_of_stomach','swelled_lymph_nodes','malaise','blurred_and_distorted_vision','phlegm','throat_irritation','redness_of_eyes','sinus_pressure','runny_nose','congestion','chest_pain','weakness_in_limbs','fast_heart_rate','pain_during_bowel_movements','pain_in_anal_region','bloody_stool','irritation_in_anus','neck_pain','dizziness','cramps','bruising','obesity','swollen_legs','swollen_blood_vessels','puffy_face_and_eyes','enlarged_thyroid','brittle_nails','swollen_extremeties','excessive_hunger','extra_marital_contacts','drying_and_tingling_lips','slurred_speech','knee_pain','hip_joint_pain','muscle_weakness','stiff_neck','swelling_joints','movement_stiffness','spinning_movements','loss_of_balance','unsteadiness','weakness_of_one_body_side','loss_of_smell','bladder_discomfort','foul_smell_of urine','continuous_feel_of_urine','passage_of_gases','internal_itching','toxic_look_(typhos)','depression','irritability','muscle_pain','altered_sensorium','red_spots_over_body','belly_pain','abnormal_menstruation','dischromic _patches','watering_from_eyes','increased_appetite','polyuria','family_history','mucoid_sputum','rusty_sputum','lack_of_concentration','visual_disturbances','receiving_blood_transfusion','receiving_unsterile_injections','coma','stomach_bleeding','distention_of_abdomen','history_of_alcohol_consumption','fluid_overload','blood_in_sputum','prominent_veins_on_calf','palpitations','painful_walking','pus_filled_pimples','blackheads','scurring','skin_peeling','silver_like_dusting','small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose','yellow_crust_ooze']
	symptoms = sorted(symptoms)
	context = {'symptoms':symptoms, 'status':'1'}
	return render(request, 'patient/diagnosis.html', context)


@csrf_exempt
def MakePredict(request):
	s1 = request.POST.get('s1')
	s2 = request.POST.get('s2')
	s3 = request.POST.get('s3')
	s4 = request.POST.get('s4')
	s5 = request.POST.get('s5')
	id = request.POST.get('id')
	
	list_b = [s1,s2,s3,s4,s5]
	print(list_b)

	list_a = ['itching','skin_rash','nodal_skin_eruptions','continuous_sneezing','shivering','chills','joint_pain','stomach_pain','acidity','ulcers_on_tongue','muscle_wasting','vomiting','burning_micturition','spotting_ urination','fatigue','weight_gain','anxiety','cold_hands_and_feets','mood_swings','weight_loss','restlessness','lethargy','patches_in_throat','irregular_sugar_level','cough','high_fever','sunken_eyes','breathlessness','sweating','dehydration','indigestion','headache','yellowish_skin','dark_urine','nausea','loss_of_appetite','pain_behind_the_eyes','back_pain','constipation','abdominal_pain','diarrhoea','mild_fever','yellow_urine','yellowing_of_eyes','acute_liver_failure','fluid_overload','swelling_of_stomach','swelled_lymph_nodes','malaise','blurred_and_distorted_vision','phlegm','throat_irritation','redness_of_eyes','sinus_pressure','runny_nose','congestion','chest_pain','weakness_in_limbs','fast_heart_rate','pain_during_bowel_movements','pain_in_anal_region','bloody_stool','irritation_in_anus','neck_pain','dizziness','cramps','bruising','obesity','swollen_legs','swollen_blood_vessels','puffy_face_and_eyes','enlarged_thyroid','brittle_nails','swollen_extremeties','excessive_hunger','extra_marital_contacts','drying_and_tingling_lips','slurred_speech','knee_pain','hip_joint_pain','muscle_weakness','stiff_neck','swelling_joints','movement_stiffness','spinning_movements','loss_of_balance','unsteadiness','weakness_of_one_body_side','loss_of_smell','bladder_discomfort','foul_smell_of urine','continuous_feel_of_urine','passage_of_gases','internal_itching','toxic_look_(typhos)','depression','irritability','muscle_pain','altered_sensorium','red_spots_over_body','belly_pain','abnormal_menstruation','dischromic _patches','watering_from_eyes','increased_appetite','polyuria','family_history','mucoid_sputum','rusty_sputum','lack_of_concentration','visual_disturbances','receiving_blood_transfusion','receiving_unsterile_injections','coma','stomach_bleeding','distention_of_abdomen','history_of_alcohol_consumption','fluid_overload','blood_in_sputum','prominent_veins_on_calf','palpitations','painful_walking','pus_filled_pimples','blackheads','scurring','skin_peeling','silver_like_dusting','small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose','yellow_crust_ooze']

	# Loop to convert all symptoms into 0's
	list_c = [] # EMpty list to store disease symptoms converted into 0's and 1's
	for x in range(0,len(list_a)):
		list_c.append(0)

	print(list_c)


	# For all matched specific disease symptoms in general put 1 and unmatched put 0
	for z in range(0,len(list_a)):
		for k in list_b:
			if(k==list_a[z]):
				list_c[z]=1

	test = list_c
	test = np.array(test)
	test = np.array(test).reshape(1,-1)
	print(test.shape)

	clf = joblib.load('model/naive_bayes.pkl')

	prediction = clf.predict(test)
	result = prediction[0]
	# drug=predict_medicine(s1,s2,s3,s4,s5,result)
	drug=MakeMend(request,id,result)

	
	a = Medical(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, disease=result,medicine=drug[-1], patient_id=id)
	a.save()

	return JsonResponse({'status':result})			


def patient_result(request):
	user_id = request.user.id
	disease = Medical.objects.all().filter(patient_id=user_id)
	context = {'disease':disease, 'status':'1'}
	return render(request, 'patient/result.html', context)


@csrf_exempt
def MakeMent(request):
	disease = request.POST.get('disease')
	userid = request.POST.get('userid')

	try:
		check_medical = Ment.objects.filter(medical_id=disease).exists()
		if(check_medical == False):
			a = Ment(medical_id=disease, patient_id=userid)
			a.save()
			return JsonResponse({'status':'saved'})
		else:
			print('Appointment Exist')
			return JsonResponse({'status':'exist'})
	except Exception as e:
		return JsonResponse({'status':'error'})			


def patient_ment(request):
	user_id = request.user.id
	appointment = Ment.objects.all().filter(patient_id=user_id)
	context = {'ment':appointment, 'status':'1'}
	return render(request, 'patient/ment.html', context)



def logoutView(request):
	logout(request)
	return redirect('login')



def doctor_commend(request):
	user_id = request.user.id
	disease = Medical.objects.all()
	context = {'disease':disease}
	return render(request, 'doctor/result.html', context)



@login_required
@csrf_exempt
def MakeMend(request,id,disease):
	print(disease)
	x=disease
	disease_list = ['Acne','Allergy','Diabetes','Fungal infection','Urinary tract infection','Malaria','Migraine','Hepatitis B','AIDS']
	
	disease_dict ={'(vertigo) Paroymsal  Positional Vertigo': 0,
 'AIDS': 1,
 'Acne': 2,
 'Alcoholic hepatitis': 3,
 'Allergy': 4,
 'Arthritis': 5,
 'Bronchial Asthma': 6,
 'Cervical spondylosis': 7,
 'Chicken pox': 8,
 'Chronic cholestasis': 9,
 'Comman Cold': 10,
 'Dengue': 11,
 'Diabetes': 12,
 'Fungal infection': 13,
 'GERD': 14,
 'Gastroenteritis': 15,
 'Heart attack': 16,
 'Hepatitis B': 17,
 'Hypertension': 18,
 'Hyperthyroidism': 19,
 'Hypoglycemia': 20,
 'Hypothyroidism': 21,
 'Impetigo': 22,
 'Jaundice': 23,
 'Malaria': 24,
 'Migraine': 25,
 'Osteoarthristis': 26,
 'Paralysis (brain hemorrhage)': 27,
 'Peptic ulcer diseae': 28,
 'Pneumonia': 29,
 'Psoriasis': 30,
 'Tuberculosis': 31,
 'Typhoid': 32,
 'Urinary tract infection': 33,
 'Varicose veins': 34,
 'hepatitis A': 35,
 'hepatitis C': 36,
 'hepatitis D': 37,
 'hepatitis E': 38}
	disease = disease_dict[disease]
	userid = Medical.patient
	print('Disease ID',disease)
	print('User ID is',id)
	print('disease id',disease)

	patient_id = Medical.objects.filter(pk=disease).values_list('patient_id', flat=True)
	# patient_id = list(patient_id)[0]
	print('-------------------------',patient_id)
	patient_id = patient_id
	disease_id = disease


	dob = Profile.objects.filter(user_id=id).values_list('birth_date', flat=True)
	print(dob)
	dob = list(dob)
	dob = dob[0]
	print('Date of birth is',dob)
	dob = str(dob)
	dob = dob[0:4]
	print('New Date of birth is',dob)
	dob = int(dob)
	age = 2023 - dob
	print('Patient Age is',age)
	

	gender = Profile.objects.filter(user_id=id).values_list('gender', flat=True)
	gender = list(gender)
	gender = gender[0]
	print('Patient Gender is',gender)

	if gender == 'Male':
		sex = 1
	else:
		sex = 0
	
	print('Patient Sex is',sex)
	
	if x in disease_dict:
		print('AI Got Drug For This Disease')
		print(disease_dict.get(x))
		new_sick = disease_dict.get(x)

		test = [new_sick,sex,age]
		print(test,'****************************************')
		test = np.array(test)
		print(test.shape)
		test = np.array(test).reshape(1,-1)
		print(test.shape)
		
		clf = joblib.load('model/medical_nb.pkl')
		prediction = clf.predict(test)
		prediction = prediction[0]
		print('Predicted Drug Is',prediction)
		# a = Medical(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, disease=result,medicine=prediction, patient_id=id)
	    # a.save()
		# return prediction

		try:
			check_medical = Medical.objects.filter(patient_id=disease).exists()
			if(check_medical == False):
				Medical.objects.filter(pk= disease).update(medicine=prediction)
				return [str(JsonResponse({'status':'recommended'})),prediction]
			else:
				print('Drug Exist')
			return JsonResponse({'status':'exist'}) 
		except Exception as e:
			print(e)    
	else:
		print('AI Can Not Recommend Drug')
		Medical.objects.filter(pk= disease).update(medicine='See Doctor')
		return JsonResponse({'status':'not is store'})





@login_required
def doctor_ment(request):
    user_id = request.user.id
    appointment = Ment.objects.all()
    context = {'ment':appointment, 'status':'1'}
    return render(request, 'doctor/ment.html', context)




@login_required
@csrf_exempt
def SaveMent(request):
  pk = request.POST.get('pk')
  day = request.POST.get('day')
  time = request.POST.get('time')


  disease = Ment.objects.filter(pk=pk).exists()
  print(disease)
  user_id = request.user.id


  
  try:
      check_ment = Ment.objects.filter(pk=pk).exists()
      if(check_ment == True):
          Ment.objects.filter(id=pk).update(approved=True,ment_day=day,time=time,doctor_id=user_id)
          return JsonResponse({'status':'Appointment Set'})
      else:
          print('Appointment Not Exist')
          return JsonResponse({'status':'not exist'}) 
  except Exception as e:
          print(e)
          return JsonResponse({'status':'error'}) 