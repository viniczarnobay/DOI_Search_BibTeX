'''
29 set 2023

Programa para busca de DOI a partir de referencias no estilo BibTeX.
A saída é a nova citação incluindo o DOI.
Diversas referencias podem ser buscadas ao mesmo tempo.

Linguagem: Python
Autor: Vinicius Czarnobay (Uso de ChatGPT)

'''

# Importe as bibliotecas necessarias
import re  # Para operações de regex (expressoes regulares)
import requests  # Para fazer solicitacoes HTTP a API do CrossRef

#------------------------------------------------------------------------------
# ENTRADAS DO USUARIO

# Insira/cole a bibliografia BibTeX conforme o exemplo:

bibtex = """
@article{mcculloch43,
  title={A logical calculus of the ideas immanent in nervous activity},
  author={McCulloch, Warren S. and Pitts, Walter},
  journal={The bulletin of mathematical biophysics},
  volume={5},
  number={4},
  pages={115--133},
  year={1943},
  publisher={Springer}
}

@article{BuracoNegro,
  title={Black hole weather forecasting with deep learning: a pilot study},
  author={Duarte, Roberta and Nemmen, Rodrigo and Navarro, Jo{\~a}o Paulo},
  journal={Monthly Notices of the Royal Astronomical Society},
  volume={512},
  number={4},
  pages={5848--5861},
  year={2022},
  publisher={Oxford University Press}
}

@inproceedings{BuckleyMorrow2010,
  title={Improved Oil Recovery by Low Salinity Waterflooding: A Mechanistic Review},
  author={Buckley, Jill S. and Morrow, Norman R.},
  organization={ 11{th} International Symposium on Reservoir Wettability},
  year={2010},
  publisher={University of Calgary},
  address={Calgary, Alberta, Canada}
}
"""

#------------------------------------------------------------------------------

# Funcao para pesquisar o DOI de um artigo a partir do titulo e autores
def find_doi(title, authors):
    # Formate o titulo e autores para a consulta na API
    formatted_title = requests.utils.quote(title)
    formatted_authors = requests.utils.quote(authors)

    # Consulta a API do CrossRef
    url = f"https://api.crossref.org/works?query.title={formatted_title}&query.author={formatted_authors}"
    response = requests.get(url)

    # Verifique se a resposta da API e bem-sucedida (status_code 200)
    if response.status_code == 200:
        data = response.json()
        # Verifique se ha resultados na resposta da API
        if data["message"]["total-results"] > 0:
            # Extraia o DOI do primeiro resultado
            doi = data["message"]["items"][0]["DOI"]
            return doi
    return None

# Funcao para adicionar o DOI a bibliografia BibTeX
def add_doi_to_bibtex(bibtex, doi):
    # Use regex para encontrar a linha de "doi={...}" e substituir pelo DOI encontrado
    bibtex = re.sub(r'(@[^{]*{[^}]*,\s*\n\s*title\s*=\s*\{[^}]*\},)', r'\1\n  doi = {' + doi + '},', bibtex, flags=re.IGNORECASE)
    return bibtex

# Dividir a bibliografia em entradas individuais
entries = re.split(r'(?=@\w+{)', bibtex)[1:]

# Inicializar uma lista para armazenar as entradas atualizadas
bibtex_with_dois = []

# Processar cada entrada individualmente
for entry in entries:
    # Extrair informacoes da entrada
    title_match = re.search(r'title\s*=\s*\{([^}]*)\}', entry)
    author_match = re.search(r'author\s*=\s*\{([^}]*)\}', entry)

    # Verifique se tanto o titulo quanto os autores foram extraidos com sucesso
    if title_match and author_match:
        title = title_match.group(1)
        authors = author_match.group(1)

        # Pesquisar o DOI
        doi = find_doi(title, authors)

        if doi:
            # Verificar o formato do DOI
            if re.match(r'^10\.\d+\/[^\s]+$', doi):
                # Adicionar o DOI a entrada
                entry_with_doi = add_doi_to_bibtex(entry, doi)
                bibtex_with_dois.append(entry_with_doi)
            else:
                # Mantenha a entrada sem DOI se o formato for invalido
                bibtex_with_dois.append(entry)
        else:
            # Mantenha a entrada sem DOI se nao for encontrado
            bibtex_with_dois.append(entry)
    else:
        # Mantenha a entrada sem DOI se não for possivel extrair titulo e autores
        bibtex_with_dois.append(entry)

# Combine todas as entradas atualizadas em uma unica string BibTeX
final_bibtex = ''.join(bibtex_with_dois)

# Imprima a bibliografia final com DOIs

print('\n\nNew BibTeX bibliography:\n')
print(final_bibtex)