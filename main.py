import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image as ReportLabImage
import os

# Inicializa o estoque e imagens
estoque = {}
imagens = {}

def adicionar_produto():
    nome = entry_nome.get().strip()
    quantidade_texto = entry_quantidade.get().strip()
    variacao = combo_variacao.get().strip()
    
    if not nome or not quantidade_texto or not variacao:
        messagebox.showwarning("Atenção", "Preencha todos os campos corretamente.")
        return

    nome_com_variacao = f"{nome} ({variacao})"

    try:
        quantidade = int(quantidade_texto)
        if quantidade > 0:
            if nome_com_variacao in estoque:
                estoque[nome_com_variacao] += quantidade
            else:
                estoque[nome_com_variacao] = quantidade
            atualizar_lista()
        else:
            messagebox.showwarning("Atenção", "A quantidade deve ser maior que zero.")
    except ValueError:
        messagebox.showwarning("Atenção", "Insira uma quantidade válida.")

def remover_produto():
    selected_item = listbox_estoque.get(tk.ACTIVE)
    if selected_item:
        nome = selected_item.split(":")[0].strip()
        if nome in estoque:
            del estoque[nome]
            if nome in imagens:
                del imagens[nome]
            atualizar_lista()
        else:
            messagebox.showwarning("Atenção", "Produto não encontrado no estoque.")
    else:
        messagebox.showwarning("Atenção", "Selecione um produto para remover.")

def buscar_produto():
    nome = entry_nome.get().strip()
    variacao = combo_variacao.get().strip()
    nome_com_variacao = f"{nome} ({variacao})"
    
    if nome_com_variacao in estoque:
        entry_quantidade.delete(0, tk.END)
        entry_quantidade.insert(0, estoque[nome_com_variacao])
    else:
        messagebox.showwarning("Atenção", "Produto não encontrado no estoque.")

def atualizar_lista():
    listbox_estoque.delete(0, tk.END)
    for nome, quantidade in estoque.items():
        listbox_estoque.insert(tk.END, f"{nome}: {quantidade} unidade(s)")
    atualizar_imagem()

def adicionar_imagem():
    selected_item = listbox_estoque.get(tk.ACTIVE)
    if selected_item:
        nome = selected_item.split(":")[0].strip()
        caminho_imagem = filedialog.askopenfilename()
        if caminho_imagem and nome:
            imagens[nome] = caminho_imagem
            atualizar_imagem()
        else:
            messagebox.showwarning("Atenção", "Selecione uma imagem válida e um produto existente.")
    else:
        messagebox.showwarning("Atenção", "Selecione um produto para adicionar imagem.")

def atualizar_imagem(event=None):
    selected_item = listbox_estoque.get(tk.ACTIVE)
    if selected_item:
        nome = selected_item.split(":")[0].strip()
        if nome in imagens:
            caminho_imagem = imagens[nome]
            img = Image.open(caminho_imagem)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            label_imagem.config(image=img)
            label_imagem.image = img
        else:
            label_imagem.config(image='', text="Sem Imagem")

def gerar_relatorio():
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if caminho_arquivo:
        doc = SimpleDocTemplate(caminho_arquivo, pagesize=A4)
        elementos = []

        estilos = getSampleStyleSheet()
        titulo = Paragraph("Relatório de Estoque", estilos['Title'])
        elementos.append(titulo)

        tabela_dados = [["Imagem", "Produto", "Quantidade"]]
        for nome, quantidade in estoque.items():
            if nome in imagens:
                img = ReportLabImage(imagens[nome], width=50, height=50)  # Redimensionando a imagem para o PDF
            else:
                img = ""  # Caso não tenha imagem, fica vazio
            tabela_dados.append([img, nome, quantidade])

        tabela = Table(tabela_dados, colWidths=[60, 340, 100])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elementos.append(tabela)
        doc.build(elementos)
        messagebox.showinfo("Relatório", "Relatório de estoque gerado com sucesso!")
        os.startfile(caminho_arquivo)  # Abre automaticamente o PDF gerado

def carregar_dados():
    global estoque, imagens
    try:
        with open('estoque.json', 'r') as f:
            estoque = json.load(f)
        with open('imagens.json', 'r') as f:
            imagens = json.load(f)
        atualizar_lista()
    except FileNotFoundError:
        estoque = {}
        imagens = {}

def salvar_dados():
    with open('estoque.json', 'w') as f:
        json.dump(estoque, f)
    with open('imagens.json', 'w') as f:
        json.dump(imagens, f)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Controle de Estoque")

# Labels e Entrys
tk.Label(root, text="Nome do Produto:").grid(row=0, column=0, padx=10, pady=5)
entry_nome = tk.Entry(root, width=50)
entry_nome.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Quantidade:").grid(row=1, column=0, padx=10, pady=5)
entry_quantidade = tk.Entry(root, width=20)
entry_quantidade.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Variação:").grid(row=2, column=0, padx=10, pady=5)
combo_variacao = ttk.Combobox(root, values=["Azul", "Vermelho", "Preto", "Outro"], width=47)
combo_variacao.grid(row=2, column=1, padx=10, pady=5)
combo_variacao.set("Selecione a variação")

# Botões
tk.Button(root, text="Adicionar Produto", command=adicionar_produto, bg="lightgreen").grid(row=3, column=0, padx=10, pady=5)
tk.Button(root, text="Remover Produto", command=remover_produto, bg="lightcoral").grid(row=3, column=1, padx=10, pady=5)
tk.Button(root, text="Buscar Produto", command=buscar_produto, bg="lightblue").grid(row=4, column=0, padx=10, pady=5)
tk.Button(root, text="Adicionar Imagem", command=adicionar_imagem, bg="orange").grid(row=4, column=1, padx=10, pady=5)
tk.Button(root, text="Gerar Relatório", command=gerar_relatorio, bg="lightgrey").grid(row=5, column=0, padx=10, pady=5)

# Listbox e Label para imagem
listbox_estoque = tk.Listbox(root, width=50)
listbox_estoque.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
listbox_estoque.bind('<<ListboxSelect>>', atualizar_imagem)

label_imagem = tk.Label(root, text="Sem Imagem")
label_imagem.grid(row=6, column=2, rowspan=2, padx=10, pady=10)

# Carrega os dados ao iniciar
carregar_dados()

# Configura o fechamento da janela
root.protocol("WM_DELETE_WINDOW", lambda: (salvar_dados(), root.destroy()))

root.mainloop()
