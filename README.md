<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

</div>

<a name="readme-top"></a>

<!-- jango Pro Template -->

<h3 align="center">Django Pro Template</h3>

<p align="center">

<br />
<br />
<a href="https://github.com/GstMirabal/CryptoBot"><strong>Explore the docs »</strong></a>
<br />
·
<a href="https://github.com/GstMirabal/CryptoBot/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
·
<a href="https://github.com/GstMirabal/CryptoBot/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
</p>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
  <a href="#getting-started">Getting Started</a>
  <ul>
    <li>
      <a href="#prerequisites">Prerequisites</a>
      <ul>
        <li><a href="#1-clone-the-repository">Clone the repository</a></li>
        <li><a href="#2-install-virtual-environment-and-dependencies">Install virtual environment and dependencies</a></li>
      </ul>
    </li>
    <li>
      <a href="#initial-configuration">Initial Configuration</a>
      <ul>
        <li><a href="#1-create-environment-variables">Create environment variables</a></li>
        <li><a href="#2-load-environment-variables">Load environment variables</a></li>
        <li><a href="#3-toml-configuration">TOML configuration</a></li>
        <li><a href="#4-database-initialization">Database initialization</a></li>
        <li><a href="#5-creating-a-superuser">Creating a superuser</a></li>
        <li><a href="#6-run-the-server">Run the server</a></li>
        <li><a href="#7-log-file">Log file</a></li>
      </ul>
    </li>
  </ul>
</li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

A production-ready Django project template with a professional, secure, and scalable architecture.

### Built With

