The Python code implements a Streamlit application that interacts with Snowflake's Cortex Analyst using its REST API. 

Here's a breakdown of the architecture and process flow:

**1. Environment Setup and Initialization:**

Environment Variables: Sensitive data like Snowflake connection details (host, user, password, account, warehouse, role, database, schema, stage, and semantic model file path) are loaded from a .env file using load_dotenv.

Snowflake Connection: A persistent connection to Snowflake is established using snowflake.connector and stored in st.session_state.CONN. This avoids repeated authentication.

Streamlit Session State: st.session_state is used to maintain:

messages: The chat history between the user and the assistant.

suggestions: Suggestions provided by Cortex Analyst.

active_suggestion: The suggestion currently selected by the user.

**2. User Interaction (Streamlit Frontend):**

Chat Input: The user types their question in the Streamlit chat input.

Message Submission: When the user presses Enter, the process_message function is triggered.

**3. Cortex Analyst Interaction (REST API):**

send_message Function: This function constructs the request payload for the Cortex Analyst API:

messages: An array containing the user's prompt in the required format.

semantic_model_file: The path to the YAML semantic model file in Snowflake.

API Request: A POST request is sent to the /api/v2/cortex/analyst/message endpoint. The Snowflake token from the established connection is used for authentication.

Response Handling: The function parses the JSON response from the API, including the request ID. If an error occurs (status code >= 400), an exception is raised.

**4. Response Processing and Display (Streamlit Frontend):**

process_message Function (continued): The API response is processed. The user's message is added to the chat history. display_content is called to render the assistant's response.

display_content Function: Handles different response content types:

text: Displays plain text responses using st.markdown.

suggestions: Displays suggested follow-up questions as buttons. Clicking a button sets the active_suggestion.

sql: Displays the generated SQL code using st.code. Executes the SQL against Snowflake using pd.read_sql. Presents the results in a tabular format using st.dataframe. If the result set has multiple rows, it also displays interactive line and bar charts using st.line_chart and st.bar_chart, respectively.

Chat History Update: The assistant's response is appended to the messages list in the session state.

**5. Suggestion Handling:**

active_suggestion Processing: After each interaction, the code checks if an active_suggestion exists. If so, it's submitted as a new prompt to Cortex Analyst, continuing the conversation.

Architecture Diagram:

![image](https://github.com/user-attachments/assets/791d0db6-9c99-41f2-8e5b-804e4ca05659)


**Output:**

![image](https://github.com/user-attachments/assets/267b720a-003f-4913-b532-b27e8429f4be)

![image](https://github.com/user-attachments/assets/b5d96f2e-a53f-4e50-831b-5769da2648df)

![image](https://github.com/user-attachments/assets/8d3d61d7-3eb7-4100-b3b2-ccf09826b83f)

![image](https://github.com/user-attachments/assets/6244bfc9-6e32-452b-9d2f-e9b3ac52e74b)




