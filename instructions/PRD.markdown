Okay, here's a breakdown of the tasks and corresponding prompts, designed to guide a developer step-by-step through the application development using the specified tech stack and requirements. I've included prompts for project setup, backend, frontend, and integration, aiming for clarity and completeness.

**I. Project Setup and Initialization (Backend - Django)**

**Task 1: Project Initialization and Environment Setup**

1.  **Prompt 1:** "Create a new Django project named `jira_integration_app` using the `django-admin startproject` command.  Explain the structure of the created project, particularly the roles of `manage.py`, the project-level `urls.py`, and the `settings.py` file."

2.  **Prompt 2:** "Create a new Django app named `core` within the `jira_integration_app` project using `python manage.py startapp core`. Explain the purpose of the `core` app and its directory structure (models.py, views.py, admin.py, apps.py, etc.)."

3.  **Prompt 3:** "Create a virtual environment using `venv` (or your preferred method) and activate it.  Explain why using a virtual environment is essential for Python development."

4.  **Prompt 4:** "Install the required Python packages: `Django`, `djangorestframework`, `python-dotenv`,`python-decouple`, `pyjwt`, `openai`, `jira`, `requests`. Save these dependencies in a `requirements.txt` file using `pip freeze > requirements.txt`."

5.  **Prompt 5:** "Configure Django settings in `settings.py`.  Specifically:
    *   Set `DEBUG = True` (for development).
    *   Add `'rest_framework'` and `'core'` to the `INSTALLED_APPS` list.
    *   Add `rest_framework.authentication.JSONWebTokenAuthentication` to the list DEFAULT_AUTHENTICATION_CLASSES in REST_FRAMEWORK
    *   Configure the database to use SQLite3 (`DATABASES` setting). Provide the default SQLite configuration.
    *   Configure static file settings (`STATIC_URL`, `STATIC_ROOT`)."

6.  **Prompt 6:** "Create a `.env` file in the project root to store sensitive information.  Add the following variables to the `.env` file: `DJANGO_SECRET_KEY` (generate a strong secret key), `OPENAI_API_KEY`, `JIRA_API_TOKEN`, `JIRA_SERVER_URL`, `JIRA_USER_EMAIL`.  Demonstrate how to load these variables into `settings.py` using `python-dotenv`."

7. **Prompt 7:** "Create a superuser account in the database using `python manage.py createsuperuser`. This superuser account should have 'is_staff' and 'is_superuser' permissions. And this is the only user who can add/edit users and configure JIRA user ID."

**Task 2: User Model and Authentication (JWT)**

1.  **Prompt 8:** "Extend the default Django User model with a custom `UserProfile` model (in `core/models.py`).  Add a `jira_user_id` field (CharField, max_length=255, blank=True, null=True) to the `UserProfile` model to store the user's Jira ID.  Create a one-to-one relationship between `UserProfile` and the built-in `User` model."

2.  **Prompt 9:** "Implement JWT authentication using `djangorestframework-simplejwt`.  Configure JWT settings in `settings.py` (e.g., `SIMPLE_JWT`). Explain the purpose of `ACCESS_TOKEN_LIFETIME` and `REFRESH_TOKEN_LIFETIME`."

3.  **Prompt 10:** "Create a Django REST Framework (DRF) view (`core/views.py`) for user login (`LoginView`).  This view should:
    *   Accept a username and password.
    *   Authenticate the user using Django's built-in authentication.
    *   Generate a JWT token pair (access and refresh) using `TokenObtainPairSerializer` if authentication is successful.
    *   Return the token pair in the response."

4.  **Prompt 11:** "Create a DRF view for token refresh (`TokenRefreshView`).  This view should:
    *   Accept a refresh token.
    *   Validate the refresh token.
    *   Generate a new access token if the refresh token is valid.
    *   Return the new access token in the response."

5.  **Prompt 12:** "Configure URL patterns (`core/urls.py` and project-level `urls.py`) for the login and token refresh views.  Use paths like `/api/token/` and `/api/token/refresh/`."

6. **Prompt 13**: "Add the Jira User ID field to the Django admin for the `UserProfile` model. This should include the 'User' field for selection, which displays only users where is_staff=True. Also, create a custom model admin class that displays a list of all `UserProfiles` and their corresponding Jira User IDs."

