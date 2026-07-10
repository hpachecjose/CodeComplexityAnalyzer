import json
import os
from datetime import datetime


ARQUIVO = "tarefas.json"


class Tarefa:
    def __init__(self, titulo, descricao="", concluida=False, data_criacao=None):
        self.titulo = titulo
        self.descricao = descricao
        self.concluida = concluida
        self.data_criacao = data_criacao or datetime.now().strftime("%d/%m/%Y %H:%M")

    def concluir(self):
        self.concluida = True

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "descricao": self.descricao,
            "concluida": self.concluida,
            "data_criacao": self.data_criacao
        }

    @staticmethod
    def from_dict(dados):
        return Tarefa(
            dados["titulo"],
            dados["descricao"],
            dados["concluida"],
            dados["data_criacao"]
        )


class GerenciadorTarefas:

    def __init__(self):
        self.tarefas = []
        self.carregar()

    def adicionar(self, tarefa):
        self.tarefas.append(tarefa)
        self.salvar()

    def listar(self):
        if not self.tarefas:
            print("\nNenhuma tarefa cadastrada.")
            return

        print("\n--- LISTA DE TAREFAS ---")

        for indice, tarefa in enumerate(self.tarefas, start=1):
            status = "✓" if tarefa.concluida else "✗"

            print(f"""
{indice}. [{status}] {tarefa.titulo}
Descrição: {tarefa.descricao}
Criada em: {tarefa.data_criacao}
""")

    def concluir_tarefa(self, indice):
        try:
            tarefa = self.tarefas[indice - 1]
            tarefa.concluir()
            self.salvar()
            print("Tarefa concluída.")

        except IndexError:
            print("Tarefa inexistente.")

    def remover(self, indice):
        try:
            self.tarefas.pop(indice - 1)
            self.salvar()
            print("Tarefa removida.")

        except IndexError:
            print("Tarefa inexistente.")

    def salvar(self):
        with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
            json.dump(
                [t.to_dict() for t in self.tarefas],
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    def carregar(self):
        if not os.path.exists(ARQUIVO):
            return

        try:
            with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

                self.tarefas = [
                    Tarefa.from_dict(item)
                    for item in dados
                ]

        except json.JSONDecodeError:
            print("Arquivo corrompido. Criando novo banco.")


def menu():

    sistema = GerenciadorTarefas()

    while True:

        print("""
========================
 GERENCIADOR DE TAREFAS
========================

1 - Listar tarefas
2 - Adicionar tarefa
3 - Concluir tarefa
4 - Remover tarefa
5 - Sair
""")

        opcao = input("Escolha: ")

        if opcao == "1":
            sistema.listar()

        elif opcao == "2":

            titulo = input("Título: ")
            descricao = input("Descrição: ")

            tarefa = Tarefa(
                titulo,
                descricao
            )

            sistema.adicionar(tarefa)

            print("Tarefa adicionada.")

        elif opcao == "3":

            sistema.listar()

            numero = int(
                input("Número da tarefa: ")
            )

            sistema.concluir_tarefa(numero)


        elif opcao == "4":

            sistema.listar()

            numero = int(
                input("Número da tarefa: ")
            )

            sistema.remover(numero)


        elif opcao == "5":
            print("Encerrando...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()