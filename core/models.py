from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Optional, List

class RawThought(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    content: str

class ExtractedTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    context_hints: list[str]
    parent_thought_id: str | None = None

class Plan(BaseModel):
    tasks: list[ExtractedTask]
    current_context: str
    suggested_order: list[str]
    rationaly: str | None = None

if __name__ == "__main__":
    thought = RawThought(content="Хочу выучить Python и сходить в магазин")
    print(thought)

    task1 = ExtractedTask(title="Купить хлеб", context_hints=["магазин", "у дома"])
    task2 = ExtractedTask(title="Пройти урок по Python", context_hints=["дома", "ноутбук"])
    print(task1, task2)

    plan = Plan(
        tasks=[task1, task2],
        current_context="дома, вечер",
        suggested_order=[task1.id, task2.id],
        rationale="Сначала магазин, потому что он закроется"
    )
    print(plan)