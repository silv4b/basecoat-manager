# Tutorial: Validação de E-mail com Django-Allauth

Este tutorial descreve como configurar a validação de e-mail obrigatória ou opcional em seu projeto Django utilizando a biblioteca `django-allauth`.

## 1. Configuração no `settings.py`

Para habilitar a validação de e-mail, você deve ajustar as configurações do `allauth` no seu arquivo `settings.py`.

### Alterar o método de verificação

Localize a constante `ACCOUNT_EMAIL_VERIFICATION` e altere seu valor:

- `"mandatory"`: O usuário não consegue fazer login até confirmar o e-mail.
- `"optional"`: O e-mail de confirmação é enviado, mas o login é permitido.
- `"none"`: (Atual) Nenhuma verificação é feita.

```python
# settings.py

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Ou "optional"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True       # Confirma o e-mail apenas clicando no link
```

## 2. Configuração do Backend de E-mail

O Django precisa saber como enviar os e-mails.

### Para Desenvolvimento (Console)

Use o backend de console para ver os e-mails no terminal em vez de enviá-los de fato:

```python
# settings.py (Apenas para desenvolvimento)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### Para Produção (SMTP)

Para enviar e-mails reais (ex: via Gmail, SendGrid, Mailtrap):

```python
# settings.py
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "Seu Nome <seu-email@exemplo.com>"
```

Adicione essas variáveis ao seu arquivo `.env`:

```env
EMAIL_HOST=smtp.exemplo.com
EMAIL_HOST_USER=seu_usuario
EMAIL_HOST_PASSWORD=sua_senha
```

## 3. URLs do Allauth

Certifique-se de que as URLs do `allauth` estão incluídas no seu `urls.py` principal:

```python
# core/urls.py
urlpatterns = [
    # ... outras urls
    path('accounts/', include('allauth.urls')),
]
```

## 4. Templates de E-mail (Opcional)

Se desejar customizar o conteúdo do e-mail de verificação, crie os seguintes arquivos em sua pasta de templates:

- `account/email/email_confirmation_subject.txt`: Assunto do e-mail.
- `account/email/email_confirmation_message.txt`: Corpo do e-mail em texto puro.
- `account/email/email_confirmation_signup_message.txt`: Mensagem de confirmação após o cadastro.

---
**Próximo Passo:** Após configurar, execute as migrações caso tenha adicionado campos novos, embora o `allauth` geralmente use tabelas existentes para verificação básica.
