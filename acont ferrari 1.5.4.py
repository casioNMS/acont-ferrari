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
        self.root.title("acont ferrari 1.5.4")
        self.root.geometry("1000x800")
        self.root.configure(bg="#202020")
        self.root.state("zoomed")

        self.quantidade = tk.IntVar(value=1)
        self.itens = []
        self.total = 0

        tk.Label(root,text="Marca:",bg="#202020",fg="white").grid(row=0,column=0)
        self.marca_entry=tk.Entry(root)
        self.marca_entry.grid(row=0,column=1)

        tk.Label(root,text="Preço:",bg="#202020",fg="white").grid(row=1,column=0)
        self.preco_entry=tk.Entry(root)
        self.preco_entry.grid(row=1,column=1)

        tk.Label(root,text="Data:",bg="#202020",fg="white").grid(row=2,column=0)
        self.data_entry=tk.Entry(root)
        self.data_entry.grid(row=2,column=1)
        self.data_entry.insert(0,datetime.now().strftime("%d/%m/%Y"))

        tk.Button(root,text="📅",command=self.abrir_calendario).grid(row=2,column=2)

        tk.Label(root,text="Dia semana:",bg="#202020",fg="white").grid(row=3,column=0)
        self.dia_entry=tk.Entry(root)
        self.dia_entry.grid(row=3,column=1)

        tk.Label(root,text="Mês:",bg="#202020",fg="white").grid(row=4,column=0)
        self.mes_entry=tk.Entry(root)
        self.mes_entry.grid(row=4,column=1)

        tk.Label(root,text="Quantidade:",bg="#202020",fg="white").grid(row=5,column=0)
        tk.Label(root,textvariable=self.quantidade,bg="#202020",fg="cyan").grid(row=5,column=1)

        tk.Button(root,text="+",command=self.aumentar).grid(row=5,column=2)
        tk.Button(root,text="-",command=self.diminuir).grid(row=5,column=3)

        frame=tk.Frame(root,bg="#202020")
        frame.grid(row=6,column=0,columnspan=4,pady=10)

        tk.Button(frame,text="Adicionar",command=self.adicionar_item,bg="green",fg="white").pack(side="left",padx=5)
        tk.Button(frame,text="Remover",command=self.remover_item,bg="red",fg="white").pack(side="left",padx=5)
        tk.Button(frame,text="Limpar Campos",command=self.limpar_campos).pack(side="left",padx=5)

        tk.Button(frame,text="📈 Relatório Anual Detalhado",
                  command=self.relatorio_anual_detalhado,
                  bg="#111",
                  fg="#00ff00").pack(side="left",padx=5)

        self.tree=ttk.Treeview(root,
            columns=("marca","preco","qtd","data","hora","dia","mes","total"),
            show="headings"
        )

        for c in ("marca","preco","qtd","data","hora","dia","mes","total"):
            self.tree.heading(c,text=c)

        self.tree.grid(row=7,column=0,columnspan=4,padx=10,pady=10,sticky="nsew")

        self.total_label=tk.Label(root,text="Total: R$0",
                                  bg="#202020",
                                  fg="yellow",
                                  font=("Arial",14,"bold"))
        self.total_label.grid(row=8,column=0,columnspan=4)

        self.relatorio=tk.Text(root,height=18,
                               bg="#151515",
                               fg="#00ff00",
                               font=("Consolas",10))
        self.relatorio.grid(row=9,column=0,columnspan=4,padx=10,pady=10)

        self.carregar_dados()

    def aumentar(self):
        self.quantidade.set(self.quantidade.get()+1)

    def diminuir(self):
        if self.quantidade.get()>1:
            self.quantidade.set(self.quantidade.get()-1)

    def limpar_campos(self):
        self.marca_entry.delete(0,"end")
        self.preco_entry.delete(0,"end")
        self.dia_entry.delete(0,"end")
        self.mes_entry.delete(0,"end")

    def remover_item(self):

        sel = self.tree.selection()

        if not sel:
            return

        for s in sel:

            valores = self.tree.item(s)["values"]

            marca = valores[0]
            data = valores[3]

            for item in self.itens:

                if item["marca"] == marca and item["data"] == data:

                    self.total -= item["subtotal"]
                    self.itens.remove(item)
                    break

            self.tree.delete(s)

        self.total_label.config(text=f"Total: R${self.total:.2f}")

        self.atualizar_relatorio()
        self.salvar()

    def abrir_calendario(self):

        top=tk.Toplevel(self.root)

        cal=Calendar(top,date_pattern="dd/mm/yyyy")
        cal.pack()

        def selecionar():
            self.data_entry.delete(0,"end")
            self.data_entry.insert(0,cal.get_date())
            top.destroy()

        tk.Button(top,text="Selecionar",command=selecionar).pack()

    def adicionar_item(self):

        marca=self.marca_entry.get()
        preco=self.preco_entry.get()
        data=self.data_entry.get()
        dia=self.dia_entry.get()
        mes=self.mes_entry.get()
        qtd=self.quantidade.get()

        try:
            preco=float(preco)
        except:
            messagebox.showerror("Erro","Preço inválido")
            return

        subtotal=preco*qtd

        item={
            "marca":marca,
            "preco":preco,
            "quantidade":qtd,
            "data":data,
            "hora":datetime.now().strftime("%H:%M"),
            "dia":dia,
            "mes":mes,
            "subtotal":subtotal
        }

        self.itens.append(item)
        self.total+=subtotal

        self.mostrar_todos()
        self.atualizar_relatorio()

        self.total_label.config(text=f"Total: R${self.total:.2f}")

        self.salvar()

    def mostrar_todos(self):

        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in self.itens:

            self.tree.insert("",tk.END,values=(

                item.get("marca"),
                item.get("preco"),
                item.get("quantidade"),
                item.get("data"),
                item.get("hora"),
                item.get("dia"),
                item.get("mes"),
                item.get("subtotal")

            ))

    def atualizar_relatorio(self):

        self.relatorio.delete("1.0","end")

        gastos_mes=defaultdict(float)
        marcas=defaultdict(int)

        for i in self.itens:

            mes=i.get("mes","?")
            gastos_mes[mes]+=i["subtotal"]
            marcas[i["marca"]]+=i["quantidade"]

        self.relatorio.insert("end","RELATÓRIO DE CONSUMO\n")
        self.relatorio.insert("end","----------------------------------------\n\n")

        self.relatorio.insert("end","[ GASTOS POR MÊS ]\n\n")

        for mes,valor in gastos_mes.items():

            barras="█"*int(valor/10)

            self.relatorio.insert("end",
                f"{mes:10} | {barras} R${valor:.2f}\n"
            )

        self.relatorio.insert("end","\n")

        self.relatorio.insert("end","[ MARCAS MAIS CONSUMIDAS (unidades) ]\n\n")

        for marca,qtd in sorted(marcas.items(), key=lambda x:x[1], reverse=True):

            barras="█"*qtd

            self.relatorio.insert("end",
                f"{marca:12} | {barras} {qtd} un\n"
            )

        self.relatorio.insert("end","\n")

        barras_total="█"*int(self.total/10)

        self.relatorio.insert("end","[ TOTAL GERAL ]\n\n")
        self.relatorio.insert("end",f"TOTAL | {barras_total} R${self.total:.2f}\n")

    def relatorio_anual_detalhado(self):

        janela=tk.Toplevel(self.root)
        janela.title("Relatório Anual Detalhado")
        janela.configure(bg="black")
        janela.geometry("600x500")

        texto=tk.Text(janela,
                      bg="black",
                      fg="#00ff00",
                      font=("Consolas",11))
        texto.pack(fill="both",expand=True)

        dados=defaultdict(lambda: defaultdict(float))
        marcas_ano=defaultdict(lambda: defaultdict(int))

        for i in self.itens:

            try:

                dt=datetime.strptime(i["data"],"%d/%m/%Y")
                ano=dt.year

                mes=i.get("mes","?")

                dados[ano][mes]+=i["subtotal"]
                marcas_ano[ano][i["marca"]]+=i["quantidade"]

            except:
                pass

        for ano in sorted(dados):

            total_ano=sum(dados[ano].values())

            texto.insert("end",
                f"{ano}  TOTAL: R${total_ano:.2f}\n\n"
            )

            for mes,valor in dados[ano].items():

                barras="█"*int(valor/10)

                texto.insert("end",
                    f"{mes:10} | {barras} R${valor:.2f}\n"
                )

            texto.insert("end","\nMARCAS MAIS CONSUMIDAS\n\n")

            for marca,qtd in marcas_ano[ano].items():

                barras="█"*qtd

                texto.insert("end",
                    f"{marca:12} | {barras} {qtd} un\n"
                )

            texto.insert("end","\n-----------------------------\n\n")

        texto.config(state="disabled")

    def salvar(self):

        with open(ARQUIVO_SALVAMENTO,"w") as f:
            json.dump({"itens":self.itens},f,indent=4)

    def carregar_dados(self):

        if os.path.exists(ARQUIVO_SALVAMENTO):

            with open(ARQUIVO_SALVAMENTO) as f:

                dados=json.load(f)

                self.itens=dados.get("itens",[])

                self.total=sum(i["subtotal"] for i in self.itens)

                self.mostrar_todos()
                self.atualizar_relatorio()

                self.total_label.config(text=f"Total: R${self.total:.2f}")

if __name__=="__main__":

    root=tk.Tk()

    app=Main(root)

    root.mainloop()