**Task 3: Jira Integration (jira_integration.py)**

1.  **Prompt 14:** "Create a file `core/jira_integration.py`. This file will house all Jira interaction logic."

2.  **Prompt 15:** "Inside `jira_integration.py`, create a class named `JiraClient`.  The constructor (`__init__`) should:
    *   Take `server_url`, `user_email`, and `api_token` as arguments (load these from the environment variables).
    *   Initialize a Jira client instance using the `jira` library (or use `requests` directly for REST API calls).
    *   Include error handling (try-except blocks) to catch potential authentication errors."

3.  **Prompt 16:** "In `JiraClient`, create a method `get_user_issues(jira_user_id, status=None)`.  This method should:
    *   Take a `jira_user_id` and an optional `status` as arguments.
    *   Construct a JQL query to fetch issues assigned to the given `jira_user_id`.  If `status` is provided, filter by that status as well.
    *   Use the Jira client to execute the JQL query.
    *   Return a list of issue objects (or dictionaries containing relevant issue data like key, summary, status, description)."
    *   Handle potential errors (e.g., invalid JQL, user not found).

4.  **Prompt 17:** "In `JiraClient`, create a method `add_comment_to_issue(issue_key, comment, mentions=None)`. This method should:
    *   Take an `issue_key`, a `comment` string, and an optional list of `mentions` (Jira user IDs) as arguments.
    *   Format the comment string to include @mentions (if provided) in the Jira comment format (e.g., `[~user_id]`).
    *   Use the Jira client to add the comment to the specified issue.
    *   Handle potential errors (e.g., issue not found, insufficient permissions)."

5.  **Prompt 18:** "In `JiraClient`, create a method `update_issue_status(issue_key, new_status)`. This method should:
    *   Take an `issue_key` and a `new_status` string as arguments.
    *   Fetch the issue using the Jira client.
    *   Get available transitions for the issue.
    *   Check if the `new_status` is a valid transition.
    *   If valid, transition the issue to the `new_status`.
    *   If invalid, return an error message indicating the valid transitions.
    *   Handle potential errors (e.g., issue not found, transition not allowed)."

6.  **Prompt 19:** "In `JiraClient`, create a method `create_issue(project_key, summary, description, issue_type, assignee=None)`. This method should:
     *   Accept mandatory fields: `project_key`, `summary`, `description`, and `issue_type`.
     *   Optionally accept `assignee` (Jira user ID).
     *   Validate that mandatory fields are not empty.
     *   Create a new issue in Jira using the provided information.
     *   Return the newly created issue key.
     *   Handle potential errors (e.g., invalid project key, insufficient permissions)."

7.  **Prompt 20:** "In `JiraClient`, create a method `get_all_statuses()`. This method will fetch all available status in Jira."

8. **Prompt 21:** "In `JiraClient`, create a method `search_users(query)`. This method will perform user search based on query, if query is empty or null, return all users"

**Task 4: OpenAI Integration (openai_integration.py)**

1.  **Prompt 22:** "Create a file `core/openai_integration.py`. This file will handle all interactions with the OpenAI API."

2.  **Prompt 23:** "Inside `openai_integration.py`, create a class named `OpenAIClient`. The constructor (`__init__`) should:
    *   Take the `api_key` as an argument (load from environment variables).
    *   Initialize an OpenAI client instance using the `openai` library."

3. **Prompt 24:** "Define OpenAI Function Calling Specifications: Create a list of dictionaries, each representing a function call specification for the OpenAI API. Include specifications for *each* of the methods in `JiraClient` (`get_user_issues`, `add_comment_to_issue`, `update_issue_status`, `create_issue`, `get_all_statuses`,`search_users`).  Each dictionary should include:
    *   `name`: The name of the JiraClient method (e.g., "get_user_issues").
    *   `description`: A clear description of what the function does.
    *   `parameters`: A JSON schema describing the parameters the function accepts (type, description, enum values if applicable).  Use the correct parameter types (string, integer, array, etc.).  Refer to OpenAI's documentation for the correct format."

