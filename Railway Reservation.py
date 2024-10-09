from mysql import connector
import mysql.connector
import random

# Establish database connection
try:
    cnx = mysql.connector.connect(user='root', password='hate', host='localhost', database='railway')
    db_cursor = cnx.cursor()
    print("Welcome to the railway reservation program!!\n")
except mysql.connector.Error as err:
    print(f"Error connecting to the database: {err}\n")
    exit(1)

def welcome():
    print("To get to know the basic commands type /help\n")
    wywd = input().strip()
    if wywd.lower() == "/help":
        print(
            "\nmr -- making reservation\n"
            "cs -- checking status\n"
            "cr -- canceling reservations\n"
            "fr -- making food reservation\n"
            "vf -- view food reservations\n"
            "cf -- cancel food reservation\n"
            "login -- user login\n"
        )
        welcome()
    elif wywd.lower() == "mk res":
        mk_res()
    elif wywd.lower() == "chl res":
        try:
            pnrcon = int(input("Enter your pnr no: "))
            chk_res(pnrcon)
        except ValueError:
            print("Invalid PNR number. Please enter a numeric value.\n")
            welcome()
    elif wywd.lower() == "cncl res":
        try:
            pnrcon = int(input("Enter your pnr no to cancel: "))
            cncl_res(pnrcon)
        except ValueError:
            print("Invalid PNR number. Please enter a numeric value.\n")
            welcome()
    elif wywd.lower() == "fr":
        try:
            pnrcon = int(input("Enter your PNR no for food reservation: "))
            fr_res(pnrcon)
        except ValueError:
            print("Invalid PNR number. Please enter a numeric value.\n")
            welcome()
    elif wywd.lower() == "vf":
        try:
            pnrcon = int(input("Enter your PNR no to view food reservations: "))
            vf_res(pnrcon)
        except ValueError:
            print("Invalid PNR number. Please enter a numeric value.\n")
            welcome()
    elif wywd.lower() == "cf":
        try:
            fr_id = int(input("Enter your Food Reservation ID to cancel: "))
            cf_res(fr_id)
        except ValueError:
            print("Invalid Food Reservation ID. Please enter a numeric value.\n")
            welcome()
    elif wywd.lower() == "login":
        nm = input("Enter your user ID: ").strip()
        pwd = input("Enter your password: ").strip()
        login(nm, pwd)
    else:
        print("Command not found. Please try again or type '/help' without quotes to know the existing commands!\n")
        welcome()

def gen():
    ls = ['confirmed', 'waiting']
    while True:
        gen_pnr = random.randint(1000000000, 9999999999)
        # Check if PNR already exists
        db_cursor.execute("SELECT COUNT(*) FROM USERS WHERE pnrno = %s", (gen_pnr,))
        count = db_cursor.fetchone()[0]
        if count == 0:
            break
    gen_status = random.choice(ls)
    gen_seat = random.randint(1, 101)
    return gen_pnr, gen_status, gen_seat

