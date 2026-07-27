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
        self.root.geometry("1000x800")
        self.root.configure(bg="#202020")
        self.root.state("zoomed")
        
        self.quantidade = tk.IntVar(value=1)
        self.itens = []
        self.total = 0.0

        # --- Interface de Entrada ---
        tk.Label(root, text="Marca:", bg="#202020", fg="white").grid(row=0, column=0, pady=5)
        self.marca_entry = tk.Entry(root)
        self.marca_entry.grid(row=0, column=1)

        tk.Label(root, text="Preço:", bg="#202020", fg="white").grid(row=1, column=0, pady=5)
        self.preco_entry = tk.Entry(root)
        self.preco_entry.grid(row=1, column=1)

        tk.Label(root, text="Data:", bg="#202020", fg="white").grid(row=2, column=0, pady=5)
        self.data_entry = tk.Entry(root)
        self.data_entry.grid(row=2, column=1)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        tk.Button(root, text="📅", command=self.abrir_calendario).grid(row=2, column=2)

        tk.Label(root, text="Quantidade:", bg="#202020", fg="white").grid(row=3, column=0, pady=5)
        tk.Label(root, textvariable=self.quantidade, bg="#202020", fg="cyan", font=("Arial", 12, "bold")).grid(row=3, column=1)
        tk.Button(root, text="+", command=self.aumentar, width=3).grid(row=3, column=2)
        tk.Button(root, text="-", command=self.diminuir, width=3).grid(row=3, column=3)

        # --- Botões de Ação ---
        btn_frame = tk.Frame(root, bg="#202020")
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)

        tk.Button(btn_frame, text="Adicionar", command=self.adicionar_item, bg="green", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remover", command=self.remover_item, bg="red", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📊 Relatórios", command=self.menu_graficos, bg="blue", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Relatório Anual", command=self.ver_gastos_anuais, bg="purple", fg="white", width=12).pack(side="left", padx=5)

        # --- Pesquisa ---
        tk.Label(root, text="Pesquisar:", bg="#202020", fg="white").grid(row=5, column=0)
        self.pesquisa_entry = tk.Entry(root)
        self.pesquisa_entry.grid(row=5, column=1)
        tk.Button(root, text="Pesquisar", command=self.pesquisar).grid(row=5, column=2)
        tk.Button(root, text="Limpar", command=self.mostrar_todos).grid(row=5, column=3)

        # --- Tabela (Treeview) ---
        self.tree = ttk.Treeview(root, columns=("marca", "preco", "qtd", "data", "total"), show="headings", height=8)
        self.tree.heading("marca", text="Marca")
        self.tree.heading("preco", text="Preço")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("data", text="Data")
        self.tree.heading("total", text="Subtotal")
        self.tree.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.total_label = tk.Label(root, text="Total: R$ 0.00", bg="#202020", fg="yellow", font=("Arial", 14, "bold"))
        self.total_label.grid(row=7, column=0, columnspan=4)

        # --- Área de Estatísticas Visual ---
        tk.Label(root, text="--- Estatísticas Detalhadas ---", bg="#202020", fg="white", font=("Arial", 10, "bold")).grid(row=8, column=0, columnspan=4, pady=(10,0))
        self.relatorio = tk.Text(root, height=12, width=80, font=("Consolas", 10), bg="#151515", fg="#00FF00")
        self.relatorio.grid(row=9, column=0, columnspan=4, padx=10, pady=10)

        self.carregar_dados()
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)

    def atualizar_relatorio(self):
        self.relatorio.config(state="normal")
        self.relatorio.delete("1.0", tk.END)

        if not self.itens:
            self.relatorio.insert(tk.END, "Nenhum dado registrado para gerar estatísticas.")
            self.relatorio.config(state="disabled")
            return

        gastos_mes = defaultdict(float)
        gastos_ano = defaultdict(float)
        marcas_cont = defaultdict(int)
        total_geral = 0

        for item in self.itens:
            try:
                dt = datetime.strptime(item["data"], "%d/%m/%Y")
                mes_ano = dt.strftime("%m/%Y")
                ano = dt.strftime("%Y")
                
                valor = item["subtotal"]
                total_geral += valor

                gastos_mes[mes_ano] += valor
                gastos_ano[ano] += valor
                marcas_cont[item["marca"]] += item["quantidade"]
            except:
                continue

        self.relatorio.insert(tk.END, "RELATÓRIO DE CONSUMO\n" + "="*40 + "\n")

        # Gastos por Mês
        self.relatorio.insert(tk.END, "\n[ GASTOS POR MÊS ]\n")
        maior_mes = max(gastos_mes.values()) if gastos_mes else 1
        for mes, valor in sorted(gastos_mes.items()):
            barras = int((valor / maior_mes) * 30)
            self.relatorio.insert(tk.END, f"{mes:8} | {'█' * barras} R${valor:.2f}\n")

        # Marcas
        self.relatorio.insert(tk.END, "\n[ MARCAS MAIS CONSUMIDAS (unidades) ]\n")
        maior_qtd = max(marcas_cont.values()) if marcas_cont else 1
        for marca, qtd in sorted(marcas_cont.items(), key=lambda x: x[1], reverse=True):
            barras = int((qtd / maior_qtd) * 30)
            self.relatorio.insert(tk.END, f"{marca[:12]:12} | {'█' * barras} {qtd} un\n")

        self.relatorio.insert(tk.END, f"\n{'='*40}\nTOTAL ACUMULADO: R$ {total_geral:.2f}")
        self.relatorio.config(state="disabled")

    def aumentar(self):
        self.quantidade.set(self.quantidade.get() + 1)

    def diminuir(self):
        if self.quantidade.get() > 1:
            self.quantidade.set(self.quantidade.get() - 1)

    def abrir_calendario(self):
        top = tk.Toplevel(self.root)
        cal = Calendar(top, date_pattern="dd/mm/yyyy")
        cal.pack()
        tk.Button(top, text="Selecionar", command=lambda: [self.data_entry.delete(0, tk.END), self.data_entry.insert(0, cal.get_date()), top.destroy()]).pack()

    def adicionar_item(self):
        marca = self.marca_entry.get().strip()
        preco = self.preco_entry.get().strip()
        data = self.data_entry.get().strip()
        qtd = self.quantidade.get()

        if not marca or not preco:
            messagebox.showwarning("Erro", "Preencha marca e preço")
            return

        try:
            preco = float(preco.replace(",", "."))
            subtotal = preco * qtd
            
            item = {
                "marca": marca,
                "preco": preco,
                "quantidade": qtd,
                "data": data,
                "subtotal": subtotal
            }

            self.itens.append(item)
            self.mostrar_todos()
            self.total += subtotal
            self.total_label.config(text=f"Total: R$ {self.total:.2f}")
            self.atualizar_relatorio()
            self.salvar()
            
            # Limpa campos
            self.marca_entry.delete(0, tk.END)
            self.preco_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número")

    def remover_item(self):
        sel = self.tree.selection()
        if not sel:
            return

        for s in sel:
            # Pega os valores da linha selecionada na tabela (Treeview)
            valores = self.tree.item(s)["values"]
            
            marca_tab = str(valores[0])
            preco_tab = float(valores[1])
            qtd_tab   = int(valores[2])
            data_tab  = str(valores[3])

            # Procura o item correspondente na lista self.itens
            item_para_remover = None
            for item in self.itens:
                # Compara todos os campos para garantir que é o item correto
                if (item["marca"] == marca_tab and 
                    abs(item["preco"] - preco_tab) < 0.01 and # Evita erro de precisão float
                    item["quantidade"] == qtd_tab and 
                    item["data"] == data_tab):
                    
                    item_para_remover = item
                    break
            
            if item_para_remover:
                self.total -= item_para_remover["subtotal"]
                self.itens.remove(item_para_remover)
            
            # Remove da visualização da tabela
            self.tree.delete(s)

        # Atualiza a interface e SALVA no arquivo
        self.total_label.config(text=f"Total: R$ {self.total:.2f}")
        self.atualizar_relatorio()
        self.salvar() # <--- Essencial para persistir a exclusão

    def pesquisar(self):
        termo = self.pesquisa_entry.get().lower()
        for i in self.tree.get_children(): self.tree.delete(i)
        
        for item in self.itens:
            if termo in item['marca'].lower() or termo in item['data']:
                self.tree.insert("", "end", values=(item["marca"], f"{item['preco']:.2f}", item["quantidade"], item["data"], f"{item['subtotal']:.2f}"))

    def mostrar_todos(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for i in self.itens:
            self.tree.insert("", "end", values=(i["marca"], f"{i['preco']:.2f}", i["quantidade"], i["data"], f"{i['subtotal']:.2f}"))

    def salvar(self):
        with open(ARQUIVO_SALVAMENTO, "w", encoding="utf-8") as f:
            json.dump({"itens": self.itens, "total": self.total}, f, indent=4)

    def carregar_dados(self):
        if os.path.exists(ARQUIVO_SALVAMENTO):
            try:
                with open(ARQUIVO_SALVAMENTO, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.itens = dados.get("itens", [])
                    self.total = sum(item['subtotal'] for item in self.itens)
                    self.mostrar_todos()
                    self.total_label.config(text=f"Total: R$ {self.total:.2f}")
                    self.atualizar_relatorio()
            except:
                pass

    # --- Métodos de Relatórios de Janela ---
    def mostrar_relatorio(self, titulo, texto):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        box = tk.Text(win, width=50, height=20)
        box.pack(padx=10, pady=10)
        box.insert("1.0", texto)
        box.config(state="disabled")

    def menu_graficos(self):
        win = tk.Toplevel(self.root)
        win.title("Menu de Relatórios")
        win.geometry("250x200")
        tk.Button(win, text="Vendas por Marca", command=self.relatorio_marcas).pack(fill="x", pady=2)
        tk.Button(win, text="Vendas por Dia", command=self.relatorio_dias).pack(fill="x", pady=2)
        tk.Button(win, text="Vendas por Mês", command=self.relatorio_meses).pack(fill="x", pady=2)
        tk.Button(win, text="Ranking de Marcas", command=self.ranking_marcas).pack(fill="x", pady=2)

    def relatorio_marcas(self):
        dados = defaultdict(int)
        for i in self.itens: dados[i["marca"]] += i["quantidade"]
        texto = "VENDAS POR MARCA\n\n" + "\n".join([f"{m}: {q} un" for m, q in dados.items()])
        self.mostrar_relatorio("Marcas", texto)

    def relatorio_dias(self):
        dados = defaultdict(int)
        for i in self.itens: dados[i["data"]] += i["quantidade"]
        texto = "VENDAS POR DIA\n\n" + "\n".join([f"{d}: {q} un" for d, q in dados.items()])
        self.mostrar_relatorio("Dias", texto)

    def relatorio_meses(self):
        dados = defaultdict(int)
        for i in self.itens:
            mes = datetime.strptime(i["data"], "%d/%m/%Y").strftime("%m/%Y")
            dados[mes] += i["quantidade"]
        texto = "VENDAS POR MÊS\n\n" + "\n".join([f"{m}: {q} un" for m, q in dados.items()])
        self.mostrar_relatorio("Meses", texto)

    def ranking_marcas(self):
        dados = defaultdict(int)
        for i in self.itens: dados[i["marca"]] += i["quantidade"]
        ranking = sorted(dados.items(), key=lambda x: x[1], reverse=True)
        texto = "RANKING\n\n" + "\n".join([f"{idx+1}º {m} ({q})" for idx, (m, q) in enumerate(ranking)])
        self.mostrar_relatorio("Ranking", texto)

    def ver_gastos_anuais(self):
        dados = defaultdict(float)
        for i in self.itens:
            ano = datetime.strptime(i["data"], "%d/%m/%Y").year
            dados[ano] += i["subtotal"]
        texto = "GASTOS ANUAIS\n\n" + "\n".join([f"{a}: R$ {v:.2f}" for a, v in dados.items()])
        self.mostrar_relatorio("Anual", texto)

    def fechar(self):
        self.salvar()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()