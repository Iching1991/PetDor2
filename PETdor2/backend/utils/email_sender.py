# PetDor2/backend/utils/email_sender.py

import logging
import smtplib
from typing import Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.utils.config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
)

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Classe responsável pelo envio de e-mails usando as configurações SMTP definidas no projeto.
    """

    def __init__(
        self,
        servidor: str = SMTP_SERVIDOR,
        porta: int = SMTP_PORTA,
        email_origem: str = SMTP_EMAIL,
        senha: str = SMTP_SENHA,
        usar_ssl: bool = SMTP_USAR_SSL,
    ):
        self.servidor = servidor
        self.porta = porta
        self.email_origem = email_origem
        self.senha = senha
        self.usar_ssl = usar_ssl

    def _conectar(self) -> smtplib.SMTP:
        """
        Realiza a conexão com o servidor SMTP, usando SSL ou TLS conforme configuração.
        """
        try:
            if self.usar_ssl:
                server = smtplib.SMTP_SSL(self.servidor, self.porta)
            else:
                server = smtplib.SMTP(self.servidor, self.porta)
                server.starttls()

            server.login(self.email_origem, self.senha)
            return server

        except Exception as e:
            logger.error(f"Erro ao conectar ao servidor SMTP: {e}", exc_info=True)
            raise

    @staticmethod
    def _montar_email(assunto: str, corpo_texto: str, corpo_html: str, remetente: str, destinatario: str):
        """
        Monta a estrutura MIME do e-mail com versões texto e HTML.
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto

        msg.attach(MIMEText(corpo_texto, "plain"))
        msg.attach(MIMEText(corpo_html, "html"))

        return msg

    def enviar(
        self,
        destinatario: str,
        assunto: str,
        corpo_html: str,
        corpo_texto: str,
    ) -> Tuple[bool, str]:
        """
        Envia um e-mail utilizando HTML + texto simples.
        """
        try:
            if not destinatario:
                return False, "Endereço de e-mail do destinatário não fornecido."

            msg = self._montar_email(
                assunto=assunto,
                corpo_texto=corpo_texto,
                corpo_html=corpo_html,
                remetente=self.email_origem,
                destinatario=destinatario,
            )

            with self._conectar() as server:
                server.sendmail(self.email_origem, destinatario, msg.as_string())

            logger.info(f"📧 E-mail enviado para {destinatario} - Assunto: '{assunto}'")
            return True, "E-mail enviado com sucesso."

        except Exception as e:
            logger.error(
                f"❌ Falha ao enviar e-mail para {destinatario} - Assunto: '{assunto}': {e}",
                exc_info=True
            )
            return False, f"Erro ao enviar e-mail: {e}"


# =======================
# API compatível com versão antiga
# =======================

def enviar_email_confirmacao_generico(
    destinatario_email: str,
    assunto: str,
    corpo_html: str,
    corpo_texto: str
) -> Tuple[bool, str]:
    """
    Função mantida para garantir compatibilidade com código antigo.
    Internamente, utiliza a nova classe EmailSender.
    """
    sender = EmailSender()
    return sender.enviar(
        destinatario=destinatario_email,
        assunto=assunto,
        corpo_html=corpo_html,
        corpo_texto=corpo_texto,
    )