4.  **Prompt 25:** "In `OpenAIClient`, create a method `get_intent_and_parameters(user_message, conversation_history)`.  This method should:
    *   Take the user's `user_message` (string) and a `conversation_history` (list of messages) as input.
    *   Construct a prompt for the OpenAI API that includes:
        *   A system message setting the context (e.g., "You are a helpful assistant that interacts with Jira.").
        *   The conversation history (previous messages between the user and the AI).
        *   The current user message.
        *   The function call specifications (from Prompt 24).
    *   Call the OpenAI ChatCompletion API with the constructed prompt, specifying `function_call="auto"`.
    *   Parse the API response. If the model chooses to call a function:
        *   Extract the function name and arguments.
        *   Return the function name and arguments as a dictionary (e.g., `{'function_name': 'get_user_issues', 'arguments': {'jira_user_id': 'abc'}}`).
    *   If the model does not choose to call a function, return the model's text response.
    *   Handle potential errors (e.g., API errors, invalid JSON).

5. **Prompt 26:** "In `OpenAIClient`, create a method `summarize_text(text, max_tokens=100)`. This method will take a string of `text` and use OpenAI to generate a summary with a maximum length of `max_tokens`."

**Task 5: Backend Views and API Endpoints**

1.  **Prompt 27:** "In `core/views.py`, create a DRF APIView named `ChatView`. This view will handle the main chat interaction.  It should:
    *   Use JWT authentication (`authentication_classes = [JSONWebTokenAuthentication]`).
    *   Require authentication (`permission_classes = [IsAuthenticated]`).
    *   Implement a `post` method to handle incoming user messages."

