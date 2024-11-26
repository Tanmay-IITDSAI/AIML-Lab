import streamlit as st
import mysql.connector
from huggingface_hub import InferenceClient

# Database connection constants
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Ved@mysql123'
DB_NAME = 'traffic_violation_db'

# Initialize the InferenceClient with your API key
client = InferenceClient(api_key="")

# Streamlit app
st.title("SQL Query Generator and Executor")
st.markdown("This app generates SQL queries based on your input and executes them on a MySQL database.")

# User input for the task description
user_input = st.text_input("Describe the SQL query you need (e.g., 'Get all records from the license_plates table'): ")

if st.button("Generate and Execute Query"):
    if user_input.strip():
        # System message for SQL query generation
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that generates SQL queries based on user input. Respond with the exact SQL query that solves the user's task. The name of the table is license_plates. Output just the answer."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        # Get the SQL query from the Hugging Face model
        try:
            completion = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3", 
                messages=messages, 
                max_tokens=500
            )
            sql_query = completion.choices[0].message['content']

            st.markdown(f"**Generated SQL Query:**\n```sql\n{sql_query}\n```")

            # Connect to the database and execute the query
            try:
                connection = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )

                cursor = connection.cursor()
                cursor.execute(sql_query)
                results = cursor.fetchall()

                # Display results in a table
                if results:
                    st.markdown("### Query Results")
                    for row in results:
                        st.write(row)
                else:
                    st.write("No results found.")
                
            except mysql.connector.Error as db_err:
                st.error(f"Database Error: {db_err}")
            
            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()

        except Exception as hf_err:
            st.error(f"Error in query generation: {hf_err}")

    else:
        st.warning("Please provide a task description to generate the query.")
