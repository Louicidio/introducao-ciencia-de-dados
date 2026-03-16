class Livro:
    def __init__ (self, titulo, autor, ISBN, disponibilidade):
        self.titulo = titulo
        self.autor = autor
        self.ISBN = ISBN
        self.disponibilidade = disponibilidade
    
class Biblioteca:
    def __init__ (self):
        self.livros = []

    def emprestimo(self, livro):
        if livro.disponibilidade:
            livro.disponibilidade = False
            return f"Empréstimo realizado: {livro.titulo} por {livro.autor}"
        else:
            return "Livro indisponível para empréstimo"
    def buscar_livro(self, titulo):
        for livro in self.livros:
            if livro.titulo == titulo:
                return f"Livro encontrado: {livro.titulo} por {livro.autor}"
        return "Livro não encontrado"
    
class Usuario:
    def __init__(self, nome, CPF, lista_livros):
        self.nome = nome
        self.CPF = CPF
        self.lista_livros = lista_livros

livro1 = Livro("O Alquimista", "Paulo Coelho", "123456789", True)
Usuario = Usuario("Luise", "12345678900", [livro1])
Biblioteca = Biblioteca()
print(Biblioteca.emprestimo(livro1))
print(Biblioteca.buscar_livro("O Alquimista"))



        