import json
from datetime import datetime
import os

LIMITE_SAQUE = 500
LIMITE_SAQUES_DIARIOS = 3
TRANSACOES_FILE = "extrato.txt"
CLIENTES_FILE = "clientes.txt"

usuarios = []
contas = []

# ---------------- PERSISTÊNCIA ----------------

def salvar_clientes():
    dados = []
    for usuario in usuarios:
        contas_usuario = [c for c in contas if c["usuario"]["cpf"] == usuario["cpf"]]
        contas_serializaveis = []
        for c in contas_usuario:
            contas_serializaveis.append({
                "agencia": c["agencia"],
                "numero": c["numero"],
                "saldo": c["saldo"],
                "numero_saques": c.get("numero_saques", 0),
                "ativa": c.get("ativa", True)
            })
        dados.append({
            "cpf": usuario["cpf"],
            "nome": usuario["nome"],
            "nascimento": usuario["nascimento"],
            "endereco": usuario["endereco"],
            "senha": usuario["senha"],
            "contas": contas_serializaveis
        })
    with open(CLIENTES_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def carregar_clientes():
    global usuarios, contas
    if not os.path.exists(CLIENTES_FILE):
        return
    with open(CLIENTES_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)
    usuarios.clear()
    contas.clear()
    for usuario_data in dados:
        usuario = {
            "cpf": usuario_data["cpf"],
            "nome": usuario_data["nome"],
            "nascimento": usuario_data["nascimento"],
            "endereco": usuario_data["endereco"],
            "senha": usuario_data["senha"]
        }
        usuarios.append(usuario)
        for c in usuario_data.get("contas", []):
            conta = {
                "agencia": c["agencia"],
                "numero": c["numero"],
                "usuario": usuario,
                "saldo": c["saldo"],
                "numero_saques": c.get("numero_saques", 0),
                "ativa": c.get("ativa", True)
            }
            contas.append(conta)

# ---------------- UTILITÁRIOS ----------------

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("Pressione Enter para continuar...")

def aplicar_cor(texto, tipo):
    if tipo == "positivo":
        return f"\033[92m{texto}\033[0m"
    elif tipo == "negativo":
        return f"\033[91m{texto}\033[0m"
    return texto

def gerar_numero_conta():
    return max((c["numero"] for c in contas), default=0) + 1

def encontrar_usuario(*, cpf):
    return next((u for u in usuarios if u["cpf"] == cpf), None)

def encontrar_conta(*, numero):
    return next((c for c in contas if c["numero"] == numero), None)

def encontrar_contas_usuario(*, usuario):
    return [c for c in contas if c["usuario"] == usuario]

# ---------------- ARQUIVO EXTRATO ----------------

def salvar_transacao_arquivo(*, cpf_origem, tipo, valor, cpf_destino=None, conta_origem=None, conta_destino=None):
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    registro = {
        "data_hora": data_hora,
        "cpf_origem": cpf_origem,
        "tipo": tipo,
        "valor": valor,
        "cpf_destino": cpf_destino,
        "conta_origem": conta_origem,
        "conta_destino": conta_destino
    }
    with open(TRANSACOES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

# ---------------- USUÁRIO ----------------

def cadastrar_usuario():
    print("=== Cadastro de Usuário ===")
    cpf = input("CPF (somente números): ").strip()
    if encontrar_usuario(cpf=cpf):
        print(aplicar_cor("CPF já cadastrado.", "negativo"))
        return False

    nome = input("Nome completo: ").strip()
    nascimento = input("Data de nascimento (dd/mm/aaaa): ").strip()
    endereco = input("Endereço (logradouro, nº - bairro - cidade/UF): ").strip()
    senha = input("Senha para login: ").strip()

    usuario = {
        "cpf": cpf,
        "nome": nome,
        "nascimento": nascimento,
        "endereco": endereco,
        "senha": senha
    }
    usuarios.append(usuario)
    salvar_clientes()
    print(aplicar_cor("Usuário cadastrado com sucesso!", "positivo"))
    return True

def login():
    print("=== Login ===")
    cpf = input("CPF: ").strip()
    senha = input("Senha: ").strip()
    usuario = encontrar_usuario(cpf=cpf)
    if usuario and usuario["senha"] == senha:
        print(aplicar_cor(f"Login bem-sucedido! Bem-vindo(a), {usuario['nome']}.", "positivo"))
        return usuario
    print(aplicar_cor("CPF ou senha inválidos.", "negativo"))
    return None

# ---------------- CONTAS ----------------

def criar_conta(*, usuario):
    print("=== Criação de Conta Corrente ===")
    numero_conta = gerar_numero_conta()
    conta = {
        "agencia": "0001",
        "numero": numero_conta,
        "usuario": usuario,
        "saldo": 0.0,
        "numero_saques": 0,
        "ativa": True
    }
    contas.append(conta)
    salvar_clientes()
    print(aplicar_cor(f"Conta criada! Número: {numero_conta:04d}", "positivo"))

def listar_contas_usuario(*, usuario):
    user_contas = encontrar_contas_usuario(usuario=usuario)
    print("=== Suas Contas ===")
    if not user_contas:
        print(aplicar_cor("Nenhuma conta encontrada.", "negativo"))
    else:
        for c in user_contas:
            status = "Ativa" if c["ativa"] else "Inativa"
            print(f"Conta: {c['numero']:04d} | Saldo: R$ {c['saldo']:.2f} | Status: {status}")

def escolher_conta_usuario(*, usuario):
    listar_contas_usuario(usuario=usuario)
    try:
        numero = int(input("Digite o número da sua conta: "))
        conta = encontrar_conta(numero=numero)
        if conta and conta["usuario"] == usuario:
            return conta
        print(aplicar_cor("Conta não encontrada ou não pertence a você.", "negativo"))
    except ValueError:
        print(aplicar_cor("Entrada inválida.", "negativo"))
    return None

def escolher_conta_banco(*, conta_origem=None):
    print("=== Contas disponíveis para destino ===")
    contas_disponiveis = [c for c in contas if c["ativa"] and c != conta_origem]
    if not contas_disponiveis:
        print(aplicar_cor("Nenhuma conta disponível para transferência.", "negativo"))
        return None
    else:
        for c in contas_disponiveis:
            titular = c["usuario"]["nome"]
            print(f"Conta: {c['numero']:04d} | Titular: {titular} | Saldo: R$ {c['saldo']:.2f}")
    try:
        numero = int(input("Digite o número da conta destino: "))
        conta = next((c for c in contas_disponiveis if c["numero"] == numero), None)
        if conta:
            return conta
        print(aplicar_cor("Conta não encontrada.", "negativo"))
    except ValueError:
        print(aplicar_cor("Entrada inválida.", "negativo"))
    return None

# ---------------- OPERAÇÕES ----------------

def depositar(*, conta):
    if not conta["ativa"]:
        print(aplicar_cor("Conta inativa.", "negativo"))
        return
    try:
        valor = float(input("Valor do depósito: R$ "))
        if valor <= 0:
            print(aplicar_cor("Valor inválido.", "negativo"))
        else:
            conta["saldo"] += valor
            salvar_transacao_arquivo(cpf_origem=conta["usuario"]["cpf"], tipo="Depósito", valor=valor, conta_origem=conta["numero"])
            salvar_clientes()
            print(aplicar_cor("Depósito realizado com sucesso.", "positivo"))
    except ValueError:
        print(aplicar_cor("Entrada inválida.", "negativo"))

def sacar(*, conta):
    if not conta["ativa"]:
        print(aplicar_cor("Conta inativa.", "negativo"))
        return
    if conta["numero_saques"] >= LIMITE_SAQUES_DIARIOS:
        print(aplicar_cor("Limite de saques diários atingido.", "negativo"))
        return
    if conta["saldo"] <= 0:
        print(aplicar_cor("Saldo insuficiente.", "negativo"))
        return
    try:
        valor = float(input("Valor do saque: R$ "))
        if valor <= 0:
            print(aplicar_cor("Valor inválido.", "negativo"))
        elif valor > conta["saldo"]:
            print(aplicar_cor("Saldo insuficiente.", "negativo"))
        elif valor > LIMITE_SAQUE:
            print(aplicar_cor(f"Limite de R$ {LIMITE_SAQUE:.2f} excedido.", "negativo"))
        else:
            conta["saldo"] -= valor
            conta["numero_saques"] += 1
            salvar_transacao_arquivo(cpf_origem=conta["usuario"]["cpf"], tipo="Saque", valor=valor, conta_origem=conta["numero"])
            salvar_clientes()
            print(aplicar_cor("Saque realizado com sucesso.", "positivo"))
    except ValueError:
        print(aplicar_cor("Entrada inválida.", "negativo"))

def transferir(*, usuario):
    print("=== Escolha sua conta de origem ===")
    conta_origem = escolher_conta_usuario(usuario=usuario)
    if not conta_origem or not conta_origem["ativa"]:
        print(aplicar_cor("Conta de origem inválida ou inativa.", "negativo"))
        pausar()
        return

    print(f"Sua conta origem: Conta {conta_origem['numero']:04d} | Saldo: R$ {conta_origem['saldo']:.2f}")

    print("=== Escolha a conta destino ===")
    conta_destino = escolher_conta_banco(conta_origem=conta_origem)
    if not conta_destino or not conta_destino["ativa"]:
        print(aplicar_cor("Conta de destino inválida ou inativa.", "negativo"))
        pausar()
        return

    try:
        valor = float(input("Informe o valor da transferência: R$ "))
        if valor <= 0:
            print(aplicar_cor("Valor inválido.", "negativo"))
        elif valor > conta_origem["saldo"]:
            print(aplicar_cor("Saldo insuficiente.", "negativo"))
        else:
            conta_origem["saldo"] -= valor
            conta_destino["saldo"] += valor
            salvar_transacao_arquivo(
                cpf_origem=conta_origem["usuario"]["cpf"],
                tipo="Transferência Enviada",
                valor=valor,
                cpf_destino=conta_destino["usuario"]["cpf"],
                conta_origem=conta_origem["numero"],
                conta_destino=conta_destino["numero"]
            )
            salvar_transacao_arquivo(
                cpf_origem=conta_destino["usuario"]["cpf"],
                tipo="Transferência Recebida",
                valor=valor,
                conta_origem=conta_destino["numero"]
            )
            salvar_clientes()
            print(aplicar_cor("Transferência realizada com sucesso.", "positivo"))
    except ValueError:
        print(aplicar_cor("Entrada inválida.", "negativo"))
    pausar()

def inativar_conta(*, conta):
    if conta["saldo"] > 0:
        print(aplicar_cor("Conta com saldo positivo. Saque ou transfira o valor antes de inativar.", "negativo"))
        return
    if not conta["ativa"]:
        print(aplicar_cor("Conta já está inativa.", "negativo"))
        return
    conta["ativa"] = False
    salvar_clientes()
    print(aplicar_cor("Conta inativada com sucesso.", "positivo"))

def excluir_conta(*, conta):
    if conta["saldo"] > 0:
        print(aplicar_cor("Conta com saldo positivo. Saque ou transfira o valor antes de excluir.", "negativo"))
        return
    contas.remove(conta)
    salvar_clientes()
    print(aplicar_cor("Conta excluída com sucesso.", "positivo"))

def mostrar_extrato_usuario(*, usuario):
    print("=== Extrato Completo do Usuário ===")
    if not os.path.exists(TRANSACOES_FILE):
        print(aplicar_cor("Nenhuma movimentação encontrada.", "negativo"))
        return

    user_contas = encontrar_contas_usuario(usuario=usuario)
    contas_usuario_numeros = [c["numero"] for c in user_contas]
    saldo_total = sum(c["saldo"] for c in user_contas)

    transacoes = []
    with open(TRANSACOES_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            try:
                registro = json.loads(linha)
                if registro["cpf_origem"] == usuario["cpf"] or (registro.get("conta_origem") in contas_usuario_numeros):
                    data_hora = registro["data_hora"]
                    conta_info = f"[conta: {registro.get('conta_origem', '----'):04d}]"
                    tipo = registro["tipo"]
                    valor = registro["valor"]
                    linha_formatada = f"[{data_hora}] {conta_info} - {tipo}: R$ {valor:.2f}"
                    transacoes.append((data_hora, tipo, linha_formatada))
            except Exception:
                pass

    if transacoes:
        transacoes.sort(key=lambda x: x[0])
        for _, tipo, linha in transacoes:
            if "Depósito" in tipo or "Recebida" in tipo:
                print(aplicar_cor(linha, "positivo"))
            elif "Saque" in tipo or "Enviada" in tipo:
                print(aplicar_cor(linha, "negativo"))
            else:
                print(linha)
        print(f"\nSaldo TOTAL de todas as contas: R$ {saldo_total:.2f}")
    else:
        print(aplicar_cor("Nenhuma movimentação encontrada para suas contas.", "negativo"))

# ---------------- MENU PRINCIPAL ----------------

def menu_usuario_logado(usuario):
    while True:
        limpar_tela()
        print(f"=== Bem-vindo(a), {usuario['nome']} ===")
        print("""
 [1] Criar nova conta
 [2] Listar suas contas
 [3] Depositar
 [4] Sacar
 [5] Transferir
 [6] Ver Extrato
 [7] Inativar Conta
 [8] Excluir Conta
 [0] Sair
""")
        opcao = input("Escolha uma opção: ").strip()
        limpar_tela()

        if opcao == "1":
            criar_conta(usuario=usuario)
            pausar()
        elif opcao == "2":
            listar_contas_usuario(usuario=usuario)
            pausar()
        elif opcao == "3":
            conta = escolher_conta_usuario(usuario=usuario)
            if conta:
                depositar(conta=conta)
            pausar()
        elif opcao == "4":
            conta = escolher_conta_usuario(usuario=usuario)
            if conta:
                sacar(conta=conta)
            pausar()
        elif opcao == "5":
            transferir(usuario=usuario)
        elif opcao == "6":
            mostrar_extrato_usuario(usuario=usuario)
            pausar()
        elif opcao == "7":
            conta = escolher_conta_usuario(usuario=usuario)
            if conta:
                inativar_conta(conta=conta)
            pausar()
        elif opcao == "8":
            conta = escolher_conta_usuario(usuario=usuario)
            if conta:
                excluir_conta(conta=conta)
            pausar()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print(aplicar_cor("Opção inválida.", "negativo"))
            pausar()

# ---------------- INÍCIO ----------------

carregar_clientes()

if not usuarios:
    print("Nenhum usuário cadastrado. Cadastre o primeiro usuário.")
    while not cadastrar_usuario():
        pass

while True:
    limpar_tela()
    print("=== Sistema Bancário ===")
    print("""
 [1] Login
 [2] Cadastrar Novo Usuário
 [0] Sair
""")
    opcao = input("Escolha uma opção: ").strip()
    limpar_tela()

    if opcao == "1":
        usuario = login()
        if usuario:
            menu_usuario_logado(usuario)
    elif opcao == "2":
        cadastrar_usuario()
        pausar()
    elif opcao == "0":
        print("Saindo...")
        break
    else:
        print(aplicar_cor("Opção inválida.", "negativo"))
        pausar()
