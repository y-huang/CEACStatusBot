from smtplib import SMTP_SSL
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from .handle import NotificationHandle

class EmailNotificationHandle(NotificationHandle):
    def __init__(self,fromEmail:str,toEmail:str,emailPassword:str,hostAddress:str='') -> None:
        super().__init__()
        self.__fromEmail = fromEmail
        self.__toEmail = toEmail.split("|")
        self.__emailPassword = emailPassword
        self.__hostAddress = hostAddress or "smtp."+fromEmail.split("@")[1]
        if ':' in self.__hostAddress:
            [addr, port] = self.__hostAddress.split(':')
            self.__hostAddress = addr
            self.__hostPort = int(port)
        else:
            self.__hostPort = 0

    def format_result_text(self, result):
        lines = []
        lines.append(f"Application Number: {result.get('application_num_origin')}")
        lines.append(f"Visa Type: {result.get('visa_type')}")
        lines.append(f"Status: {result.get('status')}")
        lines.append(f"Case Created: {result.get('case_created')}")
        lines.append(f"Last Updated: {result.get('case_last_updated')}")
        lines.append("")
        lines.append(f"Description:")
        lines.append(result.get('description', "").strip())
        lines.append("")
        lines.append("- CEACStatusBot")
        return "\n".join(lines)

    def format_result_text(self, result):        
        html = f"""
        <html>
          <body>
            <p>Application Number: {result.get('application_num_origin')}</p>
            <p>Visa Type: {result.get('visa_type')}</p>
            <p>Status: <b>{result.get('status')}</b></p>
            <p>Case Created: {result.get('case_created')}</p>
            <p>Last Updated: <b>{result.get('case_last_updated')}</b></p>
            <br>
            <p>Description:</p>
            <p>{result.get('description', '').strip()}</p>
            <br>
            <p>-- CEACStatusBot</p>
          </body>
        </html>
        """
        return html
    
    def send(self, result):
        
        # {'success': True, 'visa_type': 'NONIMMIGRANT VISA APPLICATION', 'status': 'Issued', 'case_created': '30-Aug-2022', 'case_last_updated': '19-Oct-2022', 'description': 'Your visa is in final processing. If you have not received it in more than 10 working days, please see the webpage for contact information of the embassy or consulate where you submitted your application.', 'application_num': '***'}

        mail_title = '[CEACStatusBot] {} : {}'.format(result["application_num_origin"],result['status'])
        mail_content = self.format_result_text(result)

        msg = MIMEMultipart()
        msg["Subject"] = Header(mail_title,'utf-8')
        msg["From"] = self.__fromEmail
        msg['To'] = ";".join(self.__toEmail)
        msg.attach(MIMEText(mail_content,'html','utf-8'))

        smtp = SMTP(self.__hostAddress, self.__hostPort)
        smtp.starttls() # ssl登录
        print(smtp.login(self.__fromEmail,self.__emailPassword))
        print(smtp.sendmail(self.__fromEmail,self.__toEmail,msg.as_string()))
        smtp.quit()
