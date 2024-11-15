## **1. Визначення задачі CSP**

### **Множина змінних (Xi)**
Я визначив множину змінних `Xi` як регіони Австралії, які потребують розфарбування. Це дозволяє моделювати задачу розфарбування карти, де кожен регіон є окремою змінною:
```python
variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
```

### **Області визначення (Di)**
Для кожної змінної я встановив непорожню область визначення `Di`, що містить можливі кольори. Я додав чотири кольори (`'Red'`, `'Green'`, `'Blue'`, `'Yellow'`), щоб забезпечити достатню гнучкість для уникнення конфліктів між сусідніми регіонами:
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
Я визначив множину обмежень `Ci`, де сусідні регіони повинні мати різні кольори. Це було реалізовано через функцію `constraints`, яка перевіряє, чи два сусідні регіони мають різні значення:
```python
def constraints(var1, val1, var2, val2):
    return val1 != val2
```
Цю функцію я застосував до всіх пар сусідніх регіонів у файлі `main.py`.

## **2. Реалізація задачі CSP**

### **Клас CSP (`csp.py`)**
Я створив клас `CSP`, який відповідає за управління змінними, доменами, обмеженнями та процесом пошуку розв'язку з використанням пошуку з поверненням та евристик.

Основні компоненти класу:
- **Ініціалізація**: Зберігаються змінні, початкові домени, сусіди та функція обмежень.
- **Перевірка повноти**: Метод `is_complete` перевіряє, чи всі змінні мають призначення.
- **Перевірка сумісності**: Метод `is_consistent` перевіряє, чи не порушує поточне призначення обмежень з уже призначеними змінними.
- **Forward Checking**: Метод `forward_checking` видаляє недопустимі значення з доменів сусідів після призначення значення змінній.
- **Вибір змінної**: Метод `select_unassigned_variable` використовує евристику MRV та ступеневу евристику для вибору наступної змінної.
- **Порядок значень**: Метод `order_domain_values` впорядковує значення за найменш обмежувальним принципом.
- **Backtracking**: Рекурсивний метод `backtrack` виконує пошук з поверненням.
- **Логування**: Всі кроки розв'язання логуються у список `step_log` для подальшого аналізу.

```python
# csp.py

class CSP:
    def __init__(self, variables, domains, neighbors, constraints):
        """
        Ініціалізація CSP задачі.

        :param variables: список змінних CSP.
        :param domains: словник, що відображає змінні на їхні області визначення.
        :param neighbors: словник, що відображає змінні на їхніх сусідів (з якими є обмеження).
        :param constraints: функція, яка перевіряє, чи виконуються обмеження між двома змінними.
        """
        self.variables = variables  # Змінні CSP
        self.initial_domains = domains  # Початкові домени змінних
        self.neighbors = neighbors  # Сусіди кожної змінної
        self.constraints = constraints  # Функція обмежень
        self.assignments = {}  # Поточні призначення змінних
        self.num_steps = 0  # Вартість шляху (кількість кроків)
        self.step_log = []  # Лог кроків

    def is_complete(self):
        """Перевірка, чи є призначення повним."""
        return len(self.assignments) == len(self.variables)

    def is_consistent(self, var, value, assignments):
        """Перевірка, чи не порушує призначення обмежень."""
        for neighbor in self.neighbors.get(var, []):
            if neighbor in assignments:
                if not self.constraints(var, value, neighbor, assignments[neighbor]):
                    self.step_log.append(f"Конфлікт: {var}={value} не сумісний з {neighbor}={assignments[neighbor]}")
                    return False
        return True

    def forward_checking(self, var, value, domains, removed):
        """Виконує Forward Checking після присвоєння значення змінній."""
        for neighbor in self.neighbors.get(var, []):
            if neighbor not in self.assignments:
                for neighbor_value in domains[neighbor][:]:
                    if not self.constraints(var, value, neighbor, neighbor_value):
                        domains[neighbor].remove(neighbor_value)
                        removed.setdefault(neighbor, []).append(neighbor_value)
                        self.step_log.append(f"Forward Checking: видалено {neighbor_value} з домену {neighbor}")
                if not domains[neighbor]:
                    self.step_log.append(
                        f"Forward Checking: домен змінної {neighbor} став порожнім після видалення значень")
                    return False
        return True

    def restore_domains(self, domains, removed):
        """Відновлює домени після повернення."""
        for var, values in removed.items():
            domains[var].extend(values)
            self.step_log.append(f"Відновлення домену змінної {var}: {values}")

    def select_unassigned_variable(self, domains):
        """Вибір непризначеної змінної за допомогою евристик MRV та ступеневої."""
        unassigned_vars = [v for v in self.variables if v not in self.assignments]

        if not unassigned_vars:
            return None

        # Евристика MRV: змінна з мінімальною кількістю можливих значень
        min_domain_size = min(len(domains[var]) for var in unassigned_vars)
        mrv_vars = [var for var in unassigned_vars if len(domains[var]) == min_domain_size]

        if len(mrv_vars) == 1:
            selected_var = mrv_vars[0]
            self.step_log.append(f"Вибрано змінну за MRV: {selected_var}")
            return selected_var

        # Ступенева евристика: змінна з найбільшою кількістю обмежень на непризначені змінні
        max_degree = -1
        selected_var = None
        for var in mrv_vars:
            degree = sum(1 for neighbor in self.neighbors.get(var, []) if neighbor not in self.assignments)
            if degree > max_degree:
                max_degree = degree
                selected_var = var
        self.step_log.append(f"Вибрано змінну за ступеневою евристикою: {selected_var}")
        return selected_var

    def order_domain_values(self, var, domains):
        """Впорядкувати значення змінної за евристикою найменш обмежувального значення."""
        if var not in domains:
            return []

        def count_conflicts(value):
            count = 0
            for neighbor in self.neighbors.get(var, []):
                if neighbor not in self.assignments:
                    for neighbor_value in domains[neighbor]:
                        if not self.constraints(var, value, neighbor, neighbor_value):
                            count += 1
            return count

        ordered_values = sorted(domains[var], key=lambda val: count_conflicts(val))
        self.step_log.append(f"Впорядковані значення для {var}: {ordered_values}")
        return ordered_values

    def backtrack(self, domains):
        """Пошук з поверненням."""
        if self.is_complete():
            return self.assignments

        var = self.select_unassigned_variable(domains)
        if var is None:
            return None

        for value in self.order_domain_values(var, domains):
            if self.is_consistent(var, value, self.assignments):
                self.step_log.append(f"Призначено: {var} = {value}")
                self.assignments[var] = value
                self.num_steps += 1

                removed = {}
                if self.forward_checking(var, value, domains, removed):
                    result = self.backtrack(domains)
                    if result:
                        return result
                # Backtrack
                self.step_log.append(f"Знято призначення: {var} = {value}")
                del self.assignments[var]
                self.num_steps += 1
                self.restore_domains(domains, removed)
        return None

    def solve(self):
        """Розв'язання задачі CSP."""
        # Ініціалізація призначень та вартості шляху
        self.assignments = {}
        self.num_steps = 0
        self.step_log = []
        self.step_log.append("Початок розв'язання CSP")
        # Створення копії початкових доменів
        domains = {var: list(values) for var, values in self.initial_domains.items()}
        result = self.backtrack(domains)
        self.step_log.append("Розв'язання завершено")
        return result
```

