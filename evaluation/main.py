import psycopg2
import json
from collections import defaultdict

# Step 1: Connect to the PostgreSQL database
def connect_to_db():
    return psycopg2.connect(
        host='localhost',
        user='postgres',
        password='122705',
        dbname='openreview'
    )

# Step 2: Parse recommendation score from JSON-like content
def parse_recommendation_score(content):
    """
    Parses and extracts the recommendation score from review content.
    """
    try:
        # Convert JSON string to dictionary
        review_data = json.loads(content)
        
        # Extract the recommendation text and find the numeric score
        recommendation_text = review_data.get("recommendation", "")
        score = int(recommendation_text.split(":")[0].strip())
        return score
    except (ValueError, AttributeError, json.JSONDecodeError) as e:
        print("Error parsing recommendation score:", e)
        return None

# Step 3: Fetch recommendation scores from generated_reviews and review tables
def fetch_comparative_scores(cursor):
    # Fetch all recommendation scores from generated_reviews
    cursor.execute("SELECT forum_id, recommendation_score FROM generated_reviews")
    generated_reviews = cursor.fetchall()
    
    # Fetch all reviews from the review table
    cursor.execute("SELECT forum, content FROM review")
    review_contents = cursor.fetchall()
    
    # Parse recommendation scores from review contents and organize by forum_id
    review_scores = defaultdict(list)
    for forum_id, content in review_contents:
        score = parse_recommendation_score(content)
        if score is not None:
            review_scores[forum_id].append(score)
    
    # Calculate the average score for each forum_id in review_scores
    avg_review_scores = {forum_id: sum(scores) / len(scores) for forum_id, scores in review_scores.items()}
    
    # Combine the results by forum_id from generated_reviews and avg_review_scores
    comparative_scores = []
    for forum_id, generated_score in generated_reviews:
        avg_score = avg_review_scores.get(forum_id)
        comparative_scores.append((forum_id, generated_score, avg_score))
    
    return comparative_scores

# Step 4: Calculate and display the differences
def compare_scores():
    # Connect to the database
    db = connect_to_db()
    cursor = db.cursor()

    # Fetch generated and average review scores
    comparative_scores = fetch_comparative_scores(cursor)
    print(comparative_scores)

    # Display the comparison results
    print("Comparison of recommendation scores (generated vs. review average):")
    for forum_id, generated_score, avg_review_score in comparative_scores:
        if avg_review_score is not None:
            difference = generated_score - avg_review_score
            print(f"Forum ID: {forum_id} | Generated Score: {generated_score} | Average Review Score: {avg_review_score:.2f} | Difference: {difference:.2f}")
        else:
            print(f"Forum ID: {forum_id} | Generated Score: {generated_score} | Average Review Score: N/A (no reviews)")

    # Close the database connection
    cursor.close()
    db.close()

# Run the comparison
if __name__ == "__main__":
    compare_scores()