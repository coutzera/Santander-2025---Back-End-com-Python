#!/usr/bin/env python3

from typing import Callable

def clear_screen():
    """Limpa o terminal (portável entre Windows/Linux/macOS)."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def show_header(title: str) -> None:
    print("=" * 40)
    print(f"{title:^40}")
    print("=" * 40)


def show_menu() -> None:
    """Exibe o menu principal do sistema bancário."""
    show_header("SISTEMA BANCÁRIO - MENU PRINCIPAL")
    print("1. Consultar saldo")
    print("2. Realizar saque")
    print("3. Fazer depósito")
    print("4. Sair")
    print()


def consultar_saldo(saldo: float) -> float:
    print(f"\nSeu saldo atual é: R$ {saldo:.2f}\n")
    return saldo


def realizar_saque(saldo: float) -> float:
    try:
        valor = float(input("Informe o valor para saque: R$ "))
        if valor <= 0:
            print("Valor inválido. Tente novamente.\n")
        elif valor > saldo:
            print("Saldo insuficiente.\n")
        else:
            saldo -= valor
            print(f"Saque de R$ {valor:.2f} realizado com sucesso.\n")
    except ValueError:
        print("Entrada inválida. Digite um número.\n")
    return saldo


def fazer_deposito(saldo: float) -> float:
    try:
        valor = float(input("Informe o valor para depósito: R$ "))
        if valor <= 0:
            print("Valor inválido. Tente novamente.\n")
        else:
            saldo += valor
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.\n")
    except ValueError:
        print("Entrada inválida. Digite um número.\n")
    return saldo


def main() -> None:
    saldo = 1000.00  # Saldo inicial fictício
    opcoes: dict[str, Callable[[float], float]] = {
        "1": consultar_saldo,
        "2": realizar_saque,
        "3": fazer_deposito,
    }

    while True:
        clear_screen()
        show_menu()
        opcao = input("Selecione uma opção: ").strip()

        if opcao == "4":
            print("\nObrigado por utilizar o sistema bancário. Até logo!\n")
            break

        func = opcoes.get(opcao)
        if func:
            saldo = func(saldo)
        else:
            print("\nOpção inválida. Tente novamente.\n")

        input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    main()
