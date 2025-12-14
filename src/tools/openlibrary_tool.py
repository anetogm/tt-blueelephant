"""
Ferramenta de consulta de livros usando a API Open Library
"""

import logging
import requests
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class OpenLibraryTool:
    """Ferramenta para consultar informações sobre livros"""
    
    BASE_URL = "https://openlibrary.org"
    
    def __init__(self):
        """Inicializa a ferramenta Open Library"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChatbotIA/1.0'
        })
    
    @property
    def name(self) -> str:
        """Nome da ferramenta"""
        return "consulta_livro"
    
    @property
    def description(self) -> str:
        """Descrição da ferramenta"""
        return """Consulta informações sobre livros usando a API Open Library.
        
Parâmetros:
- query: Nome do livro ou autor

Retorna informações como:
- Título e autor(es)
- Ano de publicação
- ISBN
- Editora
- Número de páginas
- Assuntos/categorias
"""
    
    def _clean_query(self, query: str) -> str:
        
        stop_words = {
            'de', 'do', 'da', 'dos', 'das', 
            'o', 'a', 'os', 'as', 
            'em', 'no', 'na', 
            'por', 'pelo', 'pela',
            'livro', 'book', 'by', 'the', 'of', 'about', 'sobre'
        }
        
        parts = query.split()
        clean_parts = [p for p in parts if p.lower() not in stop_words]
        
        # Se a limpeza removeu tudo, usa a original
        if not clean_parts:
            return query
            
        return " ".join(clean_parts)

    def execute(self, query: str) -> Dict:
        """
        Executa consulta de livro
        """
        try:
            # limpeza na query antes de buscar
            query_clean = self._clean_query(query.strip())
            logger.info(f"Query Original: '{query}' | Query Limpa: '{query_clean}'")
            
            # Busca livro usando a query limpa
            book_result = self._search_book(query_clean)
            
            if book_result and not book_result.get("error"):
                return book_result
            
            return {
                "error": True,
                "message": f"Livro '{query}' não encontrado. Tente outro título ou autor."
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout ao consultar API Open Library")
            return {
                "error": True,
                "message": "Tempo esgotado ao consultar livros. Tente novamente."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar Open Library: {e}")
            return {
                "error": True,
                "message": f"Erro ao consultar livros: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erro inesperado na ferramenta Open Library: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Erro inesperado: {str(e)}"
            }
    
    def _search_book(self, query: str) -> Optional[Dict]:
        """Busca livro pelo título"""
        try:
            url = f"{self.BASE_URL}/search.json"
            params = {
                "q": query,
                "limit": 10,
                "fields": "key,title,author_name,first_publish_year,isbn,publisher,number_of_pages_median,subject,language,cover_i"
            }
            
            logger.info(f"Fazendo request: {url} com params: {params}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            docs = data.get("docs", [])
            
            if not docs:
                logger.warning(f"Nenhum livro encontrado para: {query}")
                return None
            
            logger.info(f"Encontrados {len(docs)} livros")
            
            # Retorna o primeiro resultado
            logger.info(f"Retornando o resultado mais relevante: {docs[0].get('title')}")
            return self._format_book(docs[0])
            
        except Exception as e:
            logger.error(f"Erro ao buscar livro: {e}", exc_info=True)
            return None
    
    def _format_book(self, book: Dict) -> Dict:
        """Formata dados do livro"""
        # Pega autores
        authors = book.get("author_name", [])
        if not authors:
            authors = ["Autor desconhecido"]
        
        # Pega ISBN
        isbn_list = book.get("isbn", [])
        isbn = isbn_list[0] if isbn_list else None
        
        # Pega editora
        publishers = book.get("publisher", [])
        publisher = publishers[0] if publishers else None
        
        # Pega assuntos
        subjects = book.get("subject", [])[:5]
        
        # Pega idiomas
        languages = book.get("language", [])
        
        return {
            "error": False,
            "type": "book",
            "key": book.get("key"),
            "title": book.get("title"),
            "authors": authors,
            "first_publish_year": book.get("first_publish_year"),
            "isbn": isbn,
            "publisher": publisher,
            "number_of_pages": book.get("number_of_pages_median"),
            "subjects": subjects,
            "languages": languages,
            "cover_id": book.get("cover_i")
        }
    
    def format_result(self, result: Dict) -> str:
        """
        Formata resultado para exibição
        """
        if result.get("error"):
            return f"**Erro**: {result.get('message', 'Erro desconhecido')}"
        
        result_type = result.get("type")
        
        if result_type == "book":
            # Título e autores
            authors_str = ", ".join(result.get("authors", [])[:3])
            year = f" ({result.get('first_publish_year')})" if result.get('first_publish_year') else ""
            
            output = f"""**{result['title']}{year}**\n"""
            output += f"\n• **Autor(es)**: {authors_str}"
            
            # Editora
            if result.get("publisher"):
                output += f"\n• **Editora**: {result['publisher']}"
            
            # Páginas
            if result.get("number_of_pages"):
                output += f"\n• **Páginas**: {result['number_of_pages']}"
            
            # ISBN
            if result.get("isbn"):
                output += f"\n• **ISBN**: {result['isbn']}"
            
            # Idiomas
            if result.get("languages"):
                langs = ", ".join(result["languages"][:3])
                output += f"\n• **Idioma(s)**: {langs}"
            
            # Assuntos/Categorias
            if result.get("subjects"):
                subjects_str = ", ".join(result["subjects"][:5])
                output += f"\n\n**Categorias**: {subjects_str}"
            
            # Link para mais informações
            if result.get("key"):
                output += f"\n\n[Ver mais no Open Library](https://openlibrary.org{result['key']})"
            
            return output
        
        elif result_type == "multiple_books":
            books_list = '\n'.join([f"  - {b}" for b in result['books']])
            return f"""**Múltiplos livros encontrados**

{result['message']}

**Opções:**
{books_list}"""
        
        return str(result)