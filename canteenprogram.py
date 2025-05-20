"""
BURNSIDE HIGH SCHOOl Canteen Menu Database

"""
# Imported modules
import time
import subprocess
import sys
import sqlite3
import os

# Try importing tabulate, if not installed, install it using pip
try:
    from tabulate import tabulate
except ImportError:
    print("Installing 'tabulate'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
    print("'tabulate' installed successfully. Please restart the program.")
    sys.exit()


# Define table headers
menu_header = ['ID', 'ITEM', 'CATEGORY','AVAILABILITY' , 'PRICE']
category_header = ['ID', 'CATEGORY']

# Establish a database connection
connection = sqlite3.connect("canteen.db")
cursor = connection.cursor()

# Password for staff only functions 
password = 'hi'


# Function for login system
def stafflogin(max_attempts=3):
    
    for attempt in range(max_attempts):
        login = input('Enter password\n')
        if login == password:
            print('Access granted')
            return True
        
        else:
            
            remaining_attempts = max_attempts - attempt - 1
            if remaining_attempts:
                print(f'Incorrect password. {remaining_attempts} attempts remaining.')
            else:
                print('Too many incorrect attempts.')
    return False
        
# Function to check if a food ID exists in the database
def findID(id):
    data = [id]
    cursor.execute('SELECT food_id FROM food WHERE food_id =?', data)
    viewid = cursor.fetchall()
    if viewid:
        return True


# Functions for screen clearing and loading
def clearscreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def loadingscreen():
    clearscreen()
    print('\033[1;37;42m Loading \033[0m')
    time.sleep(0.2)
    clearscreen()
    print('\033[1;37;42m Loading. \033[0m')
    time.sleep(0.2)
    clearscreen()
    print('\033[1;37;42m Loading.. \033[0m')
    time.sleep(0.2)
    clearscreen()
    print('\033[1;37;42m Loading... \033[0m')
    time.sleep(0.2)
    clearscreen()


# Menu functions
def displayallmenu():

    # Get data from database
    viewall = cursor.execute('SELECT food.food_id, food.food_name, category.category_name,food.availability , food.food_price FROM food JOIN category ON food.category_id = category.category_id')
    rows = viewall.fetchall()

    # Convert 1/0 to Yes/No
    formatted_rows = [(id, name, cat, 'Yes' if avail else 'No', f"${price:.2f}") for id, name, cat, avail, price in rows]

    # Print out in table
    print(' \033[1mMENU:\033[0m')
    print(tabulate(formatted_rows, headers=menu_header, tablefmt="simple_grid"))

def viewmenusort():
    
    print(".--- View Menu ---.\n")
    
    print("1. View by category")
    print("2. View by avalailability")
    print("3. View by price")
    print("4. View by ID")
    print('Press \033[1;44m ENTER \033[0m to go back to main menu\n')

    choice = input("Enter your choice (1-4):\n").strip()

    if choice == '1':
        displaycategory()
        try:
            category_id = int(input("Enter the category ID you want to view:\n"))
        except ValueError:
            print("Invalid input. Must be a number.")
            return

        cursor.execute("SELECT category_name FROM category WHERE category_id = ?", (category_id,))
        category = cursor.fetchone()
        if not category:
            print("That category does not exist.")
            return

        cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id WHERE food.category_id = ?", (category_id,))

    elif choice == '2':
        print("Filter by availability:")
        print("1. Availabily only")
        print("2. Unavailable only")
        print("3. Both")

        avail_choice = input("Enter your choice (1-3):\n").strip()

        if avail_choice == '1':
            cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id WHERE food.availability = 1")
        elif avail_choice == '2':
            cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id WHERE food.availability = 0")
        elif avail_choice == '3':
            cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id")
        else:
            print("Invalid choice.")
            return


    elif choice == '3':
        cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id ORDER BY food.food_price ASC")

    elif choice == '4':
        print("1. Ascending")
        print("2. Descending")

        id_choice = input('Enter your choice (1-2):\n').strip()

        if id_choice == '1':
            cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id ORDER BY food.food_id ASC")

        if id_choice == '2':
            cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id ORDER BY food.food_id DESC")

    
    
    else:
        loadingscreen()
        return

    rows = cursor.fetchall()
    if not rows:
        print("No items found for this filter.")
    else:
        formatted_rows = [(id, name, cat, 'Yes' if avail else 'No', f"${price:.2f}") for id, name, cat, avail, price in rows]
        print("\n\033[1mSorted Menu Items:\033[0m")
        print(tabulate(formatted_rows, headers=menu_header, tablefmt="simple_grid"))

    input("\nEnter anything to go back.")

    
def displaycategory():
    viewall = cursor.execute('SELECT * FROM "category"')
    rows = viewall.fetchall()
    formatted_rows = [(category_id, category_name) for category_id, category_name in rows]
    
    print(' \033[1mCategories:\033[0m')
    print(tabulate(formatted_rows, headers=category_header, tablefmt="simple_grid"))



# Edit menu functions
def additem():

    print('.--- Add new item ---.')

    name = input('Enter name of item:\n')

    while True:
        
        try:
            price = float(input('Enter item price:\n').strip())
            
            if price <= 0:
                print('Price must be larger than 0')
                continue
            break
        except ValueError:
            print('Invalid input, please enter a price.')
    
    while True:
        
        try:
            
            availability = int(input('Item avaiiability (1 = True, 0 = False)\n'))
            if availability not in (0, 1):
                raise ValueError
            break

        except ValueError:
            print('Invalid input. Enter 1 or 0')
    
    displaycategory()
    while True:
        
        try: 
            
            category = int(input('Choose catagory (enter category ID as shown above)\n'))
            if category > 8 or category < 1:
                print('ID not in database')
                continue
            break
        
        except ValueError:
            print('Invalid input. Enter ID of category')

    data = [name, price, availability, category]
    cursor.execute("INSERT INTO 'food' ('food_name', 'food_price', 'availability', 'category_id') VALUES (?,?,?,?)", data)
    connection.commit()

def edititem():
    clearscreen()
    print(".--- Edit an existing item ---.")
    displayallmenu()

    try:
        food_id = int(input("Enter the ID of the item you want to edit:\n"))
    except ValueError:
        print("Invalid input. Must be a number.")
        return

    if not findID(food_id):
        print("Item with that ID doesn't exist.")
        return

    print("What would you like to update?")
    print("1. Name")
    print("2. Price")
    print("3. Availability")
    print("4. Category")
    
    edit_menu = input("Enter the number of the thing you want to update:\n").strip()

    if edit_menu == '1':
        new_name = input("Enter new name:\n").strip()
        cursor.execute("UPDATE food SET food_name = ? WHERE food_id = ?", (new_name, food_id))

    elif edit_menu == '2':
        try:
            new_price = float(input("Enter new price:\n").strip())
            if new_price <= 0:
                print("Price must be greater than 0.")
                return
            cursor.execute("UPDATE food SET food_price = ? WHERE food_id = ?", (new_price, food_id))
        except ValueError:
            print("Invalid input. Must be a number.")
            return

    elif edit_menu == '3':
        try:
            new_availability = int(input("Enter availability (1 = Yes, 0 = No):\n"))
            if new_availability not in (0, 1):
                raise ValueError
            cursor.execute("UPDATE food SET availability = ? WHERE food_id = ?", (new_availability, food_id))
        except ValueError:
            print("Invalid input. Enter 1 or 0.")
            return

    elif edit_menu == '4':
        displaycategory()
        try:
            new_category = int(input("Enter new category ID:\n"))
            if new_category < 1 or new_category > 7:
                print("Invalid category.")
                return
            cursor.execute("UPDATE food SET category_id = ? WHERE food_id = ?", (new_category, food_id))
        except ValueError:
            print("Invalid input.")
            return

    else:
        print("Invalid input. Please choose")
        return

    connection.commit()
    print("Item updated successfully.")
    time.sleep(1)

def deleteitem():
    clearscreen()
    print(".--- Delete an item from the menu ---.")
    displayallmenu()

    try:
        food_id = int(input("Enter the ID of the item you want to delete:\n"))
    except ValueError:
        print("Invalid input. Must be a number.\n")
        time.sleep(1)
        clearscreen()
        return

    if not findID(food_id):
        print("No item with that ID exists.\n")
        time.sleep(1)
        clearscreen()
        return

    # Get the item details before deleting
    cursor.execute("SELECT food_name FROM food WHERE food_id = ?", (food_id,))
    item_name = cursor.fetchone()[0]

    confirm = input(f"Are you sure you want to delete '{item_name}'? (y/n): ").lower().strip()
    if confirm == 'y':
        cursor.execute("DELETE FROM food WHERE food_id = ?", (food_id,))
        connection.commit()
        print(f"'{item_name}' has been deleted.")
    else:
        print("Delete cancelled.")

    time.sleep(1.5)

def editmenu():
    
    # Loop for edit menu
    while True:

        print(".--- Editing menu ---.")

        edit_menu = input('Enter \033[1m"A"\033[0m to add a new item \nEnter \033[1m"B"\033[0m to delete an item\nEnter \033[1m"C"\033[0m to update an item\nEnter anything else to go back to main menu\n').lower().strip()
    
        if edit_menu == 'a':
            additem()
        elif edit_menu == 'b':
            deleteitem()
        elif edit_menu == 'c':
            edititem()
        else:
            break



#.--- Start of main program ---.
clearscreen()

print('Welcome to the Burnside High School online canteen menu!')
time.sleep(0.5)

# Main program loop
while True:
    
    
    print('MAIN MENU:')
    
    # Prompt user for main menu input
    main_menu = input('Enter \033[1m"A"\033[0m to order\nEnter \033[1m"B"\033[0m to view order history\nEnter \033[1m"C"\033[0m to view menu\nEnter \033[1m"D"\033[0m to edit menu (staff only)\n').strip().upper()

    # Order items
    if main_menu == 'A':
        print('You chose order items from menu')
        
    # View order history
    if main_menu == 'B':
        pass
    
    # View menu
    if main_menu == 'C':
        loadingscreen()
        viewmenusort()
        

    if main_menu == 'D':
        
        # Call login function
        if stafflogin():
            loadingscreen()
            clearscreen()
            editmenu()
        else:
            
            continue
    clearscreen()