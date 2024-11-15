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
        # Make a copy of initial domains
        domains = {var: list(values) for var, values in self.initial_domains.items()}
        result = self.backtrack(domains)
        self.step_log.append("Розв'язання завершено")
        return result
