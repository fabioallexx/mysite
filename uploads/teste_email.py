import yagmail

# Criar o cliente yagmail
yag = yagmail.SMTP('cmmoita.stgi.est2@outlook.pt', '*cmMoita.2024')

emails = input("Digite os emails (um por linha, termine com 'fim'):\n").splitlines()
subject = input("Digite o assunto do email:\n")
body_template = input("Digite o corpo do email (use {email} para o email do destinatário):\n")

for email_receiver in emails:
    if email_receiver.strip().lower() == 'fim':
        break
    body = body_template.format(email=email_receiver)
    yag.send(to=email_receiver, subject=subject, contents=body)
    print(f'Email enviado para {email_receiver} com sucesso!')