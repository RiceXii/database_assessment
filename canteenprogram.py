"""
BURNSIDE HIGH SCHOOl Canteen Menu Database

"""
# Imported modules
from datetime import datetime
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
order_header = ['ID', 'TOTAL ITEMS', 'TOTAL PRICE', 'DATE']

# Establish a database connection
connection = sqlite3.connect("canteen.db")
cursor = connection.cursor()



# bold - \033[1m \033[m

# -------------Password and login function-------------
password = 'hi'

def stafflogin(max_attempts=3):
    clearscreen()
    for attempt in range(max_attempts):
        print('Enter password:\n')
        login = input('\033[1m--> \033[0m')
        
        if login == password:
            print('Access granted')
            return True
        
        else:
            remaining_attempts = max_attempts - attempt - 1
            if remaining_attempts:
                clearscreen()
                print(f'\033[1mIncorrect password. {remaining_attempts} attempt(s) remaining.\033[0m\n')
            else:
                clearscreen()
                print('\033[1mToo many incorrect attempts.\033[0m\n')

    return False
            
        
        


# -------------Function to check for FOOD ID-------------
def findID(id):
    data = [id]
    cursor.execute('SELECT food_id FROM food WHERE food_id =?', data)
    viewid = cursor.fetchall()
    if viewid:
        return True


# -------------Small functions-------------
def invalid():
    clearscreen()
    print("\033[30;41mInvalid input.\033[0m")
    time.sleep(1)
    clearscreen()

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


# -------------Order function-------------
def orderitems():
    clearscreen()
    print(".--- Order Food Items ---.")
    
    items_ordered = []
    total_price = 0

    while True:
        displayallmenu()

        print("\n\033[1mCART:\033[0m")
        if items_ordered:
            for i, item in enumerate(items_ordered, 1):
                print(f"{i}. {item}")
            print(f"Total items: {len(items_ordered)}")
            print(f"Total price: ${total_price:.2f}")
        else:
            pass

        try:
            item_id = int(input("\nEnter the ID of the food you want to order (or 0 to finish):\n"))
        except ValueError:
            invalid()
            continue

        if item_id == 0:
            break

        if not findID(item_id):
            clearscreen()
            print("\033[30;41mNot in menu.\033[0m")
            time.sleep(1)
            clearscreen()
            continue


        # Get item details
        cursor.execute("SELECT food_name, food_price FROM food WHERE food_id = ?", (item_id,))
        item = cursor.fetchone()
        if item:
            name, price = item
            items_ordered.append(name)
            total_price += price
            clearscreen()
            print(f"\033[92mAdded {name} - ${price:.2f}\033[0m")

    if not items_ordered:
        clearscreen()
        print("\033[1mNo items were ordered.\033[0m")
        time.sleep(2)
        return
    

    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [len(items_ordered), total_price, order_date]
    cursor.execute("INSERT INTO orders (total_items, total_price, order_date) VALUES (?, ?, ?)", data)
    connection.commit()


    clearscreen()
    print("\n\033[1mFinal Order Summary:\033[0m")
    for item in items_ordered:
        print(f"- {item}")
    print(f"Total items: {len(items_ordered)}")
    print(f"Total cost: ${total_price:.2f}")
    print(f"Order placed on: {order_date}")
    input("\nPress Enter to return to the main menu.")

def vieworderhistory():
    clearscreen()
    loadingscreen()
    vieworders = cursor.execute('SELECT * FROM ORDERS')
    rows = vieworders.fetchall()

    print(tabulate(rows, headers=order_header, tablefmt="simple_grid"))

    input('Press \033[1;44m ENTER \033[0m to go back to main menu\n')

# -------------Menu functions-------------
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
    clearscreen()

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
            category_id = int(input("\nEnter the category ID you want to view:\n"))
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
        print("\nFilter by availability:")
        print("1. Availabily only")
        print("2. Unavailable only")
        print("3. Both")

        avail_choice = input("\nEnter your choice (1-3):\n").strip()

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
        print("\n1. Ascending")
        print("2. Descending")

        id_choice = input('\nEnter your choice (1-2):\n').strip()

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
        loadingscreen()
        formatted_rows = [(id, name, cat, 'Yes' if avail else 'No', f"${price:.2f}") for id, name, cat, avail, price in rows]
        print("\n\033[1mSorted Menu Items:\033[0m")
        print(tabulate(formatted_rows, headers=menu_header, tablefmt="simple_grid"))

    input('Press \033[1;44m ENTER \033[0m to go back to main menu\n')

