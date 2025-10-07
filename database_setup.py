import pymysql

def connect_database():
    """Connect to MySQL database"""
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="Samwel@890",
            database='invoice_system',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def add_product(name, quantity, price):
    """Add a product to the database"""
    connection = connect_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO products (name, quantity, price) VALUES (%s, %s, %s)"
                cursor.execute(sql, (name, quantity, price))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
        finally:
            connection.close()

def get_all_products():
    """Retrieve all products from database"""
    connection = connect_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM products")
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
        finally:
            connection.close()