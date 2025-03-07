from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    id: int
    title: str
    description: str
    estimated_duration: float  # en heures
    priority: TaskPriority
    status: TaskStatus
    dependencies: List[int]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assigned_to: Optional[str] = None


class TaskScheduler:
    """Gestionnaire de planification des tâches agricoles"""

    def __init__(self):
        self.tasks: List[Task] = []
        self.last_id = 0

    def add_task(self, task_data: Dict) -> Task:
        """Ajoute une nouvelle tâche au planificateur"""
        self.last_id += 1
        task = Task(
            id=self.last_id,
            title=task_data["title"],
            description=task_data["description"],
            estimated_duration=task_data["estimated_duration"],
            priority=TaskPriority(task_data["priority"]),
            status=TaskStatus.PENDING,
            dependencies=task_data.get("dependencies", []),
            start_date=task_data.get("start_date"),
            end_date=task_data.get("end_date"),
            assigned_to=task_data.get("assigned_to"),
        )
        self.tasks.append(task)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Récupère une tâche par son ID"""
        return next((task for task in self.tasks if task.id == task_id), None)

    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """Met à jour le statut d'une tâche"""
        task = self.get_task(task_id)
        if task:
            task.status = status
            if status == TaskStatus.IN_PROGRESS:
                task.start_date = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                task.end_date = datetime.now()
            return True
        return False

    def get_pending_tasks(self) -> List[Task]:
        """Récupère toutes les tâches en attente"""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Récupère les tâches par niveau de priorité"""
        return [task for task in self.tasks if task.priority == priority]

    def get_tasks_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Task]:
        """Récupère les tâches dans une plage de dates"""
        return [
            task
            for task in self.tasks
            if task.start_date and start_date <= task.start_date <= end_date
        ]

    def optimize_schedule(self) -> List[Task]:
        """Optimise la planification des tâches en attente"""
        pending_tasks = self.get_pending_tasks()

        # Trier par priorité et dépendances
        pending_tasks.sort(
            key=lambda x: (
                len(x.dependencies),
                {"low": 0, "medium": 1, "high": 2, "urgent": 3}[x.priority.value],
            )
        )

        scheduled_tasks = []
        current_date = datetime.now()

        for task in pending_tasks:
            # Vérifier les dépendances
            if all(
                self.get_task(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            ):
                task.start_date = current_date
                task.end_date = current_date + timedelta(hours=task.estimated_duration)
                current_date = task.end_date
                scheduled_tasks.append(task)

        return scheduled_tasks

    def get_task_conflicts(self) -> List[Dict]:
        """Identifie les conflits potentiels dans la planification"""
        conflicts = []
        sorted_tasks = sorted(self.tasks, key=lambda x: x.start_date or datetime.max)

        for i, task1 in enumerate(sorted_tasks):
            if not task1.start_date or not task1.end_date:
                continue

            for task2 in sorted_tasks[i + 1 :]:
                if not task2.start_date or not task2.end_date:
                    continue

                if (
                    task1.start_date <= task2.end_date
                    and task2.start_date <= task1.end_date
                ):
                    conflicts.append(
                        {
                            "task1": task1,
                            "task2": task2,
                            "overlap_start": max(task1.start_date, task2.start_date),
                            "overlap_end": min(task1.end_date, task2.end_date),
                        }
                    )

        return conflicts

    def get_critical_path(self) -> List[Task]:
        """Calcule le chemin critique des tâches"""
        # Implémentation simple du chemin critique
        tasks_with_deps = [task for task in self.tasks if task.dependencies]
        critical_path = []

        while tasks_with_deps:
            # Trouver la tâche avec le plus de dépendances
            task = max(tasks_with_deps, key=lambda x: len(x.dependencies))
            critical_path.append(task)
            tasks_with_deps.remove(task)

        return critical_path

    def generate_gantt_data(self) -> List[Dict]:
        """Génère les données pour un diagramme de Gantt"""
        return [
            {
                "id": task.id,
                "title": task.title,
                "start": task.start_date.isoformat() if task.start_date else None,
                "end": task.end_date.isoformat() if task.end_date else None,
                "progress": (
                    100
                    if task.status == TaskStatus.COMPLETED
                    else 50 if task.status == TaskStatus.IN_PROGRESS else 0
                ),
                "dependencies": task.dependencies,
            }
            for task in self.tasks
        ]
