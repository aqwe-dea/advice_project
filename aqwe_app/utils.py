from django.core.mail import send_mail

def send_advice_email(user_email: str, advice: str):
    email = EmailMessage(
         subject='Ваш детальный совет от АКВИ',
         body=message,
         from_email=DEFAULT_FROM_EMAIL,
         to=[user_email],
    )
    email.attach_file('advice.txt')
    email.send(fail_silently=False)
       
     subject = 'Ваш совет от АКВИ'
     message = f'Вот ваш совет:\n\n{advice}'
     send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)