* [![Python][Python.png]][Python-url]
* [![Django][Django.gif]][Django-url]
* [![Docker][Docker.gif]][Docker-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To start this project, follow these steps:

### Prerequisites

-   **`pip`**: A package management system for Python.
    
-   **`venv`**: A module for creating isolated Python environments.
    
-   **Docker & Docker Compose**: To run the project's database.



### 1. Clone the Repository

Use `git clone` to download the project files to your local machine, then navigate into the newly created directory:

```bash
git clone https://github.com/GstMirabal/Django-Pro-Template.git
cd Django-Pro-Template
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 2. Install Virtual Environment and Dependencies

1.  Create a virtual environment:
    
    From the project root directory, run:
    
    ```
    python3 -m venv venv
    
    ```
    
2.  **Activate the virtual environment:**
    
    -   On **macOS and Linux**:
        
        ```
        source venv/bin/activate
        
        ```
        
    -   On **Windows**:
        
        ```
        venv\Scripts\activate
        
        ```
        
3.  Install project dependencies:
    
    With the virtual environment activated, install all required packages:
    
    ```
    pip install -r requirements.txt
    
    ```
    

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- INITIAL SETUP -->

## Initial Configuration

### 1. Create Environment Variables
Before running the application, you need to set up your local environment secrets.

1.  Create your .env File:
    
    Navigate to the root of the project. Create a .env file by copying the template:
    
    ```
    cp .env.example .env
    
    ```
    
2.  Generate a Django Secret Key:
    
    Run the following command in your terminal:
    
    ```
    python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

3.  Complete your .env File:

- Navigate to the root of the project and 				copy the content of the `.env.example` file 	located in the `src` folder and paste it into the new `.env` file.

- Paste the secret key you just generated into the DJANGO_SECRET_KEY variable. Also, fill in any other required values, such as POSTGRES_PASSWORD.

	> **Note**: The `SECRET_KEY` is essential for the security of your Django project. Never share this key publicly.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
	
- The `.env` file should contain the following configuration variables needed to run the project:

```bash
# ==============================================================================
#                 ENVIRONMENT VARIABLES TEMPLATE (.env.example)
# ==============================================================================
# This file serves as a template for the required environment variables.
# To set up your local development environment:
#   1. Copy this file and rename it to ".env".
#   2. Fill in the required secret values (e.g., DJANGO_SECRET_KEY, POSTGRES_PASSWORD) in your new ".env" file.
#
# IMPORTANT: This .env.example file IS safe to commit to version control (Git).
# The .env file with your secrets MUST NEVER be committed.
# ==============================================================================


# ==============================================================================
#                       PROJECT & DOCKER COMPOSE SETTINGS
# ==============================================================================
# Base name for the project, used by Docker Compose and documentation.
PROJECT_NAME='YourProjectName'


# ==============================================================================
#                       DJANGO SETTINGS
# ==============================================================================

# DJANGO_SECRET_KEY: Generate a new secret key for your local .env file.
# Command: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DJANGO_SECRET_KEY=

# BASE_DIR: Optional override for the project's root path.
# Leave blank for local development to let settings.py calculate it automatically.
BASE_DIR=

# DEBUG: Enables Django's debug mode. Should be "False" in production.
DEBUG="True"

# ALLOWED_HOSTS: Comma-separated list of hosts allowed for development.
# In production, this should be your actual domain(s) (e.g., 'api.cryptobot.com').
ALLOWED_HOSTS="localhost,127.0.0.1"

# CORS_ALLOWED_ORIGINS: Comma-separated list of frontend origins allowed in development.
# In production, this should be your frontend's domain (e.g., 'https://app.cryptobot.com').
CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"


# ==============================================================================
#                       POSTGRESQL DATABASE SETTINGS
# ==============================================================================
# These variables are used by Docker Compose to BUILD the database and by
# Django (via config.toml) to CONNECT to it.

# Choose a name for your local development database.
POSTGRES_DB=your_db_name

# Choose a username for your local database.
POSTGRES_USER=your_db_user

# Choose a secure password for your local database. This is a secret.
# IMPORTANT: If your password contains special characters like !, @, #, etc.,
# they MUST be URL-encoded (e.g., '!' becomes '%21').
POSTGRES_PASSWORD=

# Host where the database is running (for local Docker, this is always 'localhost').
POSTGRES_HOST="localhost"

# Standard PostgreSQL port.
POSTGRES_PORT="5432"


# ==============================================================================
#                       PROJECT LOGGING
# ==============================================================================
# Directory where log files will be stored.
PROJECT_LOGS_DIR="logs"


# ==============================================================================
#                       EMAIL SETTINGS
# ==============================================================================
# Not used in development (DEBUG=True) because the console backend is active.
# In production, these must be filled with real SMTP credentials.
EMAIL_HOST=""
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
```

### 1.1 Environment Variable Descriptions

This section explains the required environment variables for the CryptoBot project, as defined in the `.env.example` file.

#### Project Metadata

-   `PROJECT_NAME`: The project's official name for logs and documentation.

#### Django Settings

-   `DJANGO_SECRET_KEY`: The cryptographic signing key. **Must be kept secret and unique for production.**
    
-   `DEBUG`: Toggles debug mode. **Must be `False` in production.**
    
-   `ALLOWED_HOSTS`: A comma-separated list of allowed hostnames.
    
-   `CORS_ALLOWED_ORIGINS`: A comma-separated list of permitted frontend origins for API requests.
    
#### PostgreSQL Database Settings

-   `POSTGRES_DB`: The name of the database.
    
-   `POSTGRES_USER`: Username for the database connection.
    
-   `POSTGRES_PASSWORD`: Password for the database user. **This is a secret and must be set in your `.env` file.**
    
-   `POSTGRES_HOST`: The database server host (e.g., `localhost`).
    
-   `POSTGRES_PORT`: The database server port (default: `5432`).
    
#### Project Logging

-   `PROJECT_LOGS_DIR`: The directory where log files are stored.
    
#### Email Settings

-   `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Configuration for the production SMTP server (not used when `DEBUG=True`).

> **Note**: `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` are crucial for the application to run. In production, all secret variables must be set.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 2. Load Environment Variables

To load the environment variables from the `.env` file, follow these steps:

1. Ensure your virtual environment is activated:

   **For macOS and Linux:**
   ```bash
   . venv/bin/activate
   ```

   **For Windows:**
   ```bash
   venv\Scripts\activate
   ```

2. Load environment variables from the `.env` file:

   **For macOS and Linux:**
   ```bash
   export $(grep -v '^#' .env | xargs)
   ```

   **For Windows:**
   ```powershell
   foreach ($line in Get-Content .env) { 
       if ($line -match "^\s*[^#\s]") { 
           $name, $value = $line -split "=", 2 
           [System.Environment]::SetEnvironmentVariable($name, $value) 
       } 
   }
   ```

This will load the environment variables from your `.env` file into your shell session, ensuring that they are available for your project.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### 3. TOML Configuration

The central configuration for the Django application is located at `backend/config.toml`. This file acts as a template, mapping variables from the `.env` file to the required settings.

The following parameters are configured by default to start the project in a local development environment:

```
# ==============================================================================
#                       DJANGO SETTINGS
# ==============================================================================
[django_settings]

# --- Secret key for Django's security. Its value is defined in the .env file ---
# It must be unique for each environment and should never be shared.
DJANGO_SECRET_KEY = "$DJANGO_SECRET_KEY"

# --- Project base path. Optional, used to override the path in environments like Docker ---
BASE_DIR = "$BASE_DIR"

# --- Enables/disables debug mode. Must be 'True' for development and 'False' for production ---
DEBUG = "$DEBUG"

# --- Comma-separated list of allowed domains for serving the application ---
# Example in production: "api.cryptobot.com,www.cryptobot.com"
ALLOWED_HOSTS = "$ALLOWED_HOSTS"

# --- Comma-separated list of allowed frontend origins to access the API ---
# Example in production: "https://app.yourname.com"
CORS_ALLOWED_ORIGINS = "$CORS_ALLOWED_ORIGINS"

# ==============================================================================
#                       DATABASE COMPONENTS
# ==============================================================================
# This section defines the individual components of the database connection.
# The values are substituted from the .env file.
# The final DATABASE_URL is then assembled within the settings.py file for maximum control.
[DB]

# --- Name of the database to be created by Docker and used by Django ---
POSTGRES_DB = "$POSTGRES_DB"

# --- Username for the database connection ---
POSTGRES_USER = "$POSTGRES_USER"

# --- Password for the database user. The actual value is a secret in .env ---
# IMPORTANT: Special characters in the password must be URL-encoded in the .env file.
POSTGRES_PASSWORD = "$POSTGRES_PASSWORD"

# --- Hostname or IP address of the database server ---
# For the local Docker setup, this is always 'localhost'.
POSTGRES_HOST = "$POSTGRES_HOST"

# --- Port on which the database server is listening ---
# The standard port for PostgreSQL is 5432.
POSTGRES_PORT = "$POSTGRES_PORT"
```

-   Remember to adjust values like `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` in your `.env` file when moving to a production environment.
    
-   The file also contains sections for email (`[email_settings]`) and logging (`[project_logging]`) configuration, which are also populated from the `.env` file.
    

**Note**: The `config.toml` file is designed to be version-controlled (committed to Git) and contains no secrets. It uses the `$VARIABLE_NAME` syntax to dynamically load sensitive values from the `.env` file. Ensure your `.env` is correctly filled out before starting the project.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DATABASE INITIALIZATION -->
### 4. Database Initialization

To set up the database and apply the initial application schema, follow the detailed steps below. This process uses Docker to run the PostgreSQL database and Django commands to create the necessary tables.

1. Start the Docker Desktop ApplicationBefore running any commands, ensure that the Docker Desktop application is open and running on your system. You should see the Docker whale icon in your system's menu bar or tray with a green indicator, which signifies that the Docker daemon is active and ready.

2. Launch the Database ContainerFrom the project's root directory (where the docker-compose.yml file is located), run the following command in your terminal:

```
docker-compose up -d
````

- What this command does: Docker Compose reads the docker-compose.yml and .env files. On its first run, it downloads the official PostgreSQL image, creates a container, and automatically initializes the database (POSTGRES_DB), user (POSTGRES_USER), and password (POSTGRES_PASSWORD) that you defined in your .env file. The -d flag runs the container in the background (detached mode).

Suggestion 1: Add a verification step. This gives the user immediate feedback that the container is running correctly before they proceed.

2.1. Verify the Container is Running (Optional)To confirm that the database container has started successfully,

```
 docker ps
```

You should see a container named cryptobot_db (or the name you configured) in the list with the status Up.

3. Apply Database MigrationsOnce the database container is running, the next step is to create the internal table structure (the schema) that the Django application requires.Navigate to the backend directory:

```
cd backend
````

> **CRITICAL WARNING: Custom User Model**
>
> This template intentionally does not include a custom user model to provide maximum flexibility. Before you run `python manage.py migrate` for the first time, you **MUST** create your own user app and set the `AUTH_USER_MODEL` in `settings.py`.
>
> Failure to do so will lock your project into Django's default user model, which is extremely difficult to change later.
>
> ```bash
> # Example of creating a user app
> cd backend
> python manage.py startapp users
> ```
> Then, create your model in `users/models.py` and add `AUTH_USER_MODEL = 'users.User'` to `settings.py`.

Run the migration commands in sequence:
```
# This command creates the migration files (the "blueprints") based on your models
python manage.py makemigrations

# This command applies the migrations to create the tables in the database
python manage.py migrate

````

Suggestion 2: Clarify the expected output. This helps the user confirm that the migrations were applied successfully.

- Expected Output: After running migrate, you will see a list of all migrations being applied, with an OK next to each one. This confirms that the tables have been created in your PostgreSQL database.

- Suggestion 3: Add the logical next step. After creating the tables, the user will almost always need a superuser to access the Django admin.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 5. Creating a Superuser
To access the admin interface, you need to create a superuser account. Follow these steps:

1. Open a terminal and navigate to your project directory.
2. Run the following command:
   ```bash
   python manage.py createsuperuser
   ```
3. Follow the prompts to enter your desired username, email, and password.

This section now includes instructions on how to create a superuser for accessing the admin interface, improving the overall completeness of the documentation.

Once created, you can log in to the admin interface at [http://0.0.0.0:8000/admin](http://0.0.0.0:8000/admin) using the superuser credentials.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- RUN THE SERVER -->
### 6. Run the Server

Finally, run the following command to start the application's local server:

1. Ensure your virtual environment is activated:
   ```bash
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. Start the server:
   ```bash
   python manage.py runserver
   ```

The server should be running at `http://0.0.0.0:8000` or the port specified in your configuration.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LOG FILE -->
### 7. Log file

A `.log` file will be generated the first time you start the server to save all the errors and warnings encountered.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
## Usage

Once the server is running, you have successfully completed the most critical phase of the project: the setup of a robust and professional infrastructure.

The project is now in a state of a professional "blank canvas". You have at your disposal:

-   A running development server connected to a **PostgreSQL** database.
-   A **secure and production-ready configuration** (`settings.py`) that handles secrets, security headers, and logging.
-   A **modular application structure** (`apps/`) ready to house your business logic.
-   A **complete testing framework** ready to verify your code.

From this point on, you have a solid foundation to start building the application's core logic. This includes, but is not limited to:

-   Defining your data models in the different `models.py` files.
-   Creating your API endpoints in the `views.py` and `urls.py` files.
-   Implementing complex business logic and services.
-   Connecting to external services and APIs.

The foundation is complete. It's time to start building.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Gustavo Mirabal Suarez 
gst.mirabal@gmail.com

- LinkedIn: [@Gustavo-Mirabal](https://www.linkedin.com/in/gustavo-adolfo-mirabal-suarez-ab2738127)
- GitHub: [@GstMirabal](https://github.com/GstMirabal)
- Twitter: [@GstMirabal](https://x.com/gst_mirabal)

Project Link: [https://github.com/GstMirabal/CryptoBot](https://github.com/GstMirabal/CryptoBot)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/GstMirabal/CryptoBot.svg?style=for-the-badge
[contributors-url]: https://github.com/GstMirabal/CryptoBot/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/GstMirabal/CryptoBot.svg?style=for-the-badge
[forks-url]: https://github.com/GstMirabal/CryptoBot/network/members
[stars-shield]: https://img.shields.io/github/stars/GstMirabal/CryptoBot.svg?style=for-the-badge
[stars-url]: https://github.com/GstMirabal/CryptoBot/stargazers
[issues-shield]: https://img.shields.io/github/issues/GstMirabal/CryptoBot.svg?style=for-the-badge
[issues-url]: https://github.com/GstMirabal/CryptoBot/issues
[license-shield]: https://img.shields.io/github/license/GstMirabal/CryptoBot.svg?style=for-the-badge
[license-url]: https://github.com/GstMirabal/CryptoBot/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/gstmirabal
[Python.png]: https://www.python.org/static/community_logos/python-powered-w-100x40.png
[Python-url]: https://www.python.org/
[Django.gif]: https://www.djangoproject.com/m/img/badges/djangomade124x25.gif
[Django-url]: https://www.djangoproject.com/
[Docker.gif]: https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
