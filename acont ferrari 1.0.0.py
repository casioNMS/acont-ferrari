import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from collections import defaultdict

import matplotlib.pyplot as plt
from tkcalendar import Calendar

ARQUIVO_SALVAMENTO = "dados_cigarros.json"


class Main:

    def __init__(self, root):

        self.root = root
        self.root.title("acont ferrari 1.0.0")
        self.root.geometry("900x650")
        self.root.configure(bg="#202020")
        self.root.state("zoomed")

        self.quantidade = tk.IntVar(value=1)
        self.itens = []
        self.total = 0.0

        # MARCA
        tk.Label(root, text="Marca:", bg="#202020", fg="white").grid(row=0, column=0)
        self.marca_entry = tk.Entry(root)
        self.marca_entry.grid(row=0, column=1)

        # PREÇO
        tk.Label(root, text="Preço:", bg="#202020", fg="white").grid(row=1, column=0)
        self.preco_entry = tk.Entry(root)
        self.preco_entry.grid(row=1, column=1)

        # DATA
        tk.Label(root, text="Data:", bg="#202020", fg="white").grid(row=2, column=0)

        self.data_entry = tk.Entry(root)
        self.data_entry.grid(row=2, column=1)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Button(root, text="📅", command=self.abrir_calendario).grid(row=2, column=2)

        # QUANTIDADE
        tk.Label(root, text="Quantidade:", bg="#202020", fg="white").grid(row=3, column=0)

        tk.Label(root, textvariable=self.quantidade, bg="#202020",
                 fg="cyan", font=("Arial", 12, "bold")).grid(row=3, column=1)

        tk.Button(root, text="+", command=self.aumentar).grid(row=3, column=2)
        tk.Button(root, text="-", command=self.diminuir).grid(row=3, column=3)

        # BOTÕES
        tk.Button(root, text="Adicionar", command=self.adicionar_item,
                  bg="green", fg="white").grid(row=4, column=0)

        tk.Button(root, text="Remover", command=self.remover_item,
                  bg="red", fg="white").grid(row=4, column=1)

        tk.Button(root, text="📊 Gráficos", command=self.menu_graficos,
                  bg="blue", fg="white").grid(row=4, column=2)

        tk.Button(root, text="Gastos por ano", command=self.ver_gastos_anuais,
                  bg="purple", fg="white").grid(row=4, column=3)

        # TABELA
        self.tree = ttk.Treeview(
            root,
            columns=("marca", "preco", "qtd", "data", "total"),
            show="headings"
        )

        self.tree.heading("marca", text="Marca")
        self.tree.heading("preco", text="Preço")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("data", text="Data")
        self.tree.heading("total", text="Subtotal")

        self.tree.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

        # TOTAL
        self.total_label = tk.Label(
            root,
            text="Total: R$ 0",
            bg="#202020",
            fg="yellow",
            font=("Arial", 14, "bold")
        )

        self.total_label.grid(row=6, column=0, columnspan=4)

        self.carregar_dados()

        self.root.protocol("WM_DELETE_WINDOW", self.fechar)

    # QUANTIDADE
    def aumentar(self):
        self.quantidade.set(self.quantidade.get() + 1)

    def diminuir(self):
        if self.quantidade.get() > 1:
            self.quantidade.set(self.quantidade.get() - 1)

    # CALENDÁRIO
    def abrir_calendario(self):

        top = tk.Toplevel(self.root)

        cal = Calendar(top, date_pattern="dd/mm/yyyy")
        cal.pack()

        def pegar_data():
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, cal.get_date())
            top.destroy()

        tk.Button(top, text="Selecionar", command=pegar_data).pack()

    # ADICIONAR
    def adicionar_item(self):

        marca = self.marca_entry.get()
        preco = self.preco_entry.get()
        data = self.data_entry.get()
        qtd = self.quantidade.get()

        if not marca or not preco:
            messagebox.showwarning("Erro", "Preencha marca e preço")
            return

        try:
            preco = float(preco)
        except:
            messagebox.showerror("Erro", "Preço inválido")
            return

        subtotal = preco * qtd

        item = {
            "marca": marca,
            "preco": preco,
            "quantidade": qtd,
            "data": data,
            "subtotal": subtotal
        }

        self.itens.append(item)

        self.tree.insert("", "end", values=(
            marca,
            f"{preco:.2f}",
            qtd,
            data,
            f"{subtotal:.2f}"
        ))

        self.total += subtotal

        self.total_label.config(text=f"Total: R$ {self.total:.2f}")

        self.salvar()

    # REMOVER
    def remover_item(self):

        sel = self.tree.selection()

        if not sel:
            return

        for s in sel:

            valores = self.tree.item(s)["values"]
            subtotal = float(valores[4])

            self.total -= subtotal

            self.tree.delete(s)

        self.total_label.config(text=f"Total: R$ {self.total:.2f}")

        self.salvar()

    # MENU DE GRÁFICOS
    def menu_graficos(self):

        win = tk.Toplevel(self.root)
        win.title("Gráficos")

        tk.Button(win, text="Vendas por Marca",
                  command=self.grafico_marcas).pack(fill="x")

        tk.Button(win, text="Vendas por Dia",
                  command=self.grafico_dias).pack(fill="x")

        tk.Button(win, text="Vendas por Mês",
                  command=self.grafico_meses).pack(fill="x")

        tk.Button(win, text="Ranking de Marcas",
                  command=self.ranking_marcas).pack(fill="x")

    # GRÁFICO MARCAS
    def grafico_marcas(self):

        dados = defaultdict(int)

        for i in self.itens:
            dados[i["marca"]] += i["quantidade"]

        plt.bar(dados.keys(), dados.values())
        plt.title("Vendas por Marca")
        plt.show()

    # GRÁFICO DIAS
    def grafico_dias(self):

        dados = defaultdict(int)

        for i in self.itens:
            dados[i["data"]] += i["quantidade"]

        plt.plot(list(dados.keys()), list(dados.values()), marker="o")
        plt.title("Vendas por Dia")
        plt.xticks(rotation=45)
        plt.show()

    # GRÁFICO MESES
    def grafico_meses(self):

        dados = defaultdict(int)

        for i in self.itens:

            try:
                data = datetime.strptime(i["data"], "%d/%m/%Y")
                mes = data.strftime("%m/%Y")
                dados[mes] += i["quantidade"]
            except:
                pass

        plt.bar(dados.keys(), dados.values())
        plt.title("Vendas por Mês")
        plt.show()

    # RANKING
    def ranking_marcas(self):

        dados = defaultdict(int)

        for i in self.itens:
            dados[i["marca"]] += i["quantidade"]

        ranking = sorted(dados.items(), key=lambda x: x[1], reverse=True)

        nomes = [r[0] for r in ranking]
        valores = [r[1] for r in ranking]

        plt.bar(nomes, valores)
        plt.title("Ranking de Marcas")
        plt.show()

    # GASTOS ANUAIS
    def ver_gastos_anuais(self):

        dados = defaultdict(float)

        for i in self.itens:

            try:
                ano = datetime.strptime(i["data"], "%d/%m/%Y").year
                dados[ano] += i["subtotal"]
            except:
                pass

        plt.plot(dados.keys(), dados.values())
        plt.title("Gastos por Ano")
        plt.show()

    # SALVAR
    def salvar(self):

        with open(ARQUIVO_SALVAMENTO, "w", encoding="utf-8") as f:
            json.dump({
                "itens": self.itens,
                "total": self.total
            }, f, indent=4)

    # CARREGAR
    def carregar_dados(self):

        if not os.path.exists(ARQUIVO_SALVAMENTO):
            return

        with open(ARQUIVO_SALVAMENTO, "r", encoding="utf-8") as f:

            dados = json.load(f)

            self.itens = dados.get("itens", [])
            self.total = dados.get("total", 0)

            for i in self.itens:

                self.tree.insert("", "end", values=(
                    i["marca"],
                    f"{i['preco']:.2f}",
                    i["quantidade"],
                    i["data"],
                    f"{i['subtotal']:.2f}"
                ))

            self.total_label.config(text=f"Total: R$ {self.total:.2f}")

    def fechar(self):

        self.salvar()
        self.root.destroy()


if __name__ == "__main__":

    root = tk.Tk()
    app = Main(root)
    root.mainloop()
