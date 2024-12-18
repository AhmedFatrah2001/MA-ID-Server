
## Overview

This server application is designed to handle ID scanning, text extraction, and user operations. It includes the following components:

- **dbConnection**: Initializes the connection to the MySQL database and creates the `users` table.
- **text_extractor**: Extracts text from ID cards using OCR.
- **zone_detector**: Uses a custom YOLOv8 model to detect zones on ID cards. The model weights should be placed in the `weights` folder.
- **userOperations**: Defines user operations and CRUD functionalities.

## Setup

### Prerequisites

- Python 3.x
- MySQL
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/AhmedFatrah2001/MA-ID-Server
    cd MA-ID-Server
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the `.env` file with your database information:
    ```env
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    ```

5. Initialize the database:
    ```sh
    python dbConnection.py
    ```

## Usage

1. Run the server:
    ```sh
    python server.py
    ```

2. The server will start and be ready to handle requests for ID scanning, text extraction, and user operations.

## Components

### dbConnection

- Initializes the MySQL database connection.
- Creates the `users` table if it does not exist.

### text_extractor

- Uses OCR to extract text from ID cards.

### zone_detector

- Utilizes a custom YOLOv8 model to detect zones on ID cards.
- Ensure the model weights are placed in the `weights` folder.

### userOperations

- Defines CRUD operations for user management.

## Contributing

Feel free to submit issues or pull requests if you have any improvements or bug fixes.

