menu = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair
=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

while True:
  print(menu)
  opcao = input("Escolha uma opção: ").lower().strip()
  
  switch opcao:
    case "d":
      print("Depósito")
      valor = float(input("Informe o valor do depósito: "))
    case "s":
      print("Saque")
      valor = float(input("Informe o valor do saque: "))
    case "e":
      print("Extrato")
      if not extrato:
        print("Não foram realizadas movimentações.")
      else:
        print(extrato)
    case "q":
      print("Saindo...")
      break
    case _:
      print("Opção inválida. Tente novamente.") 