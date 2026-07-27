import tkinter as tk
from tkinter import ttk
import json
import os

ARQUIVO = "dados_cigarro.json"


class Main:

    def __init__(self, root):

        self.root = root
        root.title("Acont Ferrari 1.4.1")
        root.state("zoomed")

        self.itens = []

        # CAMPOS

        tk.Label(root,text="Marca").grid(row=0,column=0)
        self.marca = tk.Entry(root)
        self.marca.grid(row=0,column=1)

        tk.Label(root,text="Preço").grid(row=0,column=2)
        self.preco = tk.Entry(root)
        self.preco.grid(row=0,column=3)

        tk.Label(root,text="Qtd").grid(row=0,column=4)
        self.qtd = tk.Entry(root)
        self.qtd.grid(row=0,column=5)

        tk.Label(root,text="Data").grid(row=1,column=0)
        self.data = tk.Entry(root)
        self.data.grid(row=1,column=1)

        tk.Label(root,text="Hora").grid(row=1,column=2)
        self.hora = tk.Entry(root)
        self.hora.grid(row=1,column=3)

        tk.Label(root,text="Dia Semana").grid(row=1,column=4)
        self.dia = tk.Entry(root)
        self.dia.grid(row=1,column=5)

        tk.Label(root,text="Mês").grid(row=2,column=0)
        self.mes = tk.Entry(root)
        self.mes.grid(row=2,column=1)

        tk.Label(root,text="Ano").grid(row=2,column=2)
        self.ano = tk.Entry(root)
        self.ano.grid(row=2,column=3)

        tk.Button(root,text="Adicionar",command=self.adicionar).grid(row=3,column=1)
        tk.Button(root,text="Excluir",command=self.excluir).grid(row=3,column=2)
        tk.Button(root, text="limpar campos", command=self.limpar_campos).grid(row=3, column=5)

        # PESQUISA AUTOMÁTICA

        tk.Label(root,text="Pesquisar").grid(row=3,column=3)

        self.pesquisa_var = tk.StringVar()
        self.pesquisa_var.trace_add("write", self.pesquisa_automatica)

        self.pesquisa_entry = tk.Entry(root,textvariable=self.pesquisa_var,width=30)
        self.pesquisa_entry.grid(row=3,column=4)

        # LISTA

        colunas = ("marca","preco","qtd","data","hora","dia","mes","ano","subtotal")

        self.tree = ttk.Treeview(root,columns=colunas,show="headings",height=15)

        for c in colunas:
            self.tree.heading(c,text=c)

        self.tree.grid(row=4,column=0,columnspan=8)

        # RELATÓRIO

        tk.Label(root,text="Estatísticas").grid(row=5,column=0)

        self.relatorio = tk.Text(root,height=20,width=120,font=("Consolas",10))
        self.relatorio.grid(row=6,column=0,columnspan=8)

        self.carregar()
        self.atualizar_lista()

    def limpar_campos(self):
        self.marca.delete(0, tk.END)
        self.preco.delete(0, tk.END)
        self.qtd.delete(0, tk.END)
        self.data.delete(0, tk.END)
        self.hora.delete(0, tk.END)
        self.dia.delete(0, tk.END)
        self.mes.delete(0, tk.END)
        self.ano.delete(0, tk.END)


    def pesquisa_automatica(self,*args):

        termo = self.pesquisa_var.get().lower()

        for i in self.tree.get_children():
            self.tree.delete(i)

        if termo == "":
            self.atualizar_lista()
            return

        for item in self.itens:

            texto = " ".join(str(v) for v in item.values()).lower()

            if termo in texto:

                self.tree.insert("",tk.END,values=(

                    item["marca"],
                    item["preco"],
                    item["qtd"],
                    item["data"],
                    item["hora"],
                    item["dia"],
                    item["mes"],
                    item["ano"],
                    item["subtotal"]

                ))


    def adicionar(self):

        try:

            preco = float(self.preco.get())
            qtd = int(self.qtd.get())

            subtotal = preco*qtd

            item = {

                "marca":self.marca.get(),
                "preco":preco,
                "qtd":qtd,
                "data":self.data.get(),
                "hora":self.hora.get(),
                "dia":self.dia.get(),
                "mes":self.mes.get(),
                "ano":self.ano.get(),
                "subtotal":subtotal

            }

            self.itens.append(item)

            self.salvar()

            self.atualizar_lista()

        except:
            pass


    def excluir(self):

        selecionado = self.tree.selection()

        if not selecionado:
            return

        item_tree = selecionado[0]

        valores = self.tree.item(item_tree)["values"]

        marca = valores[0]
        data = valores[3]

        for i in self.itens:

            if i["marca"] == marca and i["data"] == data:

                self.itens.remove(i)
                break

        self.salvar()

        self.atualizar_lista()


    def atualizar_lista(self):

        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in self.itens:

            self.tree.insert("",tk.END,values=(

                item["marca"],
                item["preco"],
                item["qtd"],
                item["data"],
                item["hora"],
                item["dia"],
                item["mes"],
                item["ano"],
                item["subtotal"]

            ))

        self.atualizar_relatorio()


    def atualizar_relatorio(self):

        self.relatorio.delete("1.0",tk.END)

        if not self.itens:
            return

        gastos_mes = {}
        gastos_ano = {}
        marcas = {}
        total = 0

        for item in self.itens:

            mes = item["mes"]
            ano = item["ano"]
            marca = item["marca"]
            valor = item["subtotal"]

            total += valor

            gastos_mes[mes] = gastos_mes.get(mes,0)+valor
            gastos_ano[ano] = gastos_ano.get(ano,0)+valor
            marcas[marca] = marcas.get(marca,0)+1


        self.relatorio.insert(tk.END,"RELATÓRIO COMPLETO\n\n")


        self.relatorio.insert(tk.END,"GASTOS POR MÊS\n\n")

        maior = max(gastos_mes.values())

        for mes,valor in gastos_mes.items():

            barras = int((valor/maior)*40)

            graf = "█"*barras

            self.relatorio.insert(tk.END,f"{mes:10} | {graf} R${valor:.2f}\n")


        self.relatorio.insert(tk.END,"\nGASTOS POR ANO\n\n")

        maior = max(gastos_ano.values())

        for ano,valor in gastos_ano.items():

            barras = int((valor/maior)*40)

            graf = "█"*barras

            self.relatorio.insert(tk.END,f"{ano:10} | {graf} R${valor:.2f}\n")


        self.relatorio.insert(tk.END,"\nMARCAS MAIS COMPRADAS\n\n")

        maior = max(marcas.values())

        for marca,qtd in marcas.items():

            barras = int((qtd/maior)*40)

            graf = "█"*barras

            self.relatorio.insert(tk.END,f"{marca:12} | {graf} {qtd} maços\n")


        self.relatorio.insert(tk.END,"\nTOTAL GASTO: R$ "+str(round(total,2)))


    def salvar(self):

        with open(ARQUIVO,"w",encoding="utf8") as f:

            json.dump(self.itens,f,indent=4,ensure_ascii=False)


    def carregar(self):

        if os.path.exists(ARQUIVO):

            with open(ARQUIVO,"r",encoding="utf8") as f:

                self.itens = json.load(f)



root = tk.Tk()

app = Main(root)

root.mainloop()