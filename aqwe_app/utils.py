from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
import os
#from docx import Document

def send_advice_email(user_email: str, advice_message: str):
     subject = 'Ваш детальный совет от АКВИ'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [user_email]
     with open('advice.txt', 'w') as f:
         f.write(advice_message)
     email = EmailMessage(subject, advice_message, from_email, to_email)
     email.attach_file('advice.txt')
     message = f'категория: {advice.category}\n\nВопрос: {advice.question}\n\nОтвет: {advice.answer}\n\nЗаметки: {advice.notes}'
     try:
         email.send(fail_silently=False)
     except Exception as e:
         print(f"Ошибка при отправке письма: {e}")
     finally:
         if os.path.exists('advice.txt'):
             os.remove('advice.txt')
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
               
     #subject = 'Ваш совет от АКВИ'
     #message = f'Вот ваш совет:\n\n{advice}'
     #send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)