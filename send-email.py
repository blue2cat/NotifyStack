from smtplib import SMTP as Client

# Configuration
smtp_host = "localhost"
smtp_port = 587
sender_email = "user1@example.com"  # Replace with a valid sender email
password = "securepassword123"      # Replace with the sender's password
recipient_email = "b@example.com"   # Replace with the recipient's email

# Create the SMTP client
client = Client(smtp_host, smtp_port)

try:
    # Identify the client to the server
    client.ehlo()

    # Enable TLS encryption
    #client.starttls()
    client.ehlo()

    # Log in to the SMTP server
    #client.login(sender_email, password)

    # Send the email
    result = client.sendmail(
        sender_email,               # Sender's email
        [recipient_email],          # Recipient(s)
        "Subject: Test Email\n\nThis is a test email."  # Email content
    )

    print("Email sent successfully:", result)
except Exception as e:
    print("Failed to send email:", e)
finally:
    # Close the connection
    client.quit()
