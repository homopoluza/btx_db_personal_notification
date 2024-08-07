import smtplib
from email.mime.text import MIMEText
import mysql.connector
from datetime import datetime, timedelta

def send_email(user_id, name, last_name, date, days, date_type):
    msg = MIMEText(f"User {user_id}: {name} {last_name} has {date_type} {date} within {days} days!")
    msg['Subject'] = f"User {user_id}: {name} {last_name} has {date_type} {date} within {days} days!"
    msg['From'] = email_login
    msg['To'] = email_to

    s = smtplib.SMTP(smtp_server, smtp_port)
    s.starttls()
    s.login(email_login, email_password)
    s.send_message(msg)
    s.quit()

# Email settings
smtp_server = ''
smtp_port = 587
email_login = ''
email_password = ''
email_to = ''

# MySQL connection parameters
db_config = {
    'host': '127.0.0.1',
    'user': 'python',
    'password': '',
    'database': ''
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    #shows only active non-system non-external users
    query = """
        SELECT
    u.ID,
    u.NAME,
    u.LAST_NAME,
    u.PERSONAL_BIRTHDAY,
    DATE_FORMAT(b_uts_user.UF_USR_1719924260264, '%Y-%m-%d') AS 'EMPLOYMENT_DATE',
    DATE_FORMAT(b_uts_user.UF_USR_1723031782192, '%Y-%m-%d') AS 'END_PROBATION_DATE'
FROM b_user u
LEFT JOIN (
    SELECT DISTINCT USER_ID
    FROM b_user_group
    WHERE GROUP_ID = 17
) excluded_users ON u.ID = excluded_users.USER_ID
LEFT JOIN b_uts_user ON u.ID = b_uts_user.VALUE_ID
WHERE u.ACTIVE = 'Y'
    AND u.EXTERNAL_AUTH_ID IS NULL
    AND excluded_users.USER_ID IS NULL;
    """
    cursor.execute(query)

    rows = cursor.fetchall()

    # Compare PERSONAL_BIRTHDAY with current date
    today = datetime.now().date()
    for row in rows:
        user_id, name, last_name, birthday, employment_date_str, probation_date_str = row
        if birthday:           
            birthday_month_day = birthday.replace(year=today.year)  # Keep only month and day
            today_plus_seven = today + timedelta(days=7)
            if today <= birthday_month_day <= today_plus_seven:
                delta = birthday_month_day - today
                date_type = "a birthday"
                send_email(user_id, name, last_name, birthday, delta.days, date_type)

        if employment_date_str:
            employment_date = datetime.strptime(employment_date_str, '%Y-%m-%d').date()
            employment_date_month_day = employment_date.replace(year=today.year)  # Keep only month and day
            today_plus_seven = today + timedelta(days=7)
            if today <= employment_date_month_day <= today_plus_seven:
                delta = employment_date_month_day - today
                date_type = "an emplyment date anniversary"
                send_email(user_id, name, last_name, employment_date, delta.days, date_type) 

        if probation_date_str:
            probation_date = datetime.strptime(probation_date_str, '%Y-%m-%d').date()
            probation_date_month_day = probation_date.replace(year=today.year)  # Keep only month and day
            today_plus_one = today + timedelta(days=1)
            if today <= probation_date_month_day <= today_plus_one:
                delta = probation_date_month_day - today
                date_type = "an end of probation date"
                send_email(user_id, name, last_name, probation_date, delta.days, date_type)        

    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
