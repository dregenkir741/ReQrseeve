from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from .models import ExtractedTask, Plan

Base = declarative_base()

class TaskRecord(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    context_hints = Column(JSON, default=[])

class PlanRecord(Base):
    __tablename__ = "plans"
    id = Column(String, primary_key=True)
    task_order = Column(JSON, default=[])
    rationale = Column(String, nullable=True)

class Storage():
    def __init__(self, db_url="sqlite:///reqrseeve.db"):
        self.engine = create_engine(db_url)
        
        Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(bind=self.engine)

    def save_tasks(self, tasks: list[ExtractedTask]):
        with self.Session() as session:
            for task in tasks:
                record = TaskRecord(id=task.id, title=task.title, context_hints=task.context_hints)
                session.merge(record)
            session.commit()

    def save_plan(self, plan: Plan, plan_id: str):
        with self.Session() as session:
            record = PlanRecord(id=plan_id, task_order=plan.suggested_order, rationale=plan.rationale)
            session.merge(record)
            session.commit()
            
if __name__ == "__main__":

    storage = Storage()

    task1 = ExtractedTask(title="Купить хлеб", context_hints=["магазин", "у дома"])
    task2 = ExtractedTask(title="Пройти урок", context_hints=["дома", "ноутбук"])

    storage.save_tasks([task1, task2])
    print("Задачи сохранены")

    plan = Plan(
        tasks=[task1, task2],
        current_context="дома",
        suggested_order=[task1.id, task2.id],
        rationale="Сначала магазин"
    )
    storage.save_plan(plan, "test_plan")
    print("План сохранён")