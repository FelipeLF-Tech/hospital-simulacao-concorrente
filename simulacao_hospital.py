"""Simulacao didatica de concorrencia; nomes e eventos sao ficticios."""
import argparse
import multiprocessing as mp
import queue
import random
from contextlib import contextmanager, ExitStack
from datetime import datetime
import time

@contextmanager
def recurso(pool):
    item = pool.get(timeout=60)
    try:
        yield item
    finally:
        pool.put(item)

def paciente(numero, medicos, salas, leitos, logs, escala):
    def registrar(texto):
        logs.put((numero, datetime.now().isoformat(timespec='milliseconds'), texto))
    try:
        registrar('Chegada')
        with recurso(medicos) as medico:
            registrar(f'Consulta: {medico}')
            time.sleep(random.uniform(1, 3) * escala)
        registrar('Exame')
        time.sleep(random.uniform(2, 4) * escala)
        if random.choice((True, False)):
            with recurso(medicos) as medico:
                with recurso(salas) as sala:
                    registrar(f'Cirurgia: {medico}, {sala}')
                    time.sleep(random.uniform(4, 8) * escala)
            with recurso(leitos) as leito:
                with recurso(medicos) as medico:
                    registrar(f'Recuperacao: {leito}, {medico}')
                    time.sleep(random.uniform(3, 6) * escala)
        registrar('Alta')
    except Exception as exc:
        registrar(f'ERRO: {exc}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pacientes', type=int, default=25)
    parser.add_argument('--escala-tempo', type=float, default=1)
    parser.add_argument('--saida', default='relatorio_final_simulacao.txt')
    args = parser.parse_args()
    if args.pacientes < 1 or args.escala_tempo < 0:
        parser.error('pacientes deve ser positivo e escala-tempo nao negativa')
    ctx = mp.get_context('spawn')
    # Filas compartilhadas e consumo concorrente dos logs.
    with ExitStack() as cleanup:
        medicos, salas, leitos, logs = [ctx.Queue() for _ in range(4)]
        for pool, quantidade, nome in ((medicos, 5, 'Medico'), (salas, 2, 'Sala'), (leitos, 10, 'Leito')):
            for i in range(quantidade):
                pool.put(f'{nome} {i+1}')
        processos = [ctx.Process(target=paciente, args=(i+1, medicos, salas, leitos, logs, args.escala_tempo)) for i in range(args.pacientes)]
        for processo in processos:
            processo.start()
        eventos = []
        # Consome logs enquanto produtores executam; nunca depende de Queue.empty().
        while any(processo.is_alive() for processo in processos):
            try:
                eventos.append(logs.get(timeout=0.05))
            except queue.Empty:
                pass
        for processo in processos:
            processo.join()
        while True:
            try:
                eventos.append(logs.get_nowait())
            except queue.Empty:
                break
        with open(args.saida, 'w', encoding='utf-8') as arquivo:
            for numero, horario, mensagem in sorted(eventos, key=lambda e: (e[0], e[1])):
                arquivo.write(f'Paciente {numero} | {horario} | {mensagem}\n')
        if any(processo.exitcode != 0 for processo in processos):
            raise RuntimeError('Um processo falhou; consulte o relatorio')
        print(f'{len(eventos)} eventos registrados em {args.saida}')

if __name__ == '__main__':
    mp.freeze_support()
    main()

