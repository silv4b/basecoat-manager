# Tutorial: Login Social (Google e GitHub) com Django-Allauth

Este tutorial guia você na implementação de autenticação social via Google (Gmail) e GitHub usando `django-allauth`.

## 1. Instalação e Configuração Inicial

Adicione os módulos necessários ao `INSTALLED_APPS` no seu `settings.py`:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # Para Google
    'allauth.socialaccount.providers.github', # Para GitHub
    # ...
]
```

Certifique-se de que o `SITE_ID` está definido (geralmente `1` para desenvolvimento):

```python
SITE_ID = 1
```

## 2. Configurar Provedores SocialAccount

Você pode configurar as chaves diretamente no `settings.py` ou via Painel Administrativo do Django. Recomendamos usar o `settings.py` com variáveis de ambiente para maior segurança.

```python
# settings.py

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'github': {
        'APP': {
            'client_id': os.environ.get('GITHUB_CLIENT_ID'),
            'secret': os.environ.get('GITHUB_SECRET'),
            'key': ''
        }
    }
}
```

## 3. Obter Credenciais

### GitHub

1. Vá para [GitHub Developer Settings](https://github.com/settings/developers).
2. Clique em **New OAuth App**.
3. Nomeie sua aplicação.
4. **Homepage URL**: `http://127.0.0.1:8000/`
5. **Authorization callback URL**: `http://127.0.0.1:8000/accounts/github/login/callback/`
6. Gere o **Client ID** e o **Client Secret**.

### Google

1. Vá para o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto.
3. Configure a **OAuth consent screen** (externa).
4. Vá em **Credentials** -> **Create Credentials** -> **OAuth client ID**.
5. Selecione **Web application**.
6. **Authorized JavaScript origins**: `http://127.0.0.1:8000`
7. **Authorized redirect URIs**: `http://127.0.0.1:8000/accounts/google/login/callback/`
8. Copie seu **Client ID** e **Client Secret**.

## 4. Variáveis de Ambiente

Adicione as credenciais ao seu arquivo `.env`:

```env
GOOGLE_CLIENT_ID=seu_google_id
GOOGLE_SECRET=seu_google_secret
GITHUB_CLIENT_ID=seu_github_id
GITHUB_SECRET=seu_github_secret
```

## 5. Implementação no Frontend

Carregue a biblioteca social em seus templates (ex: `login.html`):

```html
{% load socialaccount %}

<div class="social-login">
    <a href="{% provider_login_url 'google' %}" class="btn btn-google">
        Entrar com Google
    </a>

    <a href="{% provider_login_url 'github' %}" class="btn btn-github">
        Entrar com GitHub
    </a>
</div>
```

## 6. Executar Migrações

Sempre que adicionar novos provedores ou o módulo `socialaccount`, execute as migrações:

```bash
uv run manage.py migrate
```

---
**Nota:** Para testes locais com Google, certifique-se de usar `127.0.0.1:8000` em vez de `localhost:8000`, pois o Google pode ser restritivo com domínios `localhost`.