### **Основний файл (`main.py`)**
У файлі `main.py` я визначив змінні, області визначення, сусідів та функцію обмежень. Потім створив екземпляр класу `CSP` та виконав розв'язання задачі. Після знаходження розв'язку, я додав візуалізацію результату за допомогою бібліотек `networkx` та `matplotlib` для наочного представлення розфарбування регіонів.

```python
# main.py

from csp import CSP
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

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

        # Візуалізація розв'язку
        G = nx.Graph()

        # Додавання вузлів
        for var in variables:
            G.add_node(var)

        # Додавання ребер
        for var, neighs in neighbors.items():
            for neigh in neighs:
                if not G.has_edge(var, neigh):
                    G.add_edge(var, neigh)

        # Створення кольорової мапи
        color_mapping = {
            'Red': 'red',
            'Green': 'green',
            'Blue': 'blue',
            'Yellow': 'yellow'
        }

        node_colors = [color_mapping[solution[var]] for var in G.nodes()]

        pos = nx.spring_layout(G, seed=42)  # Фіксований layout для стабільності

        plt.figure(figsize=(8,6))
        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1500, font_size=12, font_weight='bold', edge_color='black')

        # Створення легенди
        patches = [mpatches.Patch(color=color, label=color) for color in color_mapping.keys()]
        plt.legend(handles=patches, title="Кольори", loc='upper right')

        plt.title("Розфарбування карти Австралії")
        plt.show()

    else:
        print("\nРозв'язок не знайдено.")

if __name__ == "__main__":
    main()
```

## **3. Виконання вимог**

Я реалізував задачу задоволення обмежень (CSP) згідно з усіма заданими вимогами:

### **Множина змінних (Xi)**
Я визначив змінні як регіони Австралії, які потребують розфарбування:
```python
variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
```

### **Області визначення (Di)**
Для кожної змінної я встановив область визначення `Di`, що містить можливі кольори. Це дозволяє змінним мати різні області визначення різного розміру та типу:
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
Я встановив обмеження, що сусідні регіони повинні мати різні кольори, через функцію `constraints`:
```python
def constraints(var1, val1, var2, val2):
    return val1 != val2
```
Цю функцію я застосував до всіх пар сусідніх регіонів у словнику `neighbors`.

### **Початковий стан**
Початковий стан визначений як пусте присвоєння `{}`, де жодна змінна не має призначеного значення. Це реалізовано через ініціалізацію словника `assignments` у класі `CSP`:
```python
self.assignments = {}
```

