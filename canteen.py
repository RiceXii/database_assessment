"""


BURNSIDE HIGH SCHOOl Canteen Menu Database


This program allows users to:
- Order items
- View order history
- Show items of the menu 
- Show sorted items of the menu (e.g Category, Availability)
- Edit items of the menu if they are staff 

(password is in the login function section)

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



# -------------Password and login function-------------
password = 'burnsidestaff'

def stafflogin(max_attempts=3):
    clearscreen()
    for attempt in range(max_attempts):
        print('Enter password:\n')
        login = input('\033[1m--> \033[0m')
        
        # If user inputs correct password, return True
        if login == password:
            print('Access granted')
            return True
        
        # If user inputs incorrect password, minus an attempt.
        else:
            remaining_attempts = max_attempts - attempt - 1
            if remaining_attempts:
                clearscreen()
                print(f'\033[1mIncorrect password. {remaining_attempts} attempt(s) remaining.\033[0m\n')
            else:
                clearscreen()
                print('\033[1mToo many incorrect attempts.\033[0m\n')

    # If user runs out of attempts, return False
    return False
            
        
        


# -------------Function to check things (Find id and check availability) -------------
def findID(id):
    data = [id]
    cursor.execute('SELECT food_id FROM food WHERE food_id =?', data)
    viewid = cursor.fetchall()
    # If ID is found, then return True
    if viewid:
        return True

def is_item_available(food_id):
    cursor.execute("SELECT availability FROM food WHERE food_id = ?", (food_id,))
    result = cursor.fetchone()
    return result[0] == 1 # Checks if the first value in the tuple is 1 and returns true

# -------------Small functions-------------
def invalid():
    clearscreen()
    print("\033[1;30;48;5;52mInvalid input.\033[0m")
    time.sleep(1)
    clearscreen()

def clearscreen():
    os.system('cls' if os.name == 'nt' else 'clear') # Clears the terminal

# Loading screen to let users process whats happening
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
    
    # TITLE
    title = " ORDER FOOD "
    print("\n" + "-"*50)
    print("\033[1;37;40m{:^50}\033[0m".format(title))
    print("-"*50 + "\n")

    # List for items and variable for total price
    items_ordered = []
    total_price = 0

    # Loop for ordering items
    while True:
        
        # Show menu to user
        displayallmenu()

        # Display the cart
        print("\n\033[1;97;44m [CART] \033[0m")
        if items_ordered:
            for i, item in enumerate(items_ordered, 1): # Enumerate goes through each item and puts a number on it
                print(f"\033[1m{i}. {item}\033[0m")  # Items in cart
            
            # Show amount of items and the total price live
            print(f"\033[1;34mTotal items: \033[0m{len(items_ordered)}") 
            print(f"\033[1;34mTotal price: \033[0m\033[1;32m${total_price:.2f}\033[0m")
            
        else:
            # If there isnt anything in items_ordered, print cart is empty
            print("\033[3;90mcart is empty\033[0m")  

        try:
            print('\n\033[1mEnter ID\033[0m\n\033[3m0 to finish\033[0m')

            item_id = int(input("\033[1m-->\033[0m ").strip())
       
        # Invalid input
        except ValueError:
            clearscreen()
            print("\033[1;30;48;5;52mInvalid input. Please enter a valid number.\033[0m")
            time.sleep(1)
            clearscreen()
            continue

        # Finish ordering
        if item_id == 0:
            break

        # Check if ID is in the menu 
        if not findID(item_id):
            clearscreen()
            print("\033[30;41mItem not in menu.\033[0m")
            time.sleep(1)
            clearscreen()
            continue
       
        # Check if item is available
        if is_item_available(item_id) == False:
            clearscreen()
            print("\033[30;41mItem not currently available\033[0m")
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
            print(f"\033[92mAdded {name} - ${price:.2f} to your cart.\033[0m")

    # No items were ordered
    if not items_ordered:
        clearscreen()
        print("\033[1;3mNo items were ordered.\033[0m")
        time.sleep(2)
        return

    # Get the current time and date 
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Store the order into orders table
    data = [len(items_ordered), total_price, order_date]
    cursor.execute("INSERT INTO orders (total_items, total_price, order_date) VALUES (?, ?, ?)", data)
    connection.commit()

    # Print out the order
    clearscreen()
    print("\n\033[1;97;44mFinal Order Summary:\033[0m")
    for item in items_ordered:
        print(f"\033[1m- {item}\033[0m")  # List of items
    print(f"\033[1;34mTotal items:\033[0m {len(items_ordered)}")
    print(f"\033[1;34mTotal cost:\033[0m \033[1;32m${total_price:.2f}\033[0m")
    print(f"\033[1;34mOrder placed on:\033[0m {order_date}")
    print("\033\n[1;30;48;5;52m [ENTER] \033[0m \033[1mReturn to Main Menu\033[0m")
    input("\033[1m-->\033[0m ").lower().strip()


def vieworderhistory():
    clearscreen()
    loadingscreen()
    vieworders = cursor.execute('SELECT * FROM ORDERS')
    rows = vieworders.fetchall()

    # Format it so that it displays the price with $
    formatted_rows = [(i, t, f"${p:.2f}", d) for i, t, p, d in rows]

    # TITLE
    clearscreen()
    title = " View Order History "
    print("\n" + "="*70)
    print("\033[1;47m{:^70}\033[0m".format(title))
    print("="*70 + "\n")

    print(tabulate(formatted_rows, headers=order_header, tablefmt="simple_grid"))

    print("\033\n[1;30;48;5;52m [ENTER] \033[0m \033[1mReturn to Main Menu\033[0m\n")
    input("\033[1m-->\033[0m ").lower().strip()



# ------------- Menu functions -------------
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
   
    # TITLE
    clearscreen()
    title = " View Menu "
    print("\n" + "="*70)
    print("\033[1;47m{:^70}\033[0m".format(title))
    print("="*70 + "\n")

    print("\033[1;30;46m [A] \033[0m \033[1mAvailability View\033[0m\n")
    print("\033[1;30;46m [I] \033[0m \033[1mID View\033[0m\n")
    print("\033[1;30;46m [C] \033[0m \033[1mCategory View\033[0m\n")
    print("\033[1;30;46m [P] \033[0m \033[1mPrice view\033[0m\n")
    print("\n\033[1;30;48;5;52m [ENTER] \033[0m \033[1mReturn to Main Menu\033[0m\n")

    view_menu = input("\033[1m-->\033[0m ").upper().strip()

    # View by ID
    if view_menu == 'I':
        
        while True:
            clearscreen()
            print("\n" + "="*70)
            print("\033[1;47m{:^70}\033[0m".format(title))
            print("="*70 + "\n")        

            print("\033[1m--- Sort by ID ---\n")
            print("\033[1;30;47m [A] \033[0m Ascending\n")
            print("\033[1;30;47m [D] \033[0m Descending\n")
            
            id_view_menu = input("\033[1m-->\033[0m ").strip().upper()

            if id_view_menu == 'A':
                cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id ORDER BY food.food_id ASC")
                break
            elif id_view_menu == 'D':
                cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id ORDER BY food.food_id DESC")
                break
            else:
                invalid()

    # View by Availability
    elif view_menu == 'A':
        
        while True:
            clearscreen()
            print("\n" + "="*70)
            print("\033[1;47m{:^70}\033[0m".format(title))
            print("="*70 + "\n")

            print("\033[1m--- Filter by availability ---\n")
            print("\033[1;30;47m [A] \033[0m Availabile only\n")
            print("\033[1;30;47m [U] \033[0m Unavailable only\n")
            print("\033[1;30;47m [B] \033[0m Both\n")

            avail_view_menu = input("\n\033[1m-->\033[0m ").strip().upper()

            if avail_view_menu == 'A':
                cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id WHERE food.availability = 1")
                break
            if avail_view_menu == 'U':
                cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id WHERE food.availability = 0")
                break
            if avail_view_menu == 'B':
                cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id")
                break
            else:
                invalid()
                continue

    # View by Category
    elif view_menu == 'C':
        

        
        while True:
            try:
                # Title
                clearscreen()
                print("\n" + "="*70)
                print("\033[1;47m{:^70}\033[0m".format(title))
                print("="*70 + "\n")      
                
                displaycategory()
                
                # Ask user for category
                print("\033[1m--- Filter by Category ---\n")
                print('\n\033[1mEnter ID\033[0m')
                category_id = int(input("\033[1m-->\033[0m "))
                break
            except ValueError:
                invalid()
            
        # If the user inputs a category that doesn't exist, tell them
        if not cursor.execute("SELECT 1 FROM category WHERE category_id = ?", (category_id,)).fetchone():
            print("\033[1;31mThat category does not exist.\033[0m")
            time.sleep(1.5)
            return

        # Filter by category
        cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id WHERE food.category_id = ?", (category_id,))
        
    # View by Price
    elif view_menu == 'P':
        


        while True:
            
            # Title
            clearscreen()
            print("\n" + "="*70)
            print("\033[1;47m{:^70}\033[0m".format(title))
            print("="*70 + "\n")        

            # Ask user for input
            print("\033[1m--- Sort by Price ---\n")
            print("\033[1;30;47m [A] \033[0m Ascending\n")
            print("\033[1;30;47m [D] \033[0m Descending\n")            
            
            price_view_menu = input("\033[1m-->\033[0m ").strip().upper()

            if price_view_menu == 'A':
                # Sort by ascending price
                cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id ORDER BY food.food_price ASC")
                break
            elif price_view_menu == 'D':
                # Sort by descending price
                cursor.execute("SELECT food.food_id, food.food_name, category.category_name, food.availability, food.food_price FROM food JOIN category ON food.category_id = category.category_id ORDER BY food.food_price DESC")
                break
            else:
                invalid()
    # Return to menu
    else:
        return

    rows = cursor.fetchall()
    
    # If no items are found
    if not rows:
        print("\n\033[1;30;48;5;52m No items found for this filter \033[0m")
        time.sleep(1)
    else:
        loadingscreen()
        
        # Title
        print("\n" + "="*70)
        print("\033[1;47m{:^70}\033[0m".format(title))
        print("="*70 + "\n")      

        # Print out sorted items
        formatted_rows = [(id, name, cat, 'Yes' if avail else 'No', f"${price:.2f}") for id, name, cat, avail, price in rows]
        print("\n\033[1mSorted Menu:\033[0m")
        print(tabulate(formatted_rows, headers=menu_header, tablefmt="simple_grid"))

    # Enter to go back to main menu
    print("\n\033[1;30;48;5;52m [ENTER] \033[0m \033[1mReturn to Main Menu\033[0m\n")
    input("\033[1m-->\033[0m ").lower().strip()



def displaycategory():
    viewall = cursor.execute('SELECT * FROM "category"')
    rows = viewall.fetchall()
    formatted_rows = [(category_id, category_name) for category_id, category_name in rows]

    # Print out the categories
    print(' \033[1mCategories:\033[0m')
    print(tabulate(formatted_rows, headers=category_header, tablefmt="simple_grid"))



# ------------- Edit menu functions -------------

# Function to add a new item to the menu
def additem():
    clearscreen()

    # Print title
    title = " ADD NEW ITEM "
    print("\n" + "-"*50)
    print("\033[1;37;40m{:^50}\033[0m".format(title))
    print("-"*50 + "\n")

    # Input: item name
    name = input('Enter name of item:\n')

    # Input: price (must be positive float)
    while True:
        try:
            price = float(input('Enter item price:\n').strip())
            if price <= 0:
                print('Price must be larger than 0')
                continue
            break
        except ValueError:
            print('Invalid input, please enter a price.')

    # Input: availability (must be 0 or 1)
    while True:
        try:
            availability = int(input('Item availability (1 = True, 0 = False)\n'))
            if availability not in (0, 1):
                raise ValueError
            break
        except ValueError:
            print('Invalid input. Enter 1 or 0')

    # Display and choose category by ID
    displaycategory()
    while True:
        try: 
            category = int(input('Choose category (enter category ID as shown above)\n'))
            if category > 8 or category < 1:
                print('ID not in database')
                continue
            break
        except ValueError:
            print('Invalid input. Enter ID of category')

    # Insert new item into database
    data = [name, price, availability, category]
    cursor.execute("INSERT INTO 'food' ('food_name', 'food_price', 'availability', 'category_id') VALUES (?,?,?,?)", data)
    connection.commit()

# Function to update existing menu items
def edititem():
    while True:
        clearscreen()
        title = " UPDATE ITEM "
        print("\n" + "-"*50)
        print("\033[1;37;40m{:^50}\033[0m".format(title))
        print("-"*50 + "\n\n")
        time.sleep(1)

        # Show menu items to choose from
        displayallmenu()

        # Input: item ID to edit
        try:
            food_id = int(input("Enter the ID of the item you want to edit:\n"))
        except ValueError:
            invalid()
            continue

        # Check if ID exists
        if not findID(food_id):
            invalid()
            continue

        # Display edit options
        print("\033[1;30;47m [N] \033[0m \033[1mUpdate Name\033[0m\n")
        print("\033[1;30;47m [P] \033[0m \033[1mUpdate Price\033[0m\n")
        print("\033[1;30;47m [A] \033[0m \033[1mUpdate Availability\033[0m\n")
        print("\033[1;30;47m [C] \033[0m \033[1mUpdate Category\033[0m\n")
        print("\n\033[1;30;48;5;52m [ENTER] \033[0m \033[1mReturn to Edit Menu\033[0m\n")

        edit_menu = input("\033[1m-->\033[0m ").strip().upper()

        # Back to menu if user inputs enter
        if edit_menu == '':
            return

        # Update name
        if edit_menu == 'N':
            print('\033[1mEnter new name:')
            new_name = input("\033[1m-->\033[0m ").strip()
            cursor.execute("UPDATE food SET food_name = ? WHERE food_id = ?", (new_name, food_id))
            break

        # Update price
        elif edit_menu == 'P':
            try:
                print('\033[1mEnter price:')
                new_price = float(input("\033[1m-->\033[0m\n").strip())
                if new_price <= 0:
                    print("Price must be greater than 0.")
                    continue
                cursor.execute("UPDATE food SET food_price = ? WHERE food_id = ?", (new_price, food_id))
                break
            except ValueError:
                print("Invalid input. Must be a number.")
                continue

        # Update availability
        elif edit_menu == 'A':
            try:
                print('\033[1mEnter availability\033[0m\n\033[3m1 = yes 0 = no')
                new_availability = int(input("\033[1m--> \033[0m"))
                if new_availability not in (0, 1):
                    raise ValueError
                cursor.execute("UPDATE food SET availability = ? WHERE food_id = ?", (new_availability, food_id))
                break
            except ValueError:
                print("Invalid input. Enter 1 or 0.")
                continue

        # Update category
        elif edit_menu == 'C':
            displaycategory()
            try:
                print('\033[1mEnter category\033[0m')
                new_category = int(input("\033[1m--> \033[0m"))
                if new_category < 1 or new_category > 7:
                    print("Invalid category.")
                    continue
                cursor.execute("UPDATE food SET category_id = ? WHERE food_id = ?", (new_category, food_id))
                break
            except ValueError:
                print("Invalid input.")
                continue

        else:
            print("Invalid input. Please choose")
            continue

    connection.commit()
    print("Item updated successfully.")
    time.sleep(1)

# Function to delete an item from the menu
def deleteitem():
    while True:
        try:
            clearscreen()
            title = " DELETE ITEM "
            print("\n" + "-"*50)
            print("\033[1;37;40m{:^50}\033[0m".format(title))
            print("-"*50 + "\n\n")
            time.sleep(1)

            displayallmenu()

            print("\033[1m--- Delete Item ---\n")
            print("\033[1mEnter ID")
            food_id = int(input("\033[1m--> "))

            if not findID(food_id):
                invalid()
                continue
            break
        except ValueError:
            invalid()
            continue

    # Confirm deletion
    cursor.execute("SELECT food_name FROM food WHERE food_id = ?", (food_id,))
    item_name = cursor.fetchone()[0]

    clearscreen()
    confirm = input(f"Are you sure you want to delete '{item_name}'? (y/n): ").lower().strip()
    if confirm == 'y':
        cursor.execute("DELETE FROM food WHERE food_id = ?", (food_id,))
        connection.commit()
        print(f"'{item_name}' has been deleted.")
    else:
        print("Delete cancelled.")

    time.sleep(1.5)
    clearscreen()

# Main edit menu function
def editmenu():
    clearscreen()
    
    while True:
        clearscreen()
        title = " EDIT MENU "
        print("\n" + "="*70)
        print("\033[1;47m{:^70}\033[0m".format(title))
        print("="*70 + "\n")

        # Display edit options
        print("\033[1;38;5;16;48;5;94m [A] \033[0m \033[1mAdd New Item\033[0m\n")
        print("\033[1;38;5;16;48;5;94m [D] \033[0m \033[1mDelete Item\033[0m\n")
        print("\033[1;38;5;16;48;5;94m [U] \033[0m \033[1mUpdate Item\033[0m\n")
        print("\n\033[1;30;48;5;52m [ENTER] \033[0m \033[1mReturn to Main Menu\033[0m\n")

        edit_menu = input("\033[1m-->\033[0m ").upper().strip()

        # Options
        if edit_menu == 'A':
            additem()
        elif edit_menu == 'D':
            deleteitem()
        elif edit_menu == 'U':
            edititem()
        else:
            break





# --------- Main program loop ---------
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
        
        # If login fails, lock out of program
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