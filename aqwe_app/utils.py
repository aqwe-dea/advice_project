from django.core.mail import send_mail

def send_advice_email(user_email: str, advice: str):
    subject = 'Ваш совет от АКВИ'
    message = f'Вот ваш совет:\n\n{advice}'
    send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)