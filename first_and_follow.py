import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys

def cal_follow(s, productions, first):
    """
    Calcula el conjunto FOLLOW para un símbolo no terminal 's' en una gramática dada.

    Args:
        s (str): Símbolo no terminal para el que se calcula FOLLOW.
        productions (dict): Diccionario de producciones de la gramática.
        first (dict): Diccionario con los conjuntos FIRST de cada no terminal.

    Returns:
        set: Conjunto FOLLOW para el símbolo 's'.
    """
    follow = set()
    # Si el símbolo no es un solo carácter, retorna un diccionario vacío (caso no esperado)
    if len(s) != 1:
        return {}
    # Si es el símbolo inicial, agrega '$' al FOLLOW
    if s == list(productions.keys())[0]:
        follow.add('$') 
    # Recorre todas las producciones buscando ocurrencias de 's'
    for i in productions:
        for j in range(len(productions[i])):
            if s in productions[i][j]:
                idx = productions[i][j].index(s)
                # Si 's' es el último símbolo de la producción
                if idx == len(productions[i][j]) - 1:
                    if productions[i][j][idx] != i:
                        # Añade FOLLOW del lado izquierdo
                        f = cal_follow(i, productions, first)
                        for x in f:
                            follow.add(x)
                else:
                    # Si hay símbolos después de 's'
                    while idx != len(productions[i][j]) - 1:
                        idx += 1
                        # Si el siguiente símbolo es terminal, se añade a FOLLOW
                        if not productions[i][j][idx].isupper():
                            follow.add(productions[i][j][idx])
                            break
                        else:
                            # Si es no terminal, añade su FIRST (excepto epsilon)
                            f = cal_first(productions[i][j][idx], productions)
                            if 'ε' not in f:
                                for x in f:
                                    follow.add(x)
                                break
                            elif 'ε' in f and idx != len(productions[i][j]) - 1:
                                f.remove('ε')
                                for k in f:
                                    follow.add(k)
                            elif 'ε' in f and idx == len(productions[i][j]) - 1:
                                f.remove('ε')
                                for k in f:
                                    follow.add(k)
                                # Si epsilon está en FIRST y es el último símbolo, añade FOLLOW del lado izquierdo
                                f = cal_follow(i, productions, first)
                                for x in f:
                                    follow.add(x)
    return follow

def cal_first(s, productions):
    """
    Calcula el conjunto FIRST para un símbolo no terminal 's'.

    Args:
        s (str): Símbolo no terminal.
        productions (dict): Diccionario de producciones.

    Returns:
        set: Conjunto FIRST para el símbolo 's'.
    """
    first = set()
    for i in range(len(productions[s])):
        for j in range(len(productions[s][i])):
            c = productions[s][i][j]
            if c.isupper():
                # Si es no terminal, calcula su FIRST recursivamente
                f = cal_first(c, productions)
                if 'ε' not in f:
                    for k in f:
                        first.add(k)
                    break
                else:
                    if j == len(productions[s][i]) - 1:
                        for k in f:
                            first.add(k)
                    else:
                        f.remove('ε')
                        for k in f:
                            first.add(k)
            else:
                # Si es terminal, se añade directamente
                first.add(c)
                break
    return first

def build_predictive_table(productions, first, follow):
    """
    Construye la tabla predictiva LL(1) para la gramática.

    Args:
        productions (dict): Diccionario de producciones.
        first (dict): Diccionario de conjuntos FIRST.
        follow (dict): Diccionario de conjuntos FOLLOW.

    Returns:
        dict: Tabla predictiva como un diccionario de tuplas (no_terminal, terminal) -> producción.
    """
    table = {}
    for lhs in productions:
        for production in productions[lhs]:
            first_alpha = set()
            # Calcula FIRST de la producción
            for symbol in production:
                if symbol.isupper():
                    first_alpha.update(first.get(symbol, set()))
                    if 'ε' not in first.get(symbol, set()):
                        break
                else:
                    first_alpha.add(symbol)
                    break
            # Llena la tabla con los terminales de FIRST
            for terminal in first_alpha:
                if terminal != 'ε':
                    table[(lhs, terminal)] = production
            # Si hay epsilon, usa FOLLOW
            if 'ε' in first_alpha:
                for terminal in follow.get(lhs, set()):
                    table[(lhs, terminal)] = production
            if 'ε' in first_alpha and '$' in follow.get(lhs, set()):
                table[(lhs, '$')] = production
    return table

