"""
Excecoes customizadas para a biblioteca de grafos.

Este modulo define as excecoes especificas utilizadas
para tratamento de erros em operacoes com grafos.
"""


class GraphException(Exception):
    """
    Excecao base para todos os erros relacionados a grafos.

    Esta e a classe pai de todas as excecoes especificas
    da biblioteca de grafos.
    """
    pass


class InvalidVertexException(GraphException):
    """
    Excecao lancada quando um indice de vertice e invalido.

    Um vertice e considerado invalido quando:
    - O indice e negativo
    - O indice e maior ou igual ao numero de vertices do grafo
    """

    def __init__(self, message: str = None, vertex: int = None, max_vertex: int = None):
        """
        Inicializa a excecao.

        Args:
            message: Mensagem de erro customizada
            vertex: Indice do vertice invalido
            max_vertex: Indice maximo valido
        """
        if message is None and vertex is not None and max_vertex is not None:
            message = (f"Vertice {vertex} invalido. "
                      f"Deve estar entre 0 e {max_vertex}")
        super().__init__(message)


class InvalidEdgeException(GraphException):
    """
    Excecao lancada para operacoes de aresta invalidas.

    Uma aresta pode ser invalida quando:
    - Tentativa de criar um laco (u == v)
    - Tentativa de operar em aresta inexistente
    - Vertices da aresta sao invalidos
    """

    def __init__(self, message: str):
        """
        Inicializa a excecao.

        Args:
            message: Mensagem descrevendo o erro
        """
        super().__init__(message)

    @staticmethod
    def loop_not_allowed(u: int) -> 'InvalidEdgeException':
        """
        Cria excecao para tentativa de criar laco.

        Args:
            u: Vertice onde se tentou criar o laco

        Returns:
            Instancia de InvalidEdgeException
        """
        return InvalidEdgeException(
            f"Lacos nao sao permitidos: aresta ({u},{u})"
        )

    @staticmethod
    def edge_not_found(u: int, v: int) -> 'InvalidEdgeException':
        """
        Cria excecao para aresta inexistente.

        Args:
            u: Vertice origem
            v: Vertice destino

        Returns:
            Instancia de InvalidEdgeException
        """
        return InvalidEdgeException(
            f"Aresta ({u},{v}) nao existe"
        )
