from datetime import datetime
import os

# --- CONFIGURAÇÕES
LIMITE_SAQUE = 500
LIMITE_SAQUES_DIARIOS = 3

# --- VARIÁVEIS DE ESTADO
saldo = 0.0
extrato = ""
numero_saques = 0

# --- FUNÇÕES AUXILIARES

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("Pressione Enter para continuar...")

def registrar_transacao(tipo, valor):
    global extrato
    data_hora = datetime.now().strftime("[ %d-%m-%Y %H:%M:%S ] - ")
    cor = "\033[92m" if tipo == "Depósito" else "\033[91m"
    extrato += f"{cor}{data_hora}{tipo}: R$ {valor:.2f}\033[0m\n"

def mostrar_extrato():
    print("=== Extrato de movimentações ===")
    if not extrato:
        print("\033[91m - Não foram realizadas movimentações.\033[0m")
    else:
        print(extrato)
    cor_saldo = "\033[92m" if saldo > 0 else "\033[91m"
    print(f"\nSaldo atual: {cor_saldo}R$ {saldo:.2f}\033[0m")
    pausar()

def menu_principal():
    return """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair
=> """

# --- LOOP PRINCIPAL
while True:
    limpar_tela()
    print(menu_principal())
    opcao = input("Escolha uma opção: ").lower().strip()
    limpar_tela()

    if opcao == "d":
        print("=== Depósito ===")
        try:
            valor = float(input("Informe o valor do depósito: R$ "))
            if valor <= 0:
                print("\033[91mValor inválido. O valor do depósito deve ser positivo.\033[0m")
            else:
                saldo += valor
                registrar_transacao("Depósito", valor)
                print(f"\033[92mDepósito de R$ {valor:.2f} realizado com sucesso.\033[0m")
        except ValueError:
            print("\033[91mEntrada inválida. Use apenas números.\033[0m")
        pausar()

    elif opcao == "s":
        print("=== Saque ===")
        if numero_saques >= LIMITE_SAQUES_DIARIOS:
            print("\033[91mNúmero máximo de saques diários atingido.\033[0m")
        elif saldo <= 0:
            print("\033[91mSaldo insuficiente para saque. Seu saldo é R$ 0.00.\033[0m")
        else:
            try:
                valor = float(input("Informe o valor do saque: R$ "))
                if valor <= 0:
                    print("\033[91mValor inválido. Use um valor positivo.\033[0m")
                elif valor > saldo:
                    print("\033[91mSaldo insuficiente para o valor do saque.\033[0m")
                elif valor > LIMITE_SAQUE:
                    print(f"\033[91mValor do saque excede o limite de R$ {LIMITE_SAQUE:.2f}.\033[0m")
                else:
                    saldo -= valor
                    numero_saques += 1
                    registrar_transacao("Saque", valor)
                    print(f"\033[91mSaque de R$ {valor:.2f} realizado com sucesso.\033[0m")
            except ValueError:
                print("\033[91mEntrada inválida. Use apenas números.\033[0m")
        pausar()

    elif opcao == "e":
        mostrar_extrato()

    elif opcao == "q":
        print("Saindo...")
        break

    else:
        print("\033[91mOpção inválida. Tente novamente.\033[0m")
        pausar()
