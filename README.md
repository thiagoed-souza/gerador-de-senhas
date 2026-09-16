<div align="center">

# 🛡️ PassGuard

**Gerador e Cofre de Senhas Seguro com Flask & Tailwind CSS**

![Python](https://img.shields.io/badge/Python-306998?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

<p align="center">
  Uma aplicação web moderna e responsiva para geração de senhas fortes, verificação de segurança em tempo real e armazenamento seguro de credenciais.
</p>

</div>

---

## 📌 Sobre o Projeto

O **PassGuard** é uma solução completa desenvolvida para facilitar a gestão de credenciais do dia a dia. Com uma interface estilo *dark mode* elegante e responsiva, o sistema permite personalizar a geração de senhas, medir sua força em tempo real e armazená-las de forma centralizada em um cofre protegido por autenticação.

---

## ✨ Funcionalidades Principais

* **🔑 Gerador Configurável de Senhas:** Personalização de tamanho (6 a 32 caracteres) e inclusão de letras maiúsculas, números e símbolos.
* **📊 Indicador de Força em Tempo Real:** Análise instantânea de complexidade da senha via JavaScript.
* **🔐 Cofre de Senhas:** Armazenamento individual de credenciais por usuário.
* **👁️ Ocultação/Exibição Dinâmica:** Alternância de visibilidade para senhas salvas no cofre.
* **🔍 Busca em Tempo Real:** Filtro rápido por nome do serviço ou usuário dentro do cofre.
* **📋 Copia Rápida:** Botão com retorno visual para copiar senhas para a área de transferência.
* **👤 Gestão de Perfil:** Atualização de avatar com *preview* instantâneo e alteração de senha de acesso.
* **🛡️ Autenticação de Usuários:** Sistema completo de cadastro, login, logout e rotas protegidas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python, Flask, Jinja2
* **Frontend:** HTML5, Tailwind CSS (via CDN), Font Awesome
* **Scripting:** JavaScript Vanilla (manipulação do DOM, manipulação da área de transferência e filtro de busca)

---

## 📂 Estrutura do Projeto

```text
passguard/
├── app.py                # Aplicação Flask (rotas e lógica principal)
├── static/               # Arquivos estáticos (uploads de foto de perfil)
│   └── uploads/
└── templates/            # Templates HTML (Jinja2)
    ├── base.html         # Layout base e navegação
    ├── dashboard.html    # Painel principal (gerador e cofre)
    ├── perfil.html       # Gerenciamento de perfil e fotos
    ├── login.html        # Autenticação de usuário
    └── register.html     # Cadastro de novos usuários
