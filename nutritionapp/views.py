import csv
import os
from django.shortcuts import render
from django.conf import settings

# 1. Helper function to handle 't' (trace) and non-numeric values
def clean_float(value):
    try:
        val_str = str(value).lower().strip()
        if val_str == 't' or not val_str:
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

# 2. Home view (This was missing, causing your AttributeError)
def home(request):
    return render(request, 'home.html')

# 3. Main Analysis view with modifications
def analyze_food(request):
    if request.method == "POST":
        food_query = request.POST.get('food_name', '').lower().strip()
        csv_path = os.path.join(settings.BASE_DIR, 'nutrition.csv')
        
        main_food = None
        alternative_food = None

        try:
            with open(csv_path, mode='r', encoding='utf-8') as file:
                reader = list(csv.DictReader(file))
                
                # Search for the main food item
                for row in reader:
                    if food_query in row['Food'].lower():
                        main_food = row
                        break
                
                # Look for a healthier alternative in the same category
                if main_food:
                    current_cat = main_food.get('Category', '')
                    for row in reader:
                        if row['Category'] == current_cat and row['Food'] != main_food['Food']:
                            if clean_float(row['Protein']) > clean_float(main_food['Protein']):
                                alternative_food = row
                                break
        except FileNotFoundError:
            return render(request, 'home.html', {'error': "Database (nutrition.csv) not found."})

        if main_food:
            # Process and clean data
            calories = clean_float(main_food.get('Calories', 0))
            protein = clean_float(main_food.get('Protein', 0))
            carbs = clean_float(main_food.get('Carbs', 0))
            fat = clean_float(main_food.get('Fat', 0))
            sugar = clean_float(main_food.get('Sugar', 0))
            fiber = clean_float(main_food.get('Fiber', 0))

            # Health Scoring Logic
            score = 0
            if protein >= 10: score += 30
            if sugar <= 5: score += 40
            if fiber >= 5: score += 30
            
            status, color = ("Healthy", "green") if score >= 70 else ("Moderate", "orange") if score >= 40 else ("Unhealthy", "red")

            context = {
                'food': main_food['Food'],
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'sugar': sugar,
                'fiber': fiber,
                'score': score,
                'status': status,
                'color': color,
                'alternative': alternative_food['Food'] if alternative_food else None
            }
            return render(request, 'result.html', context)
        else:
            return render(request, 'home.html', {'error': f"No data found for '{food_query}'"})
    
    return render(request, 'home.html')