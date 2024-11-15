from constraint import Problem
import networkx as nx
import matplotlib.pyplot as plt

def main():
    # Змінні (регіони Австралії)
    variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']

    # Області визначення (кольори)
    colors = ['Red', 'Green', 'Blue', 'Yellow']  # Додано більше кольорів

    # Створення проблеми
    problem = Problem()

    # Додавання змінних
    problem.addVariables(variables, colors)

    # Сусіди (суміжні регіони)
    neighbors = {
        'WA': ['NT', 'SA'],
        'NT': ['WA', 'SA', 'Q', 'NSW'],
        'SA': ['WA', 'NT', 'Q', 'NSW', 'V'],
        'Q': ['NT', 'SA', 'NSW'],
        'NSW': ['SA', 'Q', 'V', 'NT'],
        'V': ['SA', 'NSW'],
        'T': [],  # Тасманія не має сусідів
    }

    # Додавання обмежень: сусідні регіони повинні мати різні кольори
    for region in variables:
        for neighbor in neighbors.get(region, []):
            problem.addConstraint(lambda x, y: x != y, (region, neighbor))

    # Пошук розв'язку
    solution = problem.getSolution()

    # Виведення розв'язку та візуалізація
    if solution:
        print("Розв'язок:")
        for var in sorted(solution.keys()):
            print(f"{var} = {solution[var]}")

        # Створення графу
        G = nx.Graph()

        # Додавання вузлів з кольорами
        for region in variables:
            G.add_node(region, color=solution[region])

        # Додавання ребер
        for region in variables:
            for neighbor in neighbors.get(region, []):
                G.add_edge(region, neighbor)

        # Отримання кольорів для візуалізації
        node_colors = [G.nodes[node]['color'].lower() for node in G.nodes()]

        # Отримання позицій вузлів автоматично
        pos = nx.spring_layout(G, seed=42)

        # Візуалізація графу
        plt.figure(figsize=(8, 6))
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1500, edgecolors='black')
        nx.draw_networkx_edges(G, pos, width=2)
        nx.draw_networkx_labels(G, pos, font_size=12, font_color='white', font_weight='bold')

        plt.title("Розфарбування карти Австралії")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    else:
        print("Розв'язок не знайдено.")

if __name__ == "__main__":
    main()
