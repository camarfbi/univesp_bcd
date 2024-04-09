import schedule
import time

def job():
    print("Executando o trabalho...")

# Agendar a execução do trabalho a cada minuto
schedule.every().minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
