import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st
import logging

logger = logging.getLogger(__name__)


# ===============================
# Função interna de envio SMTP
# ===============================
def _enviar_email(destinatario, assunto, html):
    try:
        smtp_server = st.secrets["EMAIL"]["SMTP_SERVER"]
        smtp_port = st.secrets["EMAIL"]["SMTP_PORT"]
        smtp_user = st.secrets["EMAIL"]["SMTP_USER"]    # relatorio@petdor.app
        smtp_pass = st.secrets["EMAIL"]["SMTP_PASS"]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = smtp_user
        msg["To"] = destinatario

        msg.attach(MIMEText(html, "html", "utf-8"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, destinatario, msg.as_string())
        server.quit()

        logger.info(f"[EMAIL] Enviado com sucesso para {destinatario}")
        return True

    except Exception as e:
        logger.error(f"[ERRO EMAIL] Falha ao enviar e-mail: {e}")
        return False


# ===============================
# Template HTML padrão
# ===============================
def _template_base(titulo, corpo_html):
    return f"""
    <div style="background:#f7f7f7;padding:25px;font-family:Arial;">
        <div style="max-width:600px;margin:auto;background:#ffffff;padding:25px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.1);">
            <h2 style="color:#1a73e8;text-align:center;margin-bottom:20px;">{titulo}</h2>

            <div style="font-size:15px;color:#333;line-height:1.6;">
                {corpo_html}
            </div>

            <br><hr style="border:none;border-top:1px solid #ddd;">
            <p style="font-size:12px;text-align:center;color:#888;margin-top:10px;">
                PETDor • Sistema de Avaliação de Dor Animal<br>
                Este e-mail foi enviado automaticamente. Não responda.
            </p>
        </div>
    </div>
    """


# ===============================
# CONFIRMAÇÃO DE CADASTRO
# ===============================
def enviar_email_confirmacao(email, nome, token):
    link = f"https://petdor.streamlit.app/confirmar_email?token={token}"

    corpo = f"""
        <p>Olá <b>{nome}</b>,</p>
        <p>Obrigado por se cadastrar no <b>PETDor</b>! Para ativar sua conta, clique no botão abaixo:</p>

        <p style="text-align:center;margin-top:30px;">
            <a href="{link}" 
               style="background:#1a73e8;color:white;padding:15px 25px;
                      text-decoration:none;border-radius:8px;font-size:16px;">
                Confirmar Cadastro
            </a>
        </p>

        <p style="margin-top:25px;">Ou copie e cole o link no navegador:</p>
        <p>{link}</p>
    """

    html = _template_base("Confirmação de Cadastro", corpo)
    return _enviar_email(email, "Confirme seu cadastro - PETDor", html)


# ===============================
# E-MAIL DE RESET DE SENHA
# ===============================
def enviar_email_reset(email, token):
    link = f"https://petdor.streamlit.app/reset_senha?token={token}"

    corpo = f"""
        <p>Você solicitou a redefinição da sua senha no <b>PETDor</b>.</p>
        <p>Clique no botão abaixo para redefinir:</p>

        <p style="text-align:center;margin-top:30px;">
            <a href="{link}"
               style="background:#e37400;color:white;padding:15px 25px;
                      text-decoration:none;border-radius:8px;font-size:16px;">
                Redefinir Senha
            </a>
        </p>

        <p style="margin-top:25px;">Ou copie e cole o link no navegador:</p>
        <p>{link}</p>
    """

    html = _template_base("Redefinição de Senha", corpo)
    return _enviar_email(email, "Redefinir senha - PETDor", html)
