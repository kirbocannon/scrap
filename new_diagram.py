from pyclbr import Class
from types import NoneType
from typing import Optional

from graphviz import Digraph

from iflow import Company

from pydantic import BaseModel

import inspect

import importlib.util

from typing import Dict, List, Union


class ClassNode:
    def __init__(self, name: str) -> None:
        self.name = name
        self.field_map = []
        self.model_ref_annotations = []

    def __eq__(self, other):
        if isinstance(other, ClassNode):
            return (self.name) == (other.name)
        return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"Class: {self.name} -> Fields: {self.field_map} (Pydantic Model Refs: {self.model_ref_annotations})"


# pydantic_classes = [cls for name, cls in globals().items() if inspect.isclass(cls) and issubclass(cls, BaseModel)]
# print(pydantic_classes)


# Load the module
module_name = "iflow"
spec = importlib.util.spec_from_file_location(
    module_name, "iflow.py"
)  # Replace "/path/to/module.py" with the path to your module
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
# fmt: off
# Get all classes from the module
pydantic_classes = [cls for name, cls in inspect.getmembers(module, inspect.isclass) if issubclass(cls, BaseModel)]

class_nodes = {}
for cls in pydantic_classes:
    cls_name = cls.__name__
    for field_name, field in cls.model_fields.items():
        field_map = {}
        model_ref_annotations = []
        if field.annotation.__class__.__name__ == "_GenericAlias":
            annotation = field.annotation.__args__[0].__name__
            if field.annotation._name:
                field_map[field_name] = {field.annotation._name: annotation}
            else:
                field_map[field_name] = annotation
            if issubclass(field.annotation.__args__[0], BaseModel):
                model_ref_annotations.append(field.annotation.__args__[0].__name__)
        elif field.annotation.__class__.__name__ == "_UnionGenericAlias":
            if field.annotation._name == "Optional":
                field_map[field_name] = {"Optional": field.annotation.__args__[0].__name__}
                model_ref_annotations.append(field.annotation.__args__[0].__name__)
            else:
                annotation = [i.__name__ for i in field.annotation.__args__ if issubclass(i, BaseModel)]
                field_map[field_name] = {field.annotation.__origin__.__name__: [i.__name__ for i in field.annotation.__args__]}
                model_ref_annotations.extend(annotation)
        else:
            field_map[field_name] = field.annotation.__name__
            if issubclass(field.annotation, BaseModel):
                model_ref_annotations.append(field.annotation.__name__)

        n = ClassNode(name=cls_name)

        if class_nodes.get(cls_name):
            class_nodes[cls_name].field_map.append(field_map)
            class_nodes[cls_name].model_ref_annotations.extend(model_ref_annotations)
        else:
            n.field_map.append(field_map)
            n.model_ref_annotations.extend(model_ref_annotations)
            class_nodes[cls_name] = n





# def generate_dependency_diagram(class_nodes: Dict[str, List[str]]):
#     dot = Digraph()

#     for name, node in class_nodes.items():
#         dot.node(name)
#         for annotation in node.model_ref_annotations:
#             dot.edge(name, annotation, label=None)

#     dot.render("dependency_diagram", format="png", cleanup=True)

#generate_dependency_diagram(class_nodes)


def find_list_value(list_of_dicts: dict, key: str) -> Union[str, None]:
    for d in list_of_dicts:
        if key in d:
            return d[key]
    return None


def clean(annotation_dict: dict):
    annotation_str = ""
    for k, v in annotation_dict.items():
        if isinstance(v, list):
            annotation_str = f"{k}[{'-'.join(v)}]"
        else:
            annotation_str = f"{k}[{v}]"
    annotation_str = annotation_str.replace(",", "_")

    return annotation_str


def recursive_search(list_of_dicts: dict, target: str) -> Union[str, None]:
    for d in list_of_dicts:
        for key, value in d.items():
            if isinstance(value, dict):
                result = recursive_search([value], target)
                if result:
                    return result
            elif isinstance(value, str) and key == target:
                return value
            
    return None

# mermaid_code = "graph TD;\n"
# for class_name, class_node in class_nodes.items():
#     mermaid_code += f"    {class_name}\n"
#     for annotation in class_node.model_ref_annotations:
#         mermaid_code += f"    {class_name} --> {annotation}\n"

# print(mermaid_code)

mermaid_code = "erDiagram\n"
for class_name, class_node in class_nodes.items():
    mermaid_code += f"    {class_name} {{\n"
    for field in class_node.field_map:
        for name, type_ in field.items():
            if not isinstance(type_, dict):
                mermaid_code += f"        {type_} {name}\n"
            else:
                mermaid_code += f"        {clean(type_)} {name}\n"
    mermaid_code += "    }\n"

class_names = list(class_nodes.keys())
for class_name, class_node in class_nodes.items():
    print(class_node.field_map)
    for ref in class_node.model_ref_annotations:
        if ref == recursive_search(class_node.field_map, 'List'):
            mermaid_code += f'    {class_name} ||--o{{ {ref} : "" \n'
        else:
            mermaid_code += f'    {class_name} ||--|| {ref} : "" \n'


# for i, k in class_nodes.items():
#     print(k)

print(mermaid_code)






# d = [{'name': 'str'}, {'location': 'Address'}, {'employees': {'List': 'Person'}}, {'daw': 'Caw'}]


# e = recursive_search(d, 'List')

# print(e)

# print(e, '---')
# print(caw)




"""    
erDiagram
    CAR ||--o{ NAMED-DRIVER : allows
    CAR {
        string registrationNumber
        string make
        string model
    }
    PERSON ||--o{ NAMED-DRIVER : is
    PERSON {
        string firstName
        string lastName
        int age
    }

"""
