from typing import List, Dict
from pydantic import BaseModel
from graphviz import Digraph
import inspect

from collections import defaultdict

from enum import Enum

from iflow import Caw


def get_pydantic_dependencies(classes: List[BaseModel]) -> Dict[str, List[str]]:
    dependencies = defaultdict(list)
    nested_types = defaultdict(list)
    for cls in classes:
        for field_name, field in cls.model_fields.items():
            if field.annotation.__class__.__name__ == "_GenericAlias":
                types_class = field.annotation.__args__[0]._name
                annotation = field.annotation.__args__[0].__args__[0]
                nested_types[cls.__name__].append(types_class)  # TODO: make recursive
            else:
                annotation = field.annotation
            if issubclass(annotation, BaseModel):
                dependencies[cls.__name__].append(annotation)
    return dict(dependencies=dependencies, nested_types=nested_types)


def generate_dependency_diagram(dependencies: Dict[str, List[str]]):
    dot = Digraph()

    for class_name, refs in dependencies["dependencies"].items():
        dot.node(class_name)
        nested_types = dependencies["nested_types"].get(class_name)
        if nested_types:
            label = nested_types[0]
        else:
            label = None
        for ref in refs:
            dot.edge(class_name, ref.__qualname__, label=label)

    dot.render("dependency_diagram", format="png", cleanup=True)


# Example Pydantic classes
class Address(BaseModel):
    street: str
    city: str
    zip_code: str


class Person(BaseModel):
    name: str
    age: int
    address: Address


class Company(BaseModel):
    name: str
    location: Address
    employees: List[List[Person]]
    daw: Caw
    # employees: Person


# Extract Pydantic classes from global scope
pydantic_classes = [cls for name, cls in globals().items() if inspect.isclass(cls) and issubclass(cls, BaseModel)]

# Get dependencies
dependencies = get_pydantic_dependencies(pydantic_classes)

# Generate and render the dependency diagram
generate_dependency_diagram(dependencies)
