import openreview
import psycopg2
import datetime
import json

def create_db_connection():
    # PostgreSQL 데이터베이스 연결 설정
    db = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='122705',
        dbname='openreview'
    )
    cursor = db.cursor()
    return db, cursor

def create_tables(cursor):
    # forum 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forum (
        id VARCHAR(255) NOT NULL PRIMARY KEY,
        title TEXT NOT NULL,
        abstract TEXT NOT NULL,
        authors TEXT NOT NULL,
        keywords TEXT NOT NULL,
        pdf_link VARCHAR(255) NOT NULL,
        invitation VARCHAR(255) NOT NULL,
        cdate TIMESTAMP NOT NULL
    )
    """)

    # review 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review (
        id VARCHAR(255) NOT NULL PRIMARY KEY,
        forum VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        signatures TEXT NOT NULL,
        invitation VARCHAR(255) NOT NULL,
        cdate TIMESTAMP NOT NULL,
        FOREIGN KEY (forum) REFERENCES forum(id)
    )
    """)

def insert_forum(db, cursor, forum_entity):
    try:
        cursor.execute("""
        INSERT INTO forum (id, title, abstract, authors, keywords, pdf_link, invitation, cdate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            forum_entity['id'],
            forum_entity['title'],
            forum_entity['abstract'],
            forum_entity['authors'],
            forum_entity['keywords'],
            forum_entity['pdf_link'],
            forum_entity['invitation'],
            forum_entity['cdate']
        ))
        db.commit()
    except psycopg2.Error as err:
        print(f"Error: {err}")
        db.rollback()

def insert_review(db, cursor, review_entity):
    try:
        cursor.execute("""
        INSERT INTO review (id, forum, content, signatures, invitation, cdate)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            review_entity['id'],
            review_entity['forum'],
            review_entity['content'],
            review_entity['signatures'],
            review_entity['invitation'],
            review_entity['cdate']
        ))
        db.commit()
    except psycopg2.Error as err:
        print(f"Error: {err}")
        db.rollback()

def convert_forum_to_entity(forum):
    forum_entity = {
        'id': forum.id,
        'title': forum.content.get('title', ''),
        'abstract': forum.content.get('abstract', ''),
        'authors': ', '.join(forum.content.get('authors', [])),
        'keywords': ', '.join(forum.content.get('keywords', [])),
        'pdf_link': 'https://openreview.net' + forum.content.get('pdf', ''),
        'invitation': forum.invitation,
        'cdate': datetime.datetime.fromtimestamp(forum.cdate / 1000)
    }
    return forum_entity

def convert_review_to_entity(review):
    review_entity = {
        'id': review.id,
        'forum': review.forum,
        'content': json.dumps(review.content),
        'signatures': ', '.join(review.signatures),
        'invitation': review.invitation,
        'cdate': datetime.datetime.fromtimestamp(review.cdate / 1000)
    }
    return review_entity

def get_submissions(client, invitation):
    submissions = list(openreview.tools.iterget_notes(
        client,
        invitation=invitation,
    ))
    print(f"초대 {invitation}의 제출물 수: {len(submissions)}")
    return submissions

def get_reviews(client, forum_id):
    reviews = []
    notes = list(openreview.tools.iterget_notes(
        client,
        forum=forum_id,
    ))
    for note in notes:
        if 'Official_Review' in note.invitation:
            reviews.append(note)
    print(f"포럼 {forum_id}의 리뷰 수: {len(reviews)}")
    return reviews

def main():
    # OpenReview 클라이언트 생성
    client = openreview.Client(baseurl='https://api.openreview.net')

    db, cursor = create_db_connection()
    create_tables(cursor)

    invitation = 'ICLR.cc/2023/Conference/-/Blind_Submission'
    submissions = get_submissions(client, invitation)

    for submission in submissions:
        forum_entity = convert_forum_to_entity(submission)
        insert_forum(db, cursor, forum_entity)

        reviews = get_reviews(client, submission.id)
        for review in reviews:
            review_entity = convert_review_to_entity(review)
            insert_review(db, cursor, review_entity)

        print(f"포럼 {submission.id}의 데이터를 저장했습니다.")

    cursor.close()
    db.close()

if __name__ == '__main__':
    main()