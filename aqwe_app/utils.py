import os
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
#from docx import Document

def send_advice_email(user_email: str, advice_message: str):
    subject = 'Ваш детальный совет от АКВИ'
    message = f'категория: {advice.category}\n\nВопрос: {advice.question}\n\nОтвет: {advice.answer}\n\nЗаметки: {advice.notes}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]
    email = EmailMessage(subject, advice_message, from_email, to_email)
    email.attach_file('advice.txt')
    with open('advice.txt', 'w') as f:
        f.write(advice_message)
    try:
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
    finally:
        if os.path.exists('advice.txt'):
            os.remove('advice.txt')
    #subject = 'Ваш совет от АКВИ'
    #message = f'Вот ваш совет:\n\n{advice}'
    #send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
    #doc = Document()
    #doc.add_heading('Ваш детальный совет от АКВИ', level=1)
    #doc.add_paragraph(f'Категория: {advice.category}')
    #doc.add_paragraph(f'Вопрос: {advice.question}')
    #doc.add_paragraph(f'Ответ: {advice.answer}')
    #doc.add_paragraph(f'Заметки: {advice.notes}')
    #doc.save('advice.doc')  
    #email.attach_file('advice.doc')
    #email.send(fail_silently=False)
    #email = EmailMessage(
        #subject = subject,
        #body = message,
        #from_email = DEFAULT_FROM_EMAIL,
        #to = [user_email],
    #)