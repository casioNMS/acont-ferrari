import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from collections import defaultdict
from tkcalendar import Calendar

ARQUIVO_SALVAMENTO = "dados_cigarros.json"


class Main:

    def __init__(self, root):

        self.root = root
        self.root.title("acont ferrari 1.2.2")
        self.root.geometry("900x650")
        self.root.configure(bg="#202020")
        self.root.state("zoomed")

        self.quantidade = tk.IntVar(value=1)
        self.itens = []
        self.total = 0.0

        tk.Label(root, text="Marca:", bg="#202020", fg="white").grid(row=0, column=0)
        self.marca_entry = tk.Entry(root)
        self.marca_entry.grid(row=0, column=1)

        tk.Label(root, text="Preço:", bg="#202020", fg="white").grid(row=1, column=0)
        self.preco_entry = tk.Entry(root)
        self.preco_entry.grid(row=1, column=1)

        tk.Label(root, text="Data:", bg="#202020", fg="white").grid(row=2, column=0)

        self.data_entry = tk.Entry(root)
        self.data_entry.grid(row=2, column=1)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Button(root, text="📅", command=self.abrir_calendario).grid(row=2, column=2)

        tk.Label(root, text="Quantidade:", bg="#202020", fg="white").grid(row=3, column=0)

        tk.Label(root, textvariable=self.quantidade,
                 bg="#202020", fg="cyan",
                 font=("Arial", 12, "bold")).grid(row=3, column=1)

        tk.Button(root, text="+", command=self.aumentar).grid(row=3, column=2)
        tk.Button(root, text="-", command=self.diminuir).grid(row=3, column=3)

        tk.Button(root, text="Adicionar", command=self.adicionar_item,
                  bg="green", fg="white").grid(row=4, column=0)

        tk.Button(root, text="Remover", command=self.remover_item,
                  bg="red", fg="white").grid(row=4, column=1)

        tk.Button(root, text="📊 Relatórios", command=self.menu_graficos,
                  bg="blue", fg="white").grid(row=4, column=2)

        tk.Button(root, text="Relatório anual", command=self.ver_gastos_anuais,
                  bg="purple", fg="white").grid(row=4, column=3)

        # ---------------- PESQUISA ----------------

        tk.Label(root, text="Pesquisar:", bg="#202020", fg="white").grid(row=5, column=0)

        self.pesquisa_entry = tk.Entry(root)
        self.pesquisa_entry.grid(row=5, column=1)

        tk.Button(root, text="Pesquisar", command=self.pesquisar).grid(row=5, column=2)

        tk.Button(root, text="Limpar", command=self.mostrar_todos).grid(row=5, column=3)

        # ---------------- TABELA ----------------

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

        self.tree.grid(row=6, column=0, columnspan=4, padx=10, pady=10)

        self.total_label = tk.Label(
            root,
            text="Total: R$ 0",
            bg="#202020",
            fg="yellow",
            font=("Arial", 14, "bold")
        )

        self.total_label.grid(row=7, column=0, columnspan=4)

        self.carregar_dados()

        self.root.protocol("WM_DELETE_WINDOW", self.fechar)

    # ---------------- CONTROLES ----------------

    def aumentar(self):
        self.quantidade.set(self.quantidade.get() + 1)

    def diminuir(self):
        if self.quantidade.get() > 1:
            self.quantidade.set(self.quantidade.get() - 1)

    # ---------------- CALENDARIO ----------------

    def abrir_calendario(self):

        top = tk.Toplevel(self.root)

        cal = Calendar(top, date_pattern="dd/mm/yyyy")
        cal.pack()

        def pegar_data():
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, cal.get_date())
            top.destroy()

        tk.Button(top, text="Selecionar", command=pegar_data).pack()

    # ---------------- ADICIONAR ----------------

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
            marca, f"{preco:.2f}", qtd, data, f"{subtotal:.2f}"
        ))

        self.total += subtotal
        self.total_label.config(text=f"Total: R$ {self.total:.2f}")

        self.salvar()

    # ---------------- REMOVER ----------------

    def remover_item(self):

        sel = self.tree.selection()

        if not sel:
            return

        for s in sel:

            valores = self.tree.item(s)["values"]

            marca = valores[0]
            preco = float(valores[1])
            qtd = int(valores[2])
            data = valores[3]
            subtotal = float(valores[4])

            self.total -= subtotal

            for item in self.itens:
                if (
                    item["marca"] == marca
                    and item["preco"] == preco
                    and item["quantidade"] == qtd
                    and item["data"] == data
                ):
                    self.itens.remove(item)
                    break

            self.tree.delete(s)

        self.total_label.config(text=f"Total: R$ {self.total:.2f}")

        self.salvar()

    # ---------------- PESQUISA ----------------

    def pesquisar(self):

        termo = self.pesquisa_entry.get().lower()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in self.itens:

            texto = f"{item['marca']} {item['data']} {item['preco']}"

            if termo in texto.lower():

                self.tree.insert("", "end", values=(
                    item["marca"],
                    f"{item['preco']:.2f}",
                    item["quantidade"],
                    item["data"],
                    f"{item['subtotal']:.2f}"
                ))

    def mostrar_todos(self):

        self.pesquisa_entry.delete(0, tk.END)

        for i in self.tree.get_children():
            self.tree.delete(i)

        for i in self.itens:

            self.tree.insert("", "end", values=(
                i["marca"],
                f"{i['preco']:.2f}",
                i["quantidade"],
                i["data"],
                f"{i['subtotal']:.2f}"
            ))

    # ---------------- RELATORIOS ----------------

    def mostrar_relatorio(self, titulo, texto):

        win = tk.Toplevel(self.root)
        win.title(titulo)

        box = tk.Text(win, width=80, height=30)
        box.pack()

        box.insert("1.0", texto)
        box.config(state="disabled")

    def menu_graficos(self):

        win = tk.Toplevel(self.root)
        win.title("Relatórios")

        tk.Button(win, text="Vendas por Marca",
                  command=self.relatorio_marcas).pack(fill="x")

        tk.Button(win, text="Vendas por Dia",
                  command=self.relatorio_dias).pack(fill="x")

        tk.Button(win, text="Vendas por Mês",
                  command=self.relatorio_meses).pack(fill="x")

        tk.Button(win, text="Ranking de Marcas",
                  command=self.ranking_marcas).pack(fill="x")

    def relatorio_marcas(self):

        dados = defaultdict(int)

        for i in self.itens:
            dados[i["marca"]] += i["quantidade"]

        texto = "RELATÓRIO DE VENDAS POR MARCA\n\n"

        for marca, qtd in dados.items():
            texto += f"Marca: {marca}\nTotal vendido: {qtd} unidades\n\n"

        self.mostrar_relatorio("Vendas por Marca", texto)

    def relatorio_dias(self):

        dados = defaultdict(int)

        for i in self.itens:
            dados[i["data"]] += i["quantidade"]

        texto = "RELATÓRIO DE VENDAS POR DIA\n\n"

        for dia, qtd in dados.items():
            texto += f"Data: {dia}\nTotal vendido: {qtd}\n\n"

        self.mostrar_relatorio("Vendas por Dia", texto)

    def relatorio_meses(self):

        dados = defaultdict(int)

        for i in self.itens:
            data = datetime.strptime(i["data"], "%d/%m/%Y")
            mes = data.strftime("%m/%Y")
            dados[mes] += i["quantidade"]

        texto = "RELATÓRIO DE VENDAS POR MÊS\n\n"

        for mes, qtd in dados.items():
            texto += f"Mês: {mes}\nTotal vendido: {qtd}\n\n"

        self.mostrar_relatorio("Vendas por Mês", texto)

    def ranking_marcas(self):

        dados = defaultdict(int)

        for i in self.itens:
            dados[i["marca"]] += i["quantidade"]

        ranking = sorted(dados.items(), key=lambda x: x[1], reverse=True)

        texto = "RANKING DE MARCAS\n\n"

        pos = 1
        for marca, qtd in ranking:
            texto += f"{pos}º lugar: {marca} ({qtd} unidades)\n"
            pos += 1

        self.mostrar_relatorio("Ranking de Marcas", texto)

    def ver_gastos_anuais(self):

        dados = defaultdict(float)

        for i in self.itens:
            ano = datetime.strptime(i["data"], "%d/%m/%Y").year
            dados[ano] += i["subtotal"]

        texto = "RELATÓRIO DE GASTOS POR ANO\n\n"

        for ano, valor in dados.items():
            texto += f"Ano {ano}: R$ {valor:.2f}\n"

        self.mostrar_relatorio("Gastos por Ano", texto)

    # ---------------- SALVAR ----------------

    def salvar(self):

        with open(ARQUIVO_SALVAMENTO, "w", encoding="utf-8") as f:
            json.dump({
                "itens": self.itens,
                "total": self.total
            }, f, indent=4)

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