def displaycategory():
    viewall = cursor.execute('SELECT * FROM "category"')
    rows = viewall.fetchall()
    formatted_rows = [(category_id, category_name) for category_id, category_name in rows]

    print(' \033[1mCategories:\033[0m')
    print(tabulate(formatted_rows, headers=category_header, tablefmt="simple_grid"))



# -------------Edit menu functions-------------
def additem():
    clearscreen()

    title = " ADD NEW ITEM "
    print("\n" + "-"*50)
    print("\033[1;37;40m{:^50}\033[0m".format(title))
    print("-"*50 + "\n")

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

    title = " UPDATE ITEM "
    print("\n" + "-"*50)
    print("\033[1;37;40m{:^50}\033[0m".format(title))
    print("-"*50 + "\n\n")
    time.sleep(1)
    
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

    title = " UPDATE ITEM "
    print("\n" + "-"*50)
    print("\033[1;37;40m{:^50}\033[0m".format(title))
    print("-"*50 + "\n\n")
    time.sleep(1)
    
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
    clearscreen()

def editmenu():
    clearscreen()
    
    # Loop for edit menu
    while True:

        # TITLE
        clearscreen()
        title = " EDIT MENU "
        print("\n" + "="*70)
        print("\033[1;47m{:^70}\033[0m".format(title))
        print("="*70 + "\n")

        print("\033[1;30;48;5;33m [A] \033[0m \033[1mAdd New Item\033[0m\n")
        print("\033[1;30;48;5;33m [B] \033[0m \033[1mDelete Item\033[0m\n")
        print("\033[1;30;48;5;33m [C] \033[0m \033[1mUpdate Item\033[0m\n")
        print("\033\n[1;30;48;5;52m [ENTER] \033[0m \033[1mReturn to Main Menu\033[0m\n")

        edit_menu = input("\033[1m-->\033[0m ").lower().strip()
        
        if edit_menu == 'a':
            additem()
        elif edit_menu == 'b':
            deleteitem()
        elif edit_menu == 'c':
            edititem()
        else:
            break


# Order functions
def orderitem():
    
    print('.--- Order Items ---.')

    ordered_items = []
    item_count = 0

    while True:
        try:
            pass
        except ValueError:
            pass


#.--- Start of main program ---.
clearscreen()


# Main program loop
while True:
    
    # TITLE
    clearscreen()
    title = " BURNSIDE HIGH SCHOOL CANTEEN "
    print("\n" + "="*70)
    print("\033[1;42m{:^70}\033[0m".format(title))
    print("="*70 + "\n")

    print("\033[1;30;48;5;22m [O] \033[0m \033[1mOrder Food\033[0m\n")
    print("\033[1;30;48;5;22m [H] \033[0m \033[1mView Orders\033[0m\n")
    print("\033[1;30;48;5;22m [M] \033[0m \033[1mView Menu\033[0m\n")
    print("\033[1;30;48;5;22m [E] \033[0m \033[1mEdit Menu\033[0m\n")
    print("\033\n[1;30;48;5;52m [Q] \033[0m \033[1mQuit program\033[0m\n")
    
    main_menu = input("\033[1m-->\033[0m ").strip().upper()
    
    # Order items
    if main_menu == 'O':
        orderitems()
        
    # View order history
    if main_menu == 'H':
        vieworderhistory()
    
    # View menu
    if main_menu == 'M':
        viewmenusort()
        
    # Edit menu
    if main_menu == 'E':
        
        # Call login function
        if stafflogin():
            editmenu()
        else:
            print("\033[30;41mLOCKING OUT\033[0m")
            time.sleep(3)
            clearscreen()
            sys.exit()
            continue
    
    # Exit program
    if main_menu == 'Q':
        
        clearscreen()
        print("\n\n\n\n\n\n\n\n\n\033[1;3mSee ya next time ;)\033[0m")
        time.sleep(3)
        clearscreen()
        sys.exit()
    clearscreen()