2.  **Prompt 28:** "Inside the `post` method of `ChatView`:
    *   Retrieve the user's message from the request data.
    *   Retrieve the user's `UserProfile` (including the `jira_user_id`).
    *   Get the conversation history (you'll need to implement a mechanism to store/retrieve this - see Task 6).
    *   Create instances of `OpenAIClient` and `JiraClient`.
    *   Call `openai_client.get_intent_and_parameters()` to determine the user's intent.

3.  **Prompt 29:** "If `get_intent_and_parameters()` returns a function call:
    *   Use a series of `if/elif` statements (or a dictionary mapping function names to methods) to call the appropriate method on the `JiraClient` instance.  Pass the arguments extracted from the OpenAI response.
        *   For example, if the function name is `get_user_issues`, call `jira_client.get_user_issues(**arguments)`.
    *   Handle potential errors from the `JiraClient` methods (e.g., issue not found).  Return appropriate error messages to the user.
    *   Construct a response message to the user based on the result of the Jira operation (e.g., "I've fetched your issues," or "I've added a comment to ABC-123").

4.  **Prompt 30:** "If `get_intent_and_parameters()` returns a text response (no function call):
    *   Return the OpenAI model's text response directly to the user.

5.  **Prompt 31:** "In `core/views.py`, create a DRF APIView named `InitialGreetingView`.  This view should:
        *   Use JWT authentication.
        *   Require authentication.
        *   Implement a `get` method.
        * On get request, it should return default AI Greeting message, like : "Hi [User]! Here are the top 3 things I can help you with today:\n\n1. Update the status of your Jira tickets.\n2. Get a summary of your assigned tickets.\n3. Add comments to your tickets.\n\nWhat would you like to do?"

6.  **Prompt 32:** "Configure URL patterns in `core/urls.py` and project-level `urls.py` for `ChatView` and `InitialGreetingView`.  Use paths like `/api/chat/` and `/api/greeting/`."

**Task 6: Conversation History**

1.  **Prompt 33:** "Create a model named `Conversation` in `core/models.py`.  This model should store conversation history. Include the following fields:
    *   `user` (ForeignKey to the User model)
    *   `message` (TextField) - The content of the message.
    *   `timestamp` (DateTimeField, auto_now_add=True)
    *   `is_user_message` (BooleanField) - True if the message is from the user, False if it's from the AI.

2.  **Prompt 34:** "Modify the `ChatView` in `core/views.py`:
    *   Before calling OpenAI, retrieve the last N messages (e.g., 10) from the `Conversation` model for the current user, ordered by timestamp. This is your `conversation_history`.
    *   After receiving a response from OpenAI (either a function call result or a text response), create a new `Conversation` instance for *both* the user's message and the AI's response. Save these to the database.

**Task 7: Daily Scrum Updates**

1.  **Prompt 35:** "Create a model named `ScrumUpdate` in `core/models.py`. Include the following fields:
    *   `user` (ForeignKey to the User model)
    *   `date` (DateField)
    *   `updates` (TextField) - The scrum updates.

2.  **Prompt 36:** "In `core/views.py`, modify the `ChatView`:
    *   At the beginning of the `post` method (before processing the user's message), check if a `ScrumUpdate` exists for the current user and date.
    *   If *no* `ScrumUpdate` exists:
        *   Prepend a message to the `conversation_history` asking for the user's scrum update (e.g., "Good morning! Can you please provide your scrum updates for today?").  This ensures the AI asks for the update.
        * Set up conversation flow in a way that, it asks for 3 specific things for daily updates: 1. What did you do yesterday?, 2. What will you do today? 3. Is there any blocker?
        * After capturing all 3 responses, create a `ScrumUpdate` and save, tag all issues in JIRA with the updates and user name by internally calling JIRA integration methods."
    *   If a `ScrumUpdate` *does* exist, proceed with processing the user's message as before.

3.  **Prompt 37:** "Create helper functions (either in `core/views.py` or a separate utility file) to:
    *   Check if a `ScrumUpdate` exists for a given user and date.
    *   Create a new `ScrumUpdate`.

**Task 8: Error Handling and Notifications**

1.  **Prompt 38:** "In `core/jira_integration.py` and `core/openai_integration.py`, add comprehensive error handling:
    *   Use `try-except` blocks around all API calls (Jira and OpenAI).
    *   Catch specific exceptions (e.g., `requests.exceptions.RequestException`, `openai.error.OpenAIError`, `jira.exceptions.JIRAError`).
    *   Log errors using the Python `logging` module. Include informative error messages and relevant context (user, issue key, etc.).
    *   Return user-friendly error messages to the `ChatView` (e.g., "Could not update ticket status. Please try again later.").

2.  **Prompt 39:** "Implement retry logic for transient API failures (e.g., network timeouts). Use a library like `requests`' `Retry` mechanism or implement a simple retry loop with exponential backoff."

3.  **Prompt 40:** "Create a mechanism to handle Jira API rate limits. This could involve:
    *   Checking the response headers for rate limit information.
    *   Using a queue (e.g., Celery with Redis) to schedule Jira API requests.
    *   Implementing a simple delay mechanism if rate limits are hit.

**II. Frontend Development (React, Vite, Javascript, Tailwind CSS)**

**Task 9: Frontend Project Setup**

1.  **Prompt 41:** "Create a new React project using Vite: `npm create vite@latest frontend --template react`.  Navigate into the `frontend` directory."

2.  **Prompt 42:** "Install the necessary frontend dependencies: `axios` (for API requests), `react-router-dom` (for routing), `tailwindcss` (for styling).  Use `npm install <package_name>`."

3.  **Prompt 43:** "Initialize Tailwind CSS: `npx tailwindcss init -p`.  This creates `tailwind.config.js` and `postcss.config.js`."

4.  **Prompt 44:** "Configure Tailwind CSS in `tailwind.config.js` to include your project's files:
    ```javascript
    module.exports = {
      content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
      ],
      // ...
    }
    ```"

5.  **Prompt 45:** "Add the Tailwind directives to your main CSS file (e.g., `src/index.css` or `src/App.css`):
    ```css
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
    ```"

6.  **Prompt 46:** "Create basic directory structure inside `src`: `components`, `pages`, `services`, `context`."

**Task 10: User Authentication (Frontend)**

1.  **Prompt 47:** "Create a context (`src/context/AuthContext.jsx`) to manage user authentication state.  This context should:
    *   Store the JWT access and refresh tokens.
    *   Provide functions for:
        *   Logging in (making a request to the backend's `/api/token/` endpoint).
        *   Logging out (removing tokens from local storage).
        *   Refreshing the access token (making a request to `/api/token/refresh/`).
        *   Checking if the user is authenticated (checking if a valid access token exists).

2.  **Prompt 48:** "Use `localStorage` to persist the tokens across sessions."

3.  **Prompt 49:** "Create a `LoginPage` component (`src/pages/LoginPage.jsx`). This component should:
    *   Display a form with username and password fields.
    *   Use the `AuthContext` to call the login function when the form is submitted.
    *   Handle potential errors (e.g., invalid credentials).
    *   Redirect the user to the chat page upon successful login."

4.  **Prompt 50:** "Create a `PrivateRoute` component (`src/components/PrivateRoute.jsx`). This component should:
    *   Wrap routes that require authentication.
    *   Check if the user is authenticated using the `AuthContext`.
    *   If authenticated, render the wrapped component.
    *   If not authenticated, redirect to the login page."

**Task 11: Chat Interface**

1.  **Prompt 51:** "Create a `ChatPage` component (`src/pages/ChatPage.jsx`). This component should:
    *   Be wrapped in a `PrivateRoute`.
    *   Display a chat interface with:
        *   An area to display messages (a scrollable list).
        *   An input field for the user to type messages.
        *   A button to send messages.

2.  **Prompt 52:** "Use `useState` to manage the list of messages and the current user input."

3.  **Prompt 53:** "Create a `Message` component (`src/components/Message.jsx`) to display individual messages.  This component should:
    *   Take a message object as a prop (with properties like `text`, `isUserMessage`, `timestamp`).
    *   Style the message differently depending on whether it's from the user or the AI.

4.  **Prompt 54:** "On initial load of `ChatPage`, make a request to get AI Greeting default message from backend API endpoint `/api/greeting/`

5.  **Prompt 55:** "When the user sends a message (by typing in the input field and clicking the send button):
    *   Add the user's message to the local message list.
    *   Make a POST request to the backend's `/api/chat/` endpoint, sending the user's message and a unique identifier for the current chat session (if needed).
    *   Use `axios` for the API request.

6.  **Prompt 56:** "When a response is received from the backend:
    *   Add the AI's response to the local message list.

7.  **Prompt 57:** "Implement error handling for API requests (e.g., display an error message if the backend is unavailable).

**Task 12: API Service**

1.  **Prompt 58:** "Create a service file (`src/services/api.js`) to encapsulate API calls.  This file should contain functions for:
    *   Sending a chat message (`sendMessage(message)`).
    *   Fetching AI Greeting message (`getGreeting()`).
    *   Include the JWT access token in the `Authorization` header for authenticated requests (using `axios` interceptors is a good approach).
    *   Handle token refresh automatically if the access token is expired (using `axios` interceptors).

**III. Dockerization**

**Task 13: Docker Compose**

1.  **Prompt 59:** "Create a `Dockerfile` for the backend (in the Django project root):
    ```dockerfile
    FROM python:3.9
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
    ```

2.  **Prompt 60:** "Create a `Dockerfile` for the frontend (in the `frontend` directory):
    ```dockerfile
    FROM node:16
    WORKDIR /app
    COPY package*.json ./
    RUN npm install
    COPY . .
    CMD ["npm", "run", "dev"]
    ```

3.  **Prompt 61:** "Create a `docker-compose.yml` file in the project root:
    ```yaml
    version: '3.8'
    services:
      backend:
        build: ./backend # Path to your Django project
        ports:
          - "8000:8000"
        volumes:
          - ./backend:/app
        environment:
          - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
          - OPENAI_API_KEY=${OPENAI_API_KEY}
          - JIRA_API_TOKEN=${JIRA_API_TOKEN}
          - JIRA_SERVER_URL=${JIRA_SERVER_URL}
          - JIRA_USER_EMAIL=${JIRA_USER_EMAIL}
        depends_on:
          - db
      db:
        image:  sqlite #Use in memory db
      frontend:
        build: ./frontend # Path to your React project
        ports:
          - "5173:5173" # Or your Vite dev server port
        volumes:
          - ./frontend:/app
        depends_on:
          - backend

    ```
   Adjust paths and ports as needed.

4.  **Prompt 62:** "Build and run the application using `docker-compose up --build`.

This comprehensive set of prompts provides a structured, detailed guide for building the Jira integration application.  It covers project setup, backend logic, frontend development, and deployment with Docker Compose.  The prompts are designed to be given to an LLM to guide a developer through each stage of the process. Remember to review and test the code generated by the LLM at each step.
