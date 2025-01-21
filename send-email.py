from smtplib import SMTP as Client

client = Client("localhost", 587)

r = client.sendmail('a@example.com', ['b@example.com'], 'test')