# School Data Chatbot

## Overview

This project is a chatbot that queries a SQLite database built from dummy school data. The database contains multiple tables (e.g., terms, students, guardians, attendance, behaviour, and attainment) generated from `data/school_dummy_data.json`. The chatbot demonstrates function calling abilities by dynamically querying the database and plotting results based on user questions.

## Features

- **Natural Language Queries:**  
  Ask questions like:  
  - "What was Abbie Adams' attendance in the autumn term?"  
  - "How is Harvey Walker doing in Maths?"  
  - "How can I contact Eden Turner's mum?"  
  - "Has Zach Hill had any detentions this term?"

- **Database Querying:**  
  The chatbot builds SQL queries on the fly and retrieves data from a SQLite database.

- **Data Visualization:**  
  When needed, it plots results (e.g., attendance trends, academic performance).

- **Function Calling:**  
  Showcases dynamic function calling to process queries and display results.

## Project Structure

- **src/**: Application source code (chatbot, API handlers, database initialisation, etc.)
- **data/**: Dummy data (`school_dummy_data.json`) used to populate the database
- **chainlit.md**: Markdown file with startup instructions for the chatbot
- **pyproject.toml**: Poetry configuration for dependency management
- **.env**: Environment configuration file

## Running the Project with Docker

### Prerequisites

- Ensure [Docker](https://www.docker.com/) is installed on your machine.

### Steps

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Environment Variables Setup:**

Before building the Docker image, you must create a `.env` file in the root of the project directory. This file should contain your OpenAI API key, which is required for the chatbot to function properly. For example, your `.env` file should include:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

An example file named .env_example is provided. Copy this file, rename it to .env, and then update it with your OpenAI API key. This step must be completed before running docker build.

3. **Build the docker image:**

   ```bash
   docker build -t school-data-chatbot .
   ```

4. **Build the docker image:**

   ```bash
   docker run -p 8002:8002 school-data-chatbot
   ```

The chatbot will be available at http://localhost:8002/.
