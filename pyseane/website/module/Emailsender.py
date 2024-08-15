import smtplib
import uuid
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from .Config import SERVER, ACCOUNT

def send_email(server,fromaddr, destinataire, sujet, content, url_fish):
    header = "<!DOCTYPE html><html><head><title></title></head><body><img src='http://localhost:8000/jaiouvertlemail' width='1' height='1' style='display:none;'><p>"
    footer = "</p></body></html>"
    contenu_html = header + content + footer
    message = MIMEMultipart()
    linkname = contenu_html[contenu_html.find('[[')+2 : contenu_html.find(']]') ]
    contenu_html_avec_url = re.sub("\[\[.*\]\]", f"<a href='{url_fish}'>{linkname}</a>", contenu_html)
    contenu_html_avec_url = re.sub("\n", "<br>", contenu_html_avec_url)

    # Créez l'objet MIMEText avec le contenu HTML mis à jour
    html_message = MIMEText(contenu_html_avec_url, 'html')
    message.attach(html_message)

    # Configurer les en-têtes du message
    message['From'] = fromaddr
    message['To'] = destinataire
    message['Subject'] = sujet
    message['Content-Type'] = "text/html; charset=ISO-8859-1"
    message['Date'] = formatdate(localtime=True)

    try:
        server.sendmail(fromaddr, [destinataire], message.as_string())
        return True
    except smtplib.SMTPException as e:
        return False

def TryConnection(mailtype, mail, password):
    server = smtplib.SMTP(SERVER["SMTP_SERVER"], SERVER["SMTP_PORT"])
    server.connect(SERVER["SMTP_SERVER"], SERVER["SMTP_PORT"])
    server.ehlo()
    server.starttls()

    if int(mailtype) == 0:
        ACCOUNT[0]["EMAIL"] = mail
        ACCOUNT[0]["PASSWORD"] = password
    try:
        server.login(ACCOUNT[int(mailtype)]["EMAIL"], ACCOUNT[int(mailtype)]["PASSWORD"])
        return server
    except:
        return None

def EmailSender(server, campagne_id, mailtype, nom, destinataires, sujet, content):
    sended = []
    fromaddr = nom+' <'+ ACCOUNT[int(mailtype)]["EMAIL"] +'>'

    for destinataire in destinataires:
        stocked_uuid = uuid.uuid4()
        url = "http://localhost:8000/"+"campagnes/"+campagne_id+"?follow="+str(stocked_uuid)

        res = send_email(server,fromaddr,destinataire, sujet, content, url)
        if res:
            sended.append(stocked_uuid)

    server.quit()
    return sended
