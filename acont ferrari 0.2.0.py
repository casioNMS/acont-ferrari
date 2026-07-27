import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

ARQUIVO_SALVAMENTO = "dados_cigarros.json"

class Main:
    def __init__(self, root):
        self.root = root
        self.root.title("Acont Ferraari 0.2.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#202020")

        self.quantidade = tk.IntVar(value=1)
        self.itens = []
        self.total = 0.0

        # === CAMPOS ===
        tk.Label(root, text="Marca do cigarro:", bg="#202020", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.marca_entry = tk.Entry(root)
        self.marca_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Preço (R$):", bg="#202020", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.preco_entry = tk.Entry(root)
        self.preco_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Data (dd/mm/aaaa):", bg="#202020", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.data_entry = tk.Entry(root)
        self.data_entry.grid(row=2, column=1, padx=5, pady=5)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # === QUANTIDADE ===
        tk.Label(root, text="Quantidade:", bg="#202020", fg="white").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        tk.Label(root, textvariable=self.quantidade, bg="#202020", fg="cyan", font=("Arial", 12, "bold")).grid(row=3, column=1)
        tk.Button(root, text="+", command=self.aumentar).grid(row=3, column=2)
        tk.Button(root, text="-", command=self.diminuir).grid(row=3, column=3)

        # === BOTÕES ===
        tk.Button(root, text="Adicionar", command=self.adicionar_item, bg="green", fg="white").grid(row=4, column=1, pady=10)
        tk.Button(root, text="Remover Selecionado", command=self.remover_item, bg="red", fg="white").grid(row=4, column=2)
        tk.Button(root, text="Ver gastos por ano", command=self.ver_gastos_anuais, bg="blue", fg="white").grid(row=4, column=3)

        # === LISTA ===
        self.tree = ttk.Treeview(root, columns=("marca", "preco", "quantidade", "data", "total"), show="headings")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("preco", text="Preço (R$)")
        self.tree.heading("quantidade", text="Qtd")
        self.tree.heading("data", text="Data")
        self.tree.heading("total", text="Subtotal (R$)")
        self.tree.column("marca", width=150)
        self.tree.column("preco", width=80)
        self.tree.column("quantidade", width=60)
        self.tree.column("data", width=100)
        self.tree.column("total", width=100)
        self.tree.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

        # === TOTAL ===
        self.total_label = tk.Label(root, text="Total: R$ 0.00", bg="#202020", fg="yellow", font=("Arial", 14, "bold"))
        self.total_label.grid(row=6, column=0, columnspan=4, pady=10)

        # === CARREGAR SALVAMENTO ===
        self.carregar_dados()

        # Salvar automaticamente ao fechar
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_app)

    # === FUNÇÕES ===
    def aumentar(self):
        self.quantidade.set(self.quantidade.get() + 1)

    def diminuir(self):
        if self.quantidade.get() > 1:
            self.quantidade.set(self.quantidade.get() - 1)

    def adicionar_item(self):
        marca = self.marca_entry.get().strip()
        preco = self.preco_entry.get().strip()
        data = self.data_entry.get().strip()
        qtd = self.quantidade.get()

        if not marca or not preco:
            messagebox.showwarning("Aviso", "Preencha a marca e o preço!")
            return

        try:
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Digite um preço válido!")
            return

        subtotal = preco * qtd
        self.itens.append({
            "marca": marca,
            "preco": preco,
            "quantidade": qtd,
            "data": data,
            "subtotal": subtotal
        })

        self.tree.insert("", "end", values=(marca, f"{preco:.2f}", qtd, data, f"{subtotal:.2f}"))
        self.total += subtotal
        self.total_label.config(text=f"Total: R$ {self.total:.2f}")

        self.marca_entry.delete(0, "end")
        self.preco_entry.delete(0, "end")
        self.quantidade.set(1)

        self.salvar_dados()

    def remover_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Aviso", "Selecione um item para remover.")
            return
        for sel in selected:
            valores = self.tree.item(sel, "values")
            subtotal = float(valores[4])
            self.total -= subtotal
            marca = valores[0]
            self.tree.delete(sel)
            self.itens = [i for i in self.itens if i["marca"] != marca or i["subtotal"] != subtotal]
        self.total_label.config(text=f"Total: R$ {self.total:.2f}")
        self.salvar_dados()

    # === GASTOS POR ANO ===
    def ver_gastos_anuais(self):
        if not self.itens:
            messagebox.showinfo("Sem dados", "Nenhum dado disponível.")
            return

        gastos_por_ano = {}
        for item in self.itens:
            try:
                ano = datetime.strptime(item["data"], "%d/%m/%Y").year
            except ValueError:
                continue  # ignora formatos errados
            gastos_por_ano[ano] = gastos_por_ano.get(ano, 0) + item["subtotal"]

        janela = tk.Toplevel(self.root)
        janela.title("Gastos anuais")
        janela.geometry("400x300")
        janela.configure(bg="#282828")

        tk.Label(janela, text="Gastos com cigarros por ano", fg="white", bg="#282828", font=("Arial", 12, "bold")).pack(pady=10)

        tree_ano = ttk.Treeview(janela, columns=("ano", "total"), show="headings")
        tree_ano.heading("ano", text="Ano")
        tree_ano.heading("total", text="Total gasto (R$)")
        tree_ano.column("ano", width=100, anchor="center")
        tree_ano.column("total", width=150, anchor="center")
        tree_ano.pack(padx=10, pady=10, fill="both", expand=True)

        total_geral = 0
        for ano, total in sorted(gastos_por_ano.items()):
            tree_ano.insert("", "end", values=(ano, f"{total:.2f}"))
            total_geral += total

        tk.Label(janela, text=f"Total geral: R$ {total_geral:.2f}", fg="yellow", bg="#282828", font=("Arial", 12, "bold")).pack(pady=10)

    # === SALVAR / CARREGAR ===
    def salvar_dados(self):
        dados = {"itens": self.itens, "total": self.total}
        with open(ARQUIVO_SALVAMENTO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def carregar_dados(self):
        if os.path.exists(ARQUIVO_SALVAMENTO):
            with open(ARQUIVO_SALVAMENTO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.itens = dados.get("itens", [])
                self.total = dados.get("total", 0.0)

                for item in self.itens:
                    self.tree.insert("", "end", values=(
                        item["marca"], f"{item['preco']:.2f}", item["quantidade"],
                        item["data"], f"{item['subtotal']:.2f}"
                    ))
                self.total_label.config(text=f"Total: R$ {self.total:.2f}")

    def fechar_app(self):
        self.salvar_dados()
        self.root.destroy()


# === EXECUÇÃO ===
if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
