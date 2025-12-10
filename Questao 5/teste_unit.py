# test_tree.py

import unittest
from questao5 import Tree, Node

class TestTree(unittest.TestCase):

    # Passo 1 — Criar uma árvore para usar nos testes
    def setUp(self):
        # Passo 1.1 — Criar a raiz (A)
        self.tree = Tree("A")

        # Passo 1.2 — Criar nós filhos
        node_b = Node("B")
        node_c = Node("C")
        node_d = Node("D")

        # Passo 1.3 — Montar a hierarquia
        # A
        # ├── B
        # │   └── D
        # └── C
        self.tree.root.add_child(node_b)
        self.tree.root.add_child(node_c)
        node_b.add_child(node_d)

        print("\nEstrutura da árvore:")
        self.tree.print_tree()
        
    # Passo 2 — Testar o DFS
    def test_dfs(self):
        expected = ["A", "B", "D", "C"]
        self.assertEqual(self.tree.dfs(), expected)

    # Passo 3 — Testar o BFS
    def test_bfs(self):
        expected = ["A", "B", "C", "D"]
        self.assertEqual(self.tree.bfs(), expected)

    # Passo 4 — Testar se os nós são folhas corretamente
    def test_is_leaf(self):
        # Passo 4.1 — Pegar o nó D e verificar se é folha
        node_d = self.tree.root.children[0].children[0]
        self.assertTrue(node_d.is_leaf())

        # Passo 4.2 — Pegar o nó B e verificar que NÃO é folha
        node_b = self.tree.root.children[0]
        self.assertFalse(node_b.is_leaf())


# Passo 5 — Rodar os testes se o arquivo for executado diretamente
if __name__ == "__main__":
    unittest.main()
