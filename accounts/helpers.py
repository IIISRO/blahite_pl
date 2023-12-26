from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives




def send_activate_link(user,uid,token):
    context ={
        'user': user,
        'uid':uid,
        'token': token,
    }

    html_content = render_to_string("activate.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        f'Register Success!',
        text_content,
        settings.EMAIL_HOST_USER ,
        [user.email]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
    return True

def send_forgetpwd_link(user,uid,token):
    context ={
        'user': user,
        'uid':uid,
        'token': token,
    }

    html_content = render_to_string("forgetpwd.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        f'Register Success!',
        text_content,
        settings.EMAIL_HOST_USER ,
        [user.email]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
    return True