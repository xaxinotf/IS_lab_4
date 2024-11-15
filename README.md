 `csp.py` та `main.py`

## **1. Визначення задачі CSP**

### **Множина змінних (Xi)**
Я визначив множину змінних `Xi` як регіони Австралії, які потрібно розфарбувати:
```python
variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
```

### **Області визначення (Di)**
Для кожної змінної я встановив непорожню область визначення `Di` можливих кольорів. Враховуючи потребу у розфарбуванні карти, я додав чотири кольори, щоб забезпечити достатню гнучкість для уникнення конфліктів:
```python
domains = {
    'WA': ['Red', 'Green', 'Blue', 'Yellow'],
    'NT': ['Red', 'Green', 'Blue', 'Yellow'],
    'SA': ['Red', 'Green', 'Blue', 'Yellow'],
    'Q': ['Red', 'Green', 'Blue', 'Yellow'],
    'NSW': ['Red', 'Green', 'Blue', 'Yellow'],
    'V': ['Red', 'Green', 'Blue', 'Yellow'],
    'T': ['Red', 'Green', 'Blue', 'Yellow'],  # Тасманія не має сусідів
}
```

### **Множина обмежень (Ci)**
Я визначив множину обмежень `Ci`, де сусідні регіони повинні мати різні кольори. Це було реалізовано через функцію `constraints`:
```python
def constraints(var1, val1, var2, val2):
    return val1 != val2
```
Цю функцію я застосував до всіх пар сусідніх регіонів у файлі `main.py`:
```python
for region in variables:
    for neighbor in neighbors.get(region, []):
        problem.addConstraint(lambda x, y: x != y, (region, neighbor))
```

## **2. Створення класу CSP з пошуком з поверненням та евристиками**

### **Клас `CSP`**
Я створив клас `CSP`, який інкапсулює всю логіку розв'язання задачі CSP, включаючи методи для перевірки повноти та сумісності призначень, Forward Checking, відновлення доменів, вибір змінних за евристиками та сам алгоритм пошуку з поверненням:
```python
class CSP:
    def __init__(self, variables, domains, neighbors, constraints):
        ...
```

### **Пошук з поверненням (Backtracking)**
Метод `backtrack` реалізує пошук з поверненням, який рекурсивно призначає значення змінним, перевіряє сумісність та використовує Forward Checking для підвищення ефективності:
```python
def backtrack(self, domains):
    ...
```

### **Евристики для підвищення ефективності**

#### **1. Евристика з мінімальною кількістю решти значень (MRV)**
У методі `select_unassigned_variable` я реалізував евристику MRV, яка обирає змінну з найменшою кількістю можливих значень для присвоєння:
```python
def select_unassigned_variable(self, domains):
    ...
    min_domain_size = min(len(domains[var]) for var in unassigned_vars)
    mrv_vars = [var for var in unassigned_vars if len(domains[var]) == min_domain_size]
    ...
```

#### **2. Ступенева евристика (Degree Heuristic)**
Якщо є кілька змінних з однаковим MRV, я використовую ступеневу евристику для вибору змінної з найбільшою кількістю сусідів:
```python
if len(mrv_vars) == 1:
    selected_var = mrv_vars[0]
    self.step_log.append(f"Вибрано змінну за MRV: {selected_var}")
    return selected_var

# Ступенева евристика
max_degree = -1
selected_var = None
for var in mrv_vars:
    degree = sum(1 for neighbor in self.neighbors.get(var, []) if neighbor not in self.assignments)
    if degree > max_degree:
        max_degree = degree
        selected_var = var
self.step_log.append(f"Вибрано змінну за ступеневою евристикою: {selected_var}")
return selected_var
```

#### **3. Евристика з найменш обмежувальним значенням (Least Constraining Value)**
У методі `order_domain_values` я впорядкував значення змінної за кількістю конфліктів, щоб обирати найменш обмежувальні значення:
```python
def order_domain_values(self, var, domains):
    ...
    ordered_values = sorted(domains[var], key=lambda val: count_conflicts(val))
    self.step_log.append(f"Впорядковані значення для {var}: {ordered_values}")
    return ordered_values
```

## **3. Візуалізація результату**

Для покращення інтерфейсу я додав візуалізацію розфарбованої карти Австралії за допомогою бібліотек `networkx` та `matplotlib`. Це дозволяє наочно бачити, які регіони якими кольорами розфарбовані, і перевірити коректність розв'язку.

### **Візуалізація графу**
У файлі `main.py` я реалізував наступний код для візуалізації:
```python
import networkx as nx
import matplotlib.pyplot as plt

def main():
    ...
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
```

### **Пояснення**
- **Створення графу:** Використовуючи `networkx`, я створюю граф, де вузли представляють регіони, а ребра — сусідні зв'язки.
- **Кольори вузлів:** Кожен вузол отримує колір відповідно до розв'язку CSP.
- **Автоматичне розташування:** Використовую `spring_layout` для автоматичного розташування вузлів на графі.
- **Візуалізація:** `matplotlib` використовується для відображення графу з розфарбованими регіонами.

## **4. Тестування та Відлагодження**

Я провів тестування коду, щоб переконатися, що розв'язок знаходиться коректно, і додав логування кроків для відстеження процесу розв'язання. Вивід логів допомагає зрозуміти, які змінні були призначені, які обмеження перевірялись, та які значення були видалені з доменів під час Forward Checking.