def print_predictive_table(table):
    """
    Imprime la tabla predictiva LL(1) en formato legible.
    Args:
        table (dict): Tabla predictiva a imprimir.
    """
    print("*****TABLA PREDICTIVA*****")
    for key, value in table.items():
        print(f"{key} : {value}")

def process_grammar_file(filename):
    """
    Procesa un archivo de gramática, calcula FIRST, FOLLOW y la tabla predictiva, y retorna los resultados como string.

    Args:
        filename (str): Nombre del archivo de gramática.

    Returns:
        str: Resultados del análisis (FIRST, FOLLOW, tabla predictiva).
    """
    output = []
    productions = {}
    grammar = open(resource_path(filename), "r", encoding="utf-8", errors="replace")
    
    first = {}
    follow = {}
    
    # Procesa cada línea del archivo de gramática
    for prod in grammar:
        l = re.split("( /->/\n/)*", prod)
        m = []
        for i in l:
            if i == "" or i is None or i == '\n' or i == " " or i == "-" or i == ">":
                pass
            else:
                m.append(i)
        
        left_prod = m.pop(0)
        right_prod = []
        t = []
        
        for j in m:
            if j != '|':
                t.append(j)
            else:
                right_prod.append(t)
                t = []
        
        right_prod.append(t)
        productions[left_prod] = right_prod
    
    # Calcula FIRST para cada no terminal
    for s in productions.keys():
        first[s] = cal_first(s, productions)
    
    output.append(f"\n=== Archivo: {filename} ===")
    output.append("*****FIRST*****")
    for lhs, rhs in first.items():
        output.append(f"{lhs} : {rhs}")
    
    # Inicializa FOLLOW vacío y lo calcula para cada no terminal
    for lhs in productions:
        follow[lhs] = set()
    
    for s in productions.keys():
        follow[s] = cal_follow(s, productions, first)
    
    output.append("\n*****FOLLOW*****")
    for lhs, rhs in follow.items():
        output.append(f"{lhs} : {rhs}")
    
    # Construye la tabla predictiva
    table = build_predictive_table(productions, first, follow)
    output.append("*****TABLA PREDICTIVA*****")
    for key, value in table.items():
        output.append(f"{key} : {value}")
    
    grammar.close()
    return "\n".join(output)

def load_file_content(filename):
    try:
        with open(resource_path(filename), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al abrir {filename}: {e}"

def run_analysis(selected_files, output_widget):
    output_widget.delete(1.0, tk.END)
    for file in selected_files:
        if os.path.exists(file):
            resultado = process_grammar_file(file)
            output_widget.insert(tk.END, resultado + "\n")
        else:
            output_widget.insert(tk.END, f"Archivo no encontrado: {file}\n")

def main():
    root = tk.Tk()
    root.title("Analizador de Gramáticas LL(1)")

    # Lista de archivos
    tk.Label(root, text="Archivos de gramática disponibles:").pack()
    listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40)
    for f in GRAMMAR_FILES:
        listbox.insert(tk.END, f)
    listbox.pack()

    # Vista previa
    preview = scrolledtext.ScrolledText(root, width=60, height=10)
    preview.pack()

    def on_select(event):
        selection = listbox.curselection()
        if selection:
            filename = listbox.get(selection[0])
            content = load_file_content(filename)
            preview.delete(1.0, tk.END)
            preview.insert(tk.END, content)

    listbox.bind('<<ListboxSelect>>', on_select)

    # Área de salida
    output = scrolledtext.ScrolledText(root, width=80, height=20)
    output.pack()

    # Botón para ejecutar análisis
    def on_run():
        selected = [listbox.get(i) for i in listbox.curselection()]
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona al menos un archivo.")
            return
        run_analysis(selected, output)

    tk.Button(root, text="Ejecutar análisis", command=on_run).pack()

    # Botón para limpiar el área de salida
    def on_clear():
        output.delete(1.0, tk.END)
        preview.delete(1.0, tk.END)
        listbox.selection_clear(0, tk.END)

    tk.Button(root, text="Limpiar análisis", command=on_clear).pack()

    root.mainloop()

if __name__ == "__main__":
    GRAMMAR_FILES = [resource_path(os.path.join("gramaticas", f"grammar{i}.txt")) for i in range(1, 10)]
    main()

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

filename = resource_path(os.path.join("gramaticas", "grammar1.txt"))
with open(filename, "r") as f:
    content = f.read()
    print(content)