def mk_res():
    """Make a reservation and insert into the USERS table."""
    name = input("Enter your name: ").strip()
    quota = input("Enter which quota you want reservation in: ").strip()
    try:
        trnno = int(input("Enter your train number: "))
    except ValueError:
        print("Invalid train number. Please enter a numeric value.\n")
        welcome()
        return
    berth = input("Enter preferred berth: ").strip().capitalize()
    try:
        age = int(input("Enter your age: "))
    except ValueError:
        print("Invalid age. Please enter a numeric value.\n")
        welcome()
        return
    clas = input("Enter your preferred class: ").strip().upper()

    # Generate reservation details
    pnrno, status, seat = gen()

    # Insert into USERS table
    try:
        db_cursor.execute(
            """
            INSERT INTO USERS (Username, pnrno, Status, Quota, TainNO, SeatNO, BERTH, class, age)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (name, pnrno, status, quota, trnno, seat, berth, clas, age)
        )
        cnx.commit()
        print("Your reservation has been successfully made!!", f"Your PNR No. is {pnrno}\n")
    except mysql.connector.Error as err:
        print(f"Error inserting reservation: {err}\n")
    welcome()

def chk_res(x):
    """Check reservation status using PNR number."""
    try:
        db_cursor.execute(
            """
            SELECT userid, Username, pnrno, Status, Quota, TainNO, SeatNO, BERTH, class, age 
            FROM USERS WHERE pnrno = %s
            """,
            (x,)
        )
        res = db_cursor.fetchone()
        if res:
            column_names = ['UserID', 'Username', 'PNR No', 'Status', 'Quota', 'Train No', 'Seat No', 'Berth', 'Class', 'Age']
            print("Here are your details:")
            for i in range(len(column_names)):
                print(f"{column_names[i]}: {res[i]}")
            print()
        else:
            print("PNR not found! Please check your number.\n")
    except mysql.connector.Error as err:
        print(f"Error fetching reservation: {err}\n")
    welcome()

def cncl_res(x):
    """Cancel a reservation based on PNR number."""
    try:
        # Verify if PNR exists
        db_cursor.execute("SELECT * FROM USERS WHERE pnrno = %s", (x,))
        result = db_cursor.fetchone()
        if not result:
            print("PNR not found! Please check your number.\n")
            welcome()
            return

        # Delete the reservation
        db_cursor.execute("DELETE FROM USERS WHERE pnrno = %s", (x,))
        cnx.commit()
        print(f"Record with PNR No {x} successfully cancelled!!\n")
    except mysql.connector.Error as err:
        print(f"Error deleting reservation: {err}\n")
    welcome()

def fr_res(pnrno):
    """Make a food reservation linked to a PNR number."""
    try:
        # Verify if PNR exists
        db_cursor.execute("SELECT userid FROM USERS WHERE pnrno = %s", (pnrno,))
        result = db_cursor.fetchone()
        if not result:
            print("PNR not found! Please check your number.\n")
            welcome()
            return
        userid = result[0]

        # Collect food reservation details
        meal_type = input("Enter meal type (Breakfast/Lunch/Dinner): ").strip().capitalize()
        food_item = input("Enter food item: ").strip().capitalize()
        try:
            quantity = int(input("Enter quantity: "))
        except ValueError:
            print("Invalid quantity. Please enter a numeric value.\n")
            welcome()
            return

        # Insert into FOOD_RESERVATIONS table
        db_cursor.execute(
            """
            INSERT INTO FOOD_RESERVATIONS (userid, meal_type, food_item, quantity)
            VALUES (%s, %s, %s, %s);
            """,
            (userid, meal_type, food_item, quantity)
        )
        cnx.commit()
        food_res_id = db_cursor.lastrowid
        print(f"Food reservation successfully made!! Your Food Reservation ID is {food_res_id}\n")
    except mysql.connector.Error as err:
        print(f"Error inserting food reservation: {err}\n")
    welcome()

def vf_res(pnrno):
    """View food reservations linked to a PNR number."""
    try:
        # Verify if PNR exists
        db_cursor.execute("SELECT userid FROM USERS WHERE pnrno = %s", (pnrno,))
        result = db_cursor.fetchone()
        if not result:
            print("PNR not found! Please check your number.\n")
            welcome()
            return
        userid = result[0]

        # Fetch food reservations
        db_cursor.execute(
            """
            SELECT food_res_id, meal_type, food_item, quantity, reservation_time
            FROM FOOD_RESERVATIONS
            WHERE userid = %s;
            """,
            (userid,)
        )
        reservations = db_cursor.fetchall()

        if reservations:
            print("Your Food Reservations:")
            print(f"{'ID':<10}{'Meal Type':<15}{'Food Item':<20}{'Quantity':<10}{'Time':<20}")
            print("-" * 75)
            for res in reservations:
                food_res_id, meal_type, food_item, quantity, reservation_time = res
                print(f"{food_res_id:<10}{meal_type:<15}{food_item:<20}{quantity:<10}{reservation_time:<20}")
            print()
        else:
            print("No food reservations found.\n")
    except mysql.connector.Error as err:
        print(f"Error fetching food reservations: {err}\n")
    welcome()

def cf_res(food_res_id):
    """Cancel a food reservation based on Food Reservation ID."""
    try:
        db_cursor.execute("SELECT * FROM FOOD_RESERVATIONS WHERE food_res_id = %s", (food_res_id,))
        result = db_cursor.fetchone()
        if not result:
            print("Food Reservation ID not found! Please check the ID.\n")
            welcome()
            return

        db_cursor.execute("DELETE FROM FOOD_RESERVATIONS WHERE food_res_id = %s", (food_res_id,))
        cnx.commit()
        print(f"Food reservation with ID {food_res_id} successfully cancelled!!\n")
    except mysql.connector.Error as err:
        print(f"Error deleting food reservation: {err}\n")
    welcome()

def login(usnm, passwd):
    """Authenticate user based on credentials in idpass.txt."""
    try:
        print(f"Attempting login for User ID: {usnm}")
        with open("idpass.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                fields = line.strip().split()
                if len(fields) >= 2:
                    file_usnm, file_pwd = fields[0], fields[1]
                    if file_usnm == usnm and file_pwd == passwd:
                        print("Full access granted!!!\n")
                        return True
            print("Invalid username or password.\n")
    except FileNotFoundError:
        print("Credentials file not found. Please ensure 'idpass.txt' exists.\n")
    except Exception as e:
        print(f"An error occurred during login: {e}\n")
    welcome()
welcome()

print("Thank you for tuning with us!!")

cnx.close()
