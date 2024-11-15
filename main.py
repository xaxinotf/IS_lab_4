# main.py

from csp import CSP

def main():
    # Змінні (регіони Австралії)
    variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']

    # Області визначення (кольори)
    domains = {
        'WA': ['Red', 'Green', 'Blue', 'Yellow'],
        'NT': ['Red', 'Green', 'Blue', 'Yellow'],
        'SA': ['Red', 'Green', 'Blue', 'Yellow'],
        'Q': ['Red', 'Green', 'Blue', 'Yellow'],
        'NSW': ['Red', 'Green', 'Blue', 'Yellow'],
        'V': ['Red', 'Green', 'Blue', 'Yellow'],
        'T': ['Red', 'Green', 'Blue', 'Yellow'],  # Тасманія не має сусідів
    }

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

    # Функція обмежень: сусідні регіони повинні мати різні кольори
    def constraints(var1, val1, var2, val2):
        return val1 != val2

    # Створення екземпляра CSP
    csp = CSP(variables, domains, neighbors, constraints)

    # Розв'язання CSP
    solution = csp.solve()

    # Виведення логів кроків
    print("\nЛог кроків:")
    for step in csp.step_log:
        print(step)

    # Виведення розв'язку та кількості кроків
    if solution:
        print("\nРозв'язок:")
        for var in sorted(solution.keys()):
            print(f"{var} = {solution[var]}")
        print(f"\nЗагальна кількість кроків (вартість шляху): {csp.num_steps}")
    else:
        print("\nРозв'язок не знайдено.")

if __name__ == "__main__":
    main()
