from openai import OpenAI
import psycopg2
import requests
from pdfminer.high_level import extract_text
import os
import json

# Step 1: Connect to the PostgreSQL database
def connect_to_db():
    return psycopg2.connect(
        host='localhost',
        user='postgres',
        password='122705',
        dbname='openreview'
    )

# Step 2: Retrieve forum and review data from the database
def get_forum_data(cursor):
    cursor.execute("SELECT id, pdf_link FROM forum")
    return cursor.fetchall()

def get_review_data(cursor, forum_id):
    cursor.execute("SELECT content FROM review WHERE forum = %s", (forum_id,))
    return cursor.fetchall()

# Step 3: Download PDF and extract text
def download_pdf(pdf_url, filename):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF: {filename}")
    except requests.RequestException as e:
        print(f"Error downloading PDF from {pdf_url}: {e}")
        return None
    return filename

def pdf_to_text_with_pdfminer(filename):
    try:
        text = extract_text(filename)
        print(f"Extracted text from PDF: {filename}")
        return text
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return None
    finally:
        if os.path.exists(filename):
            os.remove(filename)  # Clean up by deleting the PDF file

# Step 4: Prepare few-shot examples for ChatGPT prompt
few_shot_examples = [
    {
        "role": "system",
        "content": "You are an academic reviewer for a research conference. Provide a summary of the review and a recommendation score between 1 and 10 as an integer."
    },
    {
        "role": "user",
        "content": "Generate a summary of the review and a recommendation score for the paper."
    },
    {
        "role": "assistant",
        "content": """Summary of the Review:
The use of CLIP to generate task-specific concept sets is innovative and promising. However, some filtering methods appear heuristic-based and could benefit from justification through ablation studies. The application of CLIP-Dissect (CD) and the GLM-SAGA solver is novel and well-motivated, though there is a lack of clarity in the differences between CD and the proposed approach. Addressing these issues would significantly strengthen the paper.

Recommendation: 6
"""
    },
    {
        "role": "user",
        "content": "Generate a review summary and recommendation score for the paper."
    },
    {
        "role": "assistant",
        "content": """Summary of the Review:
This paper presents an approach to create concept bottleneck models without requiring labeled data, leveraging large language models and embeddings. While creative, the paper could benefit from additional validation experiments to substantiate the results. Some sections would also benefit from clearer elaboration to support the claims. Overall, the approach is intriguing but has room for improvement.

Recommendation: 7
"""
    },
    {
        "role": "user",
        "content": "Please provide a summary of the review and a recommendation score."
    },
    {
        "role": "assistant",
        "content": """Summary of the Review:
The paper introduces a novel framework that creatively leverages GPT and CLIP for label-free concept generation. While the approach is interesting and shows promise, the evaluation feels limited. Additional details in certain sections and further empirical analysis could strengthen the findings. This paper provides a useful contribution to the field but needs improvement in clarity and thoroughness.

Recommendation: 8
"""
    }
]

# Step 5: Generate reviews using ChatGPT API
def generate_review_summary(client, raw_text, few_shot_examples):
     # Construct the messages as a list with system, few-shot, and user messages
    messages = few_shot_examples + [
        {"role": "user", "content": f"Paper content:\n{raw_text}\nGenerate a review summary and recommendation score:"}
    ]
    
    # Send the request to OpenAI's API with the correct model and message format
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    
    # Extract and parse the content of the assistant's response
    content = response.choices[0].message.content

    # Initialize variables for parsed data
    score = None
    summary = ""

    # Parse the response to extract score and summary
    lines = content.splitlines()
    for line in lines:
        if "Summary of the Review:" in line:
            # Extract summary text starting from the summary line
            summary_index = lines.index(line)
            summary = "\n".join(lines[summary_index + 1:]).strip()
            break
        elif "Recommendation:" in line:
            # Extract the numeric score
            try:
                score = int(line.split(":")[1].strip())
            except ValueError:
                print("Could not parse recommendation score.")
            break

    # Return the parsed recommendation score and summary
    return score, summary

def insert_generated_review(cursor, forum_id, recommendation_score, summary):
    """
    Inserts the generated review data into the 'generated_reviews' table.
    """
    try:
        cursor.execute("""
            INSERT INTO generated_reviews (forum_id, recommendation_score, summary)
            VALUES (%s, %s, %s)
        """, (forum_id, recommendation_score, summary))
        cursor.connection.commit()  # 커밋 추가
        print(f"Inserted review for forum_id {forum_id} with score {recommendation_score}.")
    except Exception as e:
        print(f"Error inserting generated review for forum_id {forum_id}: {e}")
        cursor.connection.rollback()  # 오류 발생 시 롤백

# Main script
def main():
    # Connect to DB
    db = connect_to_db()
    cursor = db.cursor()

    # OpenAI client
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Retrieve forum data
    forums = get_forum_data(cursor)

    for forum_id, pdf_url in forums:
        # Download PDF and extract text
        pdf_filename = f"{forum_id}.pdf"
        downloaded_pdf = download_pdf(pdf_url, pdf_filename)

        if downloaded_pdf:
            raw_text = pdf_to_text_with_pdfminer(downloaded_pdf)
            if raw_text:
                # Generate review summary and recommendation score
                score, summary = generate_review_summary(client, raw_text, few_shot_examples)
                
                # Print results
                print(f"Generated Recommendation Score for {forum_id}: {score}")
                print(f"Generated Review Summary for {forum_id}:\n{summary}")

                # Insert generated review into the database
                insert_generated_review(cursor, forum_id, score, summary)

    # Close DB connection
    cursor.close()
    db.close()

if __name__ == "__main__":
    main()