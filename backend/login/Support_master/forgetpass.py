import smtplib
from email.message import EmailMessage
from Cache_Info.redis_Create import Create
from Cache_Info.redis_Read import Read
from load_var import ConfigVar

class MagicLink:
    def __init__(self):
        self.__SMTP_SERVER = "smtp.gmail.com"
        self.__SMTP_PORT = 587
        self.__SENDER_EMAIL =ConfigVar.SENDER_MAIL
        self.__SENDER_PASSWORD = ConfigVar.SENDER_PASS
        
    async def sendMagicLink(self,tomail, token):
        try:
            if  await Read.read_by_email(tomail) == {}:
                return # Thong bao : tao tai khoan moi
        except:
            return
        magic_url = f"https://yourapp.com/auth/magic?token={token}"
        html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Magic Link Login</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #007bff;
                color: #ffffff;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .button:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Đăng nhập bằng Magic Link</h2>
            <p>Chào bạn,</p>
            <p>Click vào nút dưới đây để đăng nhập vào tài khoản của bạn. Link này sẽ hết hạn sau 15 phút.</p>
            <p>
                <a href="{magic_url}" class="button">Đăng nhập ngay</a>
            </p>
            <p>Nếu không phải bạn yêu cầu, vui lòng bỏ qua email này.</p>
            <p>Trân trọng,<br>Đội ngũ YourApp</p>
        </div>
    </body>
    </html>
    """

        # Tạo email
        msg = EmailMessage()
        msg["Subject"] = "Đăng nhập Magic Link"
        msg["From"] = self.__SENDER_EMAIL
        msg["To"] = tomail

        # Thiết lập nội dung HTML
        msg.set_content("This email requires HTML support. Please view it in a compatible email client.")
        msg.add_alternative(html_content, subtype="html")  # Thêm nội dung HTML

        # Gửi email qua SMTP
        try:
            with smtplib.SMTP(self.__SMTP_SERVER,self.__SMTP_PORT) as server:
                server.starttls()  # Bật mã hóa
                server.login(self.__SENDER_EMAIL, self.__SENDER_PASSWORD)
                server.send_message(msg)
            print(f"Email sent to {tomail}")
        except Exception as e:
            print(f"Error sending email: {e}")

    async def vertify_magiclink(token):
        if Read.read_magiclink(token) == 1:
            #login
            pass
        else:
            return False # Quay vef trang dang nhap va goi y cho ng dung dang nhap lai
        