### **Крок функція присвоєння**
На кожному кроці алгоритм вибирає змінну з непризначеним значенням, використовуючи евристики MRV та ступеневу евристику, та присвоює їй найменш обмежувальне значення:
```python
var = self.select_unassigned_variable(domains)
for value in self.order_domain_values(var, domains):
    if self.is_consistent(var, value, self.assignments):
        self.assignments[var] = value
        self.num_steps += 1
        # Forward checking та рекурсивний виклик
```

### **Перевірка мети**
Після кожного присвоєння алгоритм перевіряє, чи всі змінні мають призначення, тобто чи досягнуто повне присвоєння:
```python
def is_complete(self):
    return len(self.assignments) == len(self.variables)
```

### **Вартість шляху**
Я відстежую кількість кроків розв'язання через змінну `num_steps`, яка збільшується на 1 після кожного призначення або зняття призначення змінної:
```python
self.num_steps += 1
```

### **Пошук з поверненням**
Я використовую рекурсивний алгоритм пошуку в глибину з поверненням (`backtrack`), який призначає значення змінним та повертається назад у випадку конфліктів або неможливості продовження:
```python
def backtrack(self, domains):
    if self.is_complete():
        return self.assignments
    var = self.select_unassigned_variable(domains)
    for value in self.order_domain_values(var, domains):
        if self.is_consistent(var, value, self.assignments):
            self.assignments[var] = value
            self.num_steps += 1
            removed = {}
            if self.forward_checking(var, value, domains, removed):
                result = self.backtrack(domains)
                if result:
                    return result
            del self.assignments[var]
            self.num_steps += 1
            self.restore_domains(domains, removed)
    return None
```

### **Евристики для покращення ефективності**

- **Minimum Remaining Values (MRV)**: Я обираю змінну з найменшою кількістю можливих значень у домені для подальшого присвоєння:
    ```python
    def select_unassigned_variable(self, domains):
        unassigned_vars = [v for v in self.variables if v not in self.assignments]
        min_domain_size = min(len(domains[var]) for var in unassigned_vars)
        mrv_vars = [var for var in unassigned_vars if len(domains[var]) == min_domain_size]
        if len(mrv_vars) == 1:
            selected_var = mrv_vars[0]
            self.step_log.append(f"Вибрано змінну за MRV: {selected_var}")
            return selected_var
        # Далі ступенева евристика
    ```

- **Ступенева евристика (degree)**: Якщо декілька змінних мають однаковий MRV, я обираю ту, яка бере участь у найбільшій кількості обмежень з непризначеними змінними:
    ```python
    for var in mrv_vars:
        degree = sum(1 for neighbor in self.neighbors.get(var, []) if neighbor not in self.assignments)
        if degree > max_degree:
            max_degree = degree
            selected_var = var
    self.step_log.append(f"Вибрано змінну за ступеневою евристикою: {selected_var}")
    return selected_var
    ```

- **Евристика найменш обмежувального значення**: Я впорядковую значення змінної таким чином, щоб спочатку обирати те, яке найменше обмежує вибір значень для сусідніх змінних:
    ```python
    def order_domain_values(self, var, domains):
        def count_conflicts(value):
            count = 0
            for neighbor in self.neighbors.get(var, []):
                if neighbor not in self.assignments:
                    for neighbor_value in domains[neighbor]:
                        if not self.constraints(var, value, neighbor, neighbor_value):
                            count += 1
            return count
        ordered_values = sorted(domains[var], key=lambda val: count_conflicts(val))
        self.step_log.append(f"Впорядковані значення для {var}: {ordered_values}")
        return ordered_values
    ```

### **Візуалізація та Інтерфейс**
Для покращення інтерфейсу я використав бібліотеки `networkx` та `matplotlib` для візуалізації розфарбування карти Австралії. Це дозволяє наочно бачити результат розв'язання задачі CSP:
```python
# Візуалізація розв'язку
G = nx.Graph()

# Додавання вузлів
for var in variables:
    G.add_node(var)

# Додавання ребер
for var, neighs in neighbors.items():
    for neigh in neighs:
        if not G.has_edge(var, neigh):
            G.add_edge(var, neigh)

# Створення кольорової мапи
color_mapping = {
    'Red': 'red',
    'Green': 'green',
    'Blue': 'blue',
    'Yellow': 'yellow'
}

node_colors = [color_mapping[solution[var]] for var in G.nodes()]

pos = nx.spring_layout(G, seed=42)  # Фіксований layout для стабільності

plt.figure(figsize=(8,6))
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1500, font_size=12, font_weight='bold', edge_color='black')

# Створення легенди
patches = [mpatches.Patch(color=color, label=color) for color in color_mapping.keys()]
plt.legend(handles=patches, title="Кольори", loc='upper right')

plt.title("Розфарбування карти Австралії")
plt.show()
```

