from dbConnection import create_connection, close_connection
from mysql.connector import Error
from werkzeug.security import check_password_hash

def create_user(username, email, password):
    """
    Insert a new user into the database.
    """
    insert_query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s);
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(insert_query, (username, email, password))
            connection.commit()
            print("User created successfully")
        except Error as e:
            print(f"Error inserting user: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def get_user_by_id(user_id):
    """
    Retrieve a user by their ID.
    """
    select_query = "SELECT id, username, email, created_at FROM users WHERE id = %s;"
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(select_query, (user_id,))
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Error retrieving user: {e}")
            return None
        finally:
            cursor.close()
            close_connection(connection)

def update_user(user_id, username=None, email=None, password=None):
    """
    Update user details.
    """
    update_query = "UPDATE users SET {} WHERE id = %s;"
    updates = []
    params = []

    if username:
        updates.append("username = %s")
        params.append(username)
    if email:
        updates.append("email = %s")
        params.append(email)
    if password:
        updates.append("password = %s")
        params.append(password)

    if not updates:
        print("No updates provided")
        return

    query = update_query.format(", ".join(updates))
    params.append(user_id)

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query, tuple(params))
            connection.commit()
            print("User updated successfully")
        except Error as e:
            print(f"Error updating user: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def delete_user(user_id):
    """
    Delete a user by their ID.
    """
    delete_query = "DELETE FROM users WHERE id = %s;"
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(delete_query, (user_id,))
            connection.commit()
            print("User deleted successfully")
        except Error as e:
            print(f"Error deleting user: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def get_user_by_credentials(identifier, password):
    """
    Retrieve a user by their username or email and validate the password.

    :param identifier: The username or email of the user.
    :param password: The plaintext password provided by the user.
    :return: The user details if found and authenticated, else None.
    """
    select_query = """
    SELECT id, username, email, password 
    FROM users 
    WHERE username = %s OR email = %s;
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(select_query, (identifier, identifier))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                return user  # Return user details if the password is correct
            else:
                return None  # Authentication failed
        except Error as e:
            print(f"Error during user authentication: {e}")
            return None
        finally:
            cursor.close()
            close_connection(connection)
