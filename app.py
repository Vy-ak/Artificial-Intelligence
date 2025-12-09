import pickle
import numpy as np
import pandas as pd
import random 
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

with open('GrowthForecast.pkl', 'rb') as f:
    model = pickle.load(f)

with open('LabelEncoder.pkl', 'rb') as f:
    ke = pickle.load(f)

STATUS_MAPPING = {
    0: "Normal",
    1: "Tall",
    2: "Stunted",
    3: "Severely Stunted"
}

# Database Lokal buat makanan
# Format: { 'menu': 'Name', 'nutrition': 'Info', 'image': 'filename.jpg' }
FOOD_DB = {
    'baby_6_12': [
        {
            'menu': 'Bubur Hati Ayam', 
            'nutrition': 'Zat Besi: 6mg, Protein: 8g', 
            'image': 'bubur_hati.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+bubur+hati+ayam+mpasi',
            'website_url': 'https://cookpad.com/id/resep/17262151'
        },
        {
            'menu': 'Puree Ikan Kembung', 
            'nutrition': 'Omega-3: 1.2g, Protein: 10g', 
            'image': 'puree_ikan.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=cara+membuat+puree+ikan+mpasi',
            'website_url': 'https://cookpad.com/id/resep/15389113?ref=search&search_term=pure+ikan'
        },
        {
            'menu': 'Bubur Telur Yoghurt', 
            'nutrition': 'Kalsium: 150mg, Lemak: 5g', 
            'image': 'bubur_telur.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+mpasi+telur',
            'website_url': 'https://cookpad.com/id/resep/14447963?ref=search&search_term=mpasi+yoghurt+telur'
        }
    ],
    'toddler_12_24': [
        {
            'menu': 'Nasi Tim Telur Puyuh', 
            'nutrition': 'Protein: 12g (Setara 3 Telur Ayam)', 
            'image': 'telur_puyuh.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+nasi+tim+telur+puyuh',
            'website_url': 'https://cookpad.com/id/resep/24792452?ref=search&search_term=bubur+tim+telur+puyuh'
        },
        {
            'menu': 'Sup Bola Ikan Tenggiri', 
            'nutrition': 'Protein: 15g, Kalori: 250kkal', 
            'image': 'bola_ikan.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+sup+bola+ikan+tenggiri+anak',
            'website_url': 'https://cookpad.com/id/resep/24463300?ref=search&search_term=sup+baso+ikan+tenggiri'
        },
        {
            'menu': 'Nugget Tempe Ayam', 
            'nutrition': 'Serat: 4g, Protein: 14g', 
            'image': 'nugget_tempe.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+nugget+tempe+ayam+sehat',
            'website_url': 'https://cookpad.com/id/resep/10044605'
        }
    ],
    'kids_24_plus': [
        {
            'menu': 'Sate Lilit Ikan', 
            'nutrition': 'Protein: 18g, Lemak Sehat: 6g', 
            'image': 'sate_lilit.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+sate+lilit+ikan+tidak+pedas',
            'website_url': 'https://cookpad.com/id/resep/16964338'
        },
        {
            'menu': 'Orak Arik Telur Sayur', 
            'nutrition': 'Vitamin A: 400IU, Protein: 10g', 
            'image': 'orak_arik.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+orak+arik+telur+sayur+anak',
            'website_url': 'https://cookpad.com/id/resep/25177740?ref=search&search_term=orak+arik+sayuran'
        },
        {
            'menu': 'Perkedel Tahu Daging', 
            'nutrition': 'Zat Besi: 4mg, Kalori: 300kkal', 
            'image': 'perkedel.jpg',
            'youtube_url': 'https://www.youtube.com/results?search_query=resep+perkedel+tahu+daging+cincang',
            'website_url': 'https://cookpad.com/id/cari/perkedel%20tahu%20daging'
        }
    ]
}

# Berat badan ideal
WHO_MEDIAN = {
    6:  {0: 67.6, 1: 65.7},
    12: {0: 75.7, 1: 74.0},
    18: {0: 82.3, 1: 80.7},
    24: {0: 87.8, 1: 86.4},
    36: {0: 96.1, 1: 95.1},
    48: {0: 103.3, 1: 102.7},
    60: {0: 110.0, 1: 109.4}
}

def get_ideal_height_msg(age, gender, current_height):
    closest_age = min(WHO_MEDIAN.keys(), key=lambda x: abs(x - age))
    ideal = WHO_MEDIAN[closest_age][gender]
    
    diff = ideal - current_height
    if diff > 0:
        return f"Target tinggi ideal untuk usia ini adalah {ideal}cm. (Kurang {diff:.1f}cm)"
    return f"Tinggi anak sudah melampaui standar rata-rata ({ideal}cm). Bagus!"

def get_random_food(age_months):
    if age_months < 12:
        return random.choice(FOOD_DB['baby_6_12'])
    elif age_months < 24:
        return random.choice(FOOD_DB['toddler_12_24'])
    else:
        return random.choice(FOOD_DB['kids_24_plus'])

# --- APP ROUTES ---
@app.route('/')
def home():
    return render_template('HomePage.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        age = float(data['age'])
        height = float(data['height'])
        gender_str = data['gender']

        gender = 0 if gender_str == "Laki-laki" else 1

        features = pd.DataFrame([[age, height, gender]], 
                        columns=['Umur (bulan)', 'Tinggi Badan (cm)', 'Jenis Kelamin'])

        pred_code = model.predict(features)[0]
        status_text = STATUS_MAPPING[pred_code]

        food_data = get_random_food(age)
        ideal_msg = get_ideal_height_msg(age, gender, height)

        if pred_code >= 2: 
            suggestion_intro = "Perbaiki gizi segera dengan menu ini:"
        else:
            suggestion_intro = "Pertahankan gizi dengan variasi menu ini:"

        return jsonify({
            'status': status_text,
            'prediction_code': int(pred_code),
            'food_name': food_data['menu'],
            'food_nutrition': food_data['nutrition'],
            'food_image': food_data['image'],
            'food_youtube': food_data['youtube_url'],
            'food_website': food_data['website_url'],
            
            'ideal_height_msg': ideal_msg,
            'suggestion_intro': suggestion_intro
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)