# Passo 1 — Criar a classe Node (representa cada nó da árvore)
class Node:
    def __init__(self, value):
        # Passo 2 — Guardar o valor do nó e a lista de filhos
        self.value = value
        self.children = []

    # Passo 3 — Método para adicionar um filho ao nó
    def add_child(self, child_node):
        self.children.append(child_node)

    # Passo 4 — Método para verificar se o nó é folha (sem filhos)
    def is_leaf(self):
        return len(self.children) == 0


# Passo 5 — Criar a classe Tree (representa a árvore inteira)
class Tree:
    def __init__(self, root_value):
        # Passo 6 — Criar o nó raiz da árvore
        self.root = Node(root_value)

    # Passo 7 — Implementar a busca em profundidade (DFS)
    def dfs(self, start_node=None, result=None):
        # Passo 7.1 — Se nenhum nó inicial foi passado, começar pela raiz
        if start_node is None:
            start_node = self.root

        # Passo 7.2 — Criar a lista de resultados na primeira chamada
        if result is None:
            result = []

        # Passo 7.3 — Visitar o nó atual
        result.append(start_node.value)

        # Passo 7.4 — Recursão: visitar cada filho
        for child in start_node.children:
            self.dfs(child, result)

        return result

    # Passo 8 — Implementar a busca em largura (BFS)
    def bfs(self):
        # Passo 8.1 — Usar uma fila para armazenar nós a serem visitados
        queue = [self.root]
        result = []

        # Passo 8.2 — Enquanto houver nós na fila
        while queue:
            # Passo 8.3 — Retirar o primeiro da fila
            current = queue.pop(0)
            result.append(current.value)

            # Passo 8.4 — Inserir seus filhos na fila
            queue.extend(current.children)

        return result

    # Passo 9 — Imprimir a árvore no console com hierarquia
    def print_tree(self, node=None, level=0):
        # Passo 9.1 — Se nenhum nó foi passado, começar pela raiz
        if node is None:
            node = self.root

        # Passo 9.2 — Imprimir com recuo proporcional ao nível
        print("  " * level + str(node.value))

        # Passo 9.3 — Recursão: imprimir os filhos com nível + 1
        for child in node.children:
            self.print_tree(child, level + 1)
