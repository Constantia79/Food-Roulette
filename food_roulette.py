import csv
import random
import os
import time
from datetime import datetime

RESTAURANTS_FILE = 'restaurants.csv'
PICKS_FILE = 'picks.csv'
CHALLENGES = [
    'Order the most expensive dish',
    'Order something you have never tried',
    'Order for someone else'
]
BUDGET_OPTIONS = ['cheap', 'medium', 'expensive', 'any']
DIET_OPTIONS = ['none', 'vegetarian', 'halal', 'kosher']

# Load restaurant data from csv
def load_restaurants(filename):
    restaurants = []
    with open(filename, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            restaurants.append(row)
    return restaurants

# Apply user input to the restaurant list
def filter_restaurants(restaurants, cuisine, budget, diet, max_distance):
    filtered = []
    for item in restaurants:
        if item['cuisine'] != cuisine:
            continue
        if budget != 'any' and item['price_range'] != budget:
            continue
        if item['dietary'] != diet:
            continue
        try:
            if float(item['distance_km']) > max_distance:
                continue
        except ValueError:
            continue
        filtered.append(item)
    return filtered

# Save a user pick to csv
def save_pick(pick):
    file_exists = os.path.exists(PICKS_FILE)
    with open(PICKS_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['timestamp', 'cuisine', 'restaurant', 'budget', 'dietary', 'distance', 'challenge'])
        if not file_exists:
            writer.writeheader()
        writer.writerow(pick)

# Display previously saved picks to the user
def view_history():
    if not os.path.exists(PICKS_FILE):
        print("No history found.")
        return
    with open(PICKS_FILE, newline='') as file:
        reader = csv.DictReader(file)
        print("Previous picks:")
        for row in reader:
            print(f"{row['timestamp']}: {row['cuisine']} at {row['restaurant']} ({row['challenge']})")

# Choose a random option, avoiding the last one if possible
def spin_unique(options, last_choice):
    print("Spinning the wheel", end='', flush=True)
    for _ in range(3):
        print('.', end='', flush=True)
        time.sleep(0.5)
    print()
    pool = [opt for opt in options if opt != last_choice] or options.copy()
    choice = random.choice(pool)
    print("You got: " + choice)
    return choice

# Prompt the user until they enter a valid option
def get_user_choice(prompt, options):
    while True:
        response = input(prompt).strip().lower()
        if response in options:
            return response
        print(f"Please enter a valid option: {options}")

# Main roulette
def main():
    restaurants = load_restaurants(RESTAURANTS_FILE)
    budget = get_user_choice(f"Enter your budget {BUDGET_OPTIONS}: ", BUDGET_OPTIONS)
    diet = get_user_choice(f"Enter dietary preference {DIET_OPTIONS}: ", DIET_OPTIONS)

    # distance restrictions
    while True:
        dist_input = input("Enter max distance from Sydney Uni (default 3): ").strip()
        if dist_input == '':
            max_distance = 3.0
        else:
            try:
                max_distance = float(dist_input)
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
        distances = [float(item['distance_km']) for item in restaurants]
        min_dist = min(distances) if distances else 0
        if max_distance < min_dist:
            print(f"Invalid distance. The closest restaurant is {min_dist} km away.")
            continue
        break

    last_cuisine = None
    last_restaurant = None

    while True:
        print("Menu: 1. Spin 2. View history 3. Quit")
        menu_choice = input("Enter 1, 2, or 3: ").strip()
        if menu_choice == '1':
            # Unique cuisine selection
            cuisines = []
            for item in restaurants:
                if item['cuisine'] not in cuisines:
                    cuisines.append(item['cuisine'])
            cuisine = spin_unique(cuisines, last_cuisine)
            last_cuisine = cuisine

            matched = filter_restaurants(restaurants, cuisine, budget, diet, max_distance)
            if not matched:
                print("No restaurants match your filters.")
                continue

            # Unique restaurant selection
            rest_list = [item['restaurant'] for item in matched]
            restaurant = spin_unique(rest_list, last_restaurant)
            last_restaurant = restaurant

            # Change restaurant if alternative option exists
            if len(rest_list) > 1:
                change = get_user_choice("Change restaurant? (yes or no): ", ['yes', 'no'])
                if change == 'yes':
                    restaurant = spin_unique(rest_list, restaurant)
                    last_restaurant = restaurant
            else:
                print("No alternative restaurants available to change.")

            challenge = random.choice(CHALLENGES)
            print("Challenge: " + challenge)

            pick = {
                'timestamp': datetime.now().isoformat(),
                'cuisine': cuisine,
                'restaurant': restaurant,
                'budget': budget,
                'dietary': diet,
                'distance': str(max_distance),
                'challenge': challenge
            }
            save_pick(pick)

        elif menu_choice == '2':
            view_history()

        elif menu_choice == '3':
            print("Thank you for using food roulette! Goodbye.")
            break

        else:
            print("Invalid menu choice. Try again.")

if __name__ == '__main__':
    main()
