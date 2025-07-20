import os
import sys
import datetime
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_date_string():
    """Get formatted date string"""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def read_content_files():
    """Read content from the markdown files"""
    context_files = {
        "recent_temporal": "../claude summaries/temporal/recent-summary.md",
        "master_summary": "../claude summaries/master-summary.md",
        "calendar": "../data/calendar.md"
    }
    
    content = {}
    
    for key, filename in context_files.items():
        try:
            with open(filename, 'r') as f:
                content[key] = f.read()
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            content[key] = f"[Error reading {filename}]"
    
    return content

def call_claude_api(content, api_key):
    """Call Claude API for daily advice generation"""

    system_prompt = f"""You are Claude. Today is {date_str}."""

    # Construct the prompt with available context
    prompt = f"""Based on the following information about my journal and calendar, please provide thoughtful daily advice and insights. Focus on what's coming up today and this week, any patterns you notice, and suggestions for making the most of the day ahead.

## Recent Summary
{content.get('recent_temporal', 'Not available')}

## Calendar Today and This Week
{content.get('calendar', 'Not available')}

## Current Life Context (Master Summary)
{content.get('master_summary', 'Not available')}

Please provide:
1. A brief reflection on recent patterns or themes
2. Specific suggestions for today based on my calendar and current context
3. Any insights about upcoming events or opportunities
4. General advice for maintaining balance and making progress on important goals

Keep the response conversational, practical, and personally relevant. Focus on actionable insights rather than generic advice."""

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    
    data = {
        "model": "claude-opus-4-20250514",
        "max_tokens": 12000,
        "system": system_prompt,
        "thinking": {
            "type": "enabled",
            "budget_tokens": 10000
        },
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data['content'][0]['text']
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def send_email(subject, body, sender_email, sender_password, receiver_email):
    """Send email with the daily advice"""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        print(f"Email sent successfully to {receiver_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def save_daily_update(content, date_str):
    """Save the daily update to a file"""
    filename = f"../meditation advice/latest_daily_update.md"
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            f.write(f"# Daily Update - {date_str}\n\n")
            f.write(content)
            f.write(f"\n\n---\n*Generated on {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")
        
        print(f"Daily update saved to {filename}")
        return True
        
    except Exception as e:
        print(f"Error saving daily update: {e}")
        return False

def main():
    """Main function to generate and send daily email"""
    
    # Get environment variables
    claude_api_key = os.environ.get('CLAUDE_API_KEY')
    sender_email = os.environ.get('EMAIL_SENDER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    receiver_email = os.environ.get('EMAIL_RECEIVER')
    
    # Check required environment variables
    if not claude_api_key:
        print("Error: CLAUDE_API_KEY environment variable not set")
        sys.exit(1)
    
    if not all([sender_email, sender_password, receiver_email]):
        print("Error: Email environment variables not set (EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER)")
        sys.exit(1)
    
    print("Starting daily email generation...")
    
    # Read content files
    print("Reading content files...")
    content = read_content_files()
    
    # Generate advice using Claude
    print("Calling Claude API...")
    daily_advice = call_claude_api(content, claude_api_key)
    
    if not daily_advice:
        print("Failed to generate daily advice")
        sys.exit(1)
    
    # Get current date
    date_str = get_date_string()
    
    # Save daily update
    print("Saving daily update...")
    save_daily_update(daily_advice, date_str)
    
    # Prepare email
    subject = f"Daily Insights - {date_str}"
    
    # Send email
    print("Sending email...")
    email_sent = send_email(
        subject=subject,
        body=daily_advice,
        sender_email=sender_email,
        sender_password=sender_password,
        receiver_email=receiver_email
    )
    
    if email_sent:
        print("Daily email process completed successfully!")
    else:
        print("Email sending failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
