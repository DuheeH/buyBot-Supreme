# buyBot-Supreme

#### Video Demo:  https://youtu.be/XXokoHQCT0E

#### Description: Supreme Merchandise BuyBOT

buyBot-Supreme is a web application that allows users to automate the add to cart and checkout of online Supreme merchandise by grabbing the URL of the merchandise.

#### buyBot-Supreme Key Languages/Libraries: 

- **Python**: Flask, Selenium
- **sqlite3**
- **bash**
- **Jinja**
- **JavaScript**
- **HTML**
- **CSS**

## Design Choices:

### Backend: 

#### Framework:
- **Node.js vs Flask**: I decided to use Flask as I preferred to use Python instead of JavaScript and Python's available libraries such as Selenium.

#### Database:
- **sqlite3 vs PostgreSQL**: I decided to implement sqlite3 instead of PostgreSQL due to time constraints and ease of implementation using the SQL function in the CS50 library. More importantly, sqlite3 was more appropriate considering the scale and project requirements.

### Frontend:

- **React.js vs (HTML,CSS,JavaScript)**: Similarly to the design considerations for databases, the scale and project requirements led me to not using React.js.
- **Asynchronous Requests**: Although data fetching was not implemented, a feature where users can search through transactions using filters would be useful.

### Deployment:

- **Github Pages**: Provides the ability to host static websites which made it not applicable for this project.
- **Heroku**: Was considered; however, free web hosting was no longer an option on the platform. Thus, the web application was hosted locally using Flask.

### Version Control:

- **GitHub**: GitHub was the obvious choice for version control which was used for this project. While working on a local repository, I found myself repeatedly removing unwanted files and folders from my GitHub repository which led to learning about **rebase** and **.gitignore**.
  
- **venv**: While looking for way to have a clean and isolated workspace for my project and avoid dependency mishaps down the line, I found out about virtual environements the venv command in python. I worked within a virtual environment during the project and generated a requirements.txt file when complete.


## Folders/Files:

- **app.py**: The Python file that contains the routing and functions required to make the application functional.
  - **Routes**: 
    - **/**: Displays transactions to date and redirect to /buy if there are no transactions.
    - **/login**: Clears session and validates username and password combination.
    - **/register**: Allows users to register and validates username and password combination.
    - **/profile**: Updates profiles table upon user input of all fields.
    - **/buy**: Adds each URL/item to cart and automates checkout using information provided in /profiles. Redirects to / upon successful transaction.
    - **/changepass**: Allows users to change password.
    - **/logout**: Clears session and redirects to /.

- **buybot.db**: A sqlite3 database containing three tables: users, profiles, and transactions.
  - **.schema**:
    ```sql
    CREATE TABLE profiles (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            firstName TEXT,
            lastName TEXT,
            email TEXT,
            address TEXT,
            address2 TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            phone TEXT,
            ccName TEXT,
            ccNumber TEXT,
            ccExpiration TEXT,
            ccSecurity TEXT,
            sameAddress TEXT DEFAULT 'on',
            FOREIGN KEY (user_id) REFERENCES users(id)
            );

    CREATE TABLE transactions
            (id INTEGER PRIMARY KEY,
            url TEXT,
            price FLOAT,
            datetime DATETIME,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id));

    CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, hash TEXT);
    ```

- **helpers.py**: A Python file that contains three helper functions: login_required(), getTable(), and randomWait().

- **requirements.txt**: A text file that includes the packages and libraries and their respective version numbers that were used for this project. Automatically generated while in a virtual environment.

- **.gitignore**: Contains files and folders that were not to be included in the GitHub Repository.

- **static/**:
  - **dynamic_url_input.js**: JavaScript to dynamically generate URL input boxes on buy.html.
  - **favicon.png**: Supreme image used at the header of the website.
  - **styles.css**: Includes CSS for text formatting and website background image.

- **templates/**: Contains HTML files to display the various pages of the web application.
