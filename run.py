import os
import sys
import subprocess

QUESTOES = {
    "q1": "Questao 1/questao1.py",
    "q2": "Questao 2/questao2.py",
    "q5": "Questao 5/teste_unit.py",
    "q6": "Questao 6/questao6.py",
    "q4": "Questao 4/questao4.py",  # ajuste se necessário
}

def main():
    if len(sys.argv) < 2:
        print("Uso: python run.py <questao> [argumentos]")
        return

    questao = sys.argv[1]           # ex: q2
    args = sys.argv[2:]             # argumentos extras passados após q2

    if questao not in QUESTOES:
        print(f"Questão '{questao}' inválida. Use: {', '.join(QUESTOES.keys())}")
        return

    caminho_script = QUESTOES[questao]

    print(f"▶ Executando {caminho_script} com argumentos: {args}\n")

    # Monta comando: python script.py arg1 arg2 arg3...
    comando = ["python", caminho_script] + args

    subprocess.run(comando)

if __name__ == "__main__":
    main()
