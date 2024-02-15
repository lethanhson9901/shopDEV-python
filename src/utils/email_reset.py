from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

# Configure Jinja2 environment
env = Environment(
    loader=FileSystemLoader(searchpath="./templates"),
    autoescape=select_autoescape(['html', 'xml'])
)

def send_reset_email(user_email: str, token: str):
    """
    Sends a password reset email to the user using a Jinja2 template for dynamic email content.
    
    Parameters:
    - user_email (str): The email address of the user to send the reset email to.
    - token (str): The password reset token to be included in the email for verification.
    """
    # Load and render the email template
    template = env.get_template('password_reset_email.html')
    reset_link = f"https://yourapp.com/reset-password?token={token}"
    email_content = template.render(reset_link=reset_link)
    
    print(f"Sending email to {user_email}:\n{email_content}")
    # Implement the actual email sending logic here