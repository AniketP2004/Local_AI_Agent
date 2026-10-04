"""Set chapter/subtopic FKs on original questions by topic.
Run:  python -m app.scripts.backfill_fk
"""
from app.database import SessionLocal
from app.models.chapter import Chapter
from app.models.subtopic import Subtopic
from app.models.question import Question

# raw topic string in questions.topic -> (chapter name, subtopic name)
MAPPING = {
    "args_kwargs": ("Functions and Scope", "Function Basics and Arguments(**args, **kwargs, defaults)"),
    "boolean_int_subclass": ("Python Fundamentals", "Variables and datatypes"),
    "chained_comparison": ("Python Fundamentals", "Control Flow (loops, conditionals)"),
    "class_decorators": ("Functions and Scope", "Decorators"),
    "class_vs_instance_attrs": ("OOP", "Classes & Objects"),
    "cli_args": ("Modules & Packaging", "Imports & Module System"),
    "closures_scope": ("Functions and Scope", "Closures"),
    "collections": ("Data Structures", "Dictionaries and Sets"),
    "data_types": ("Python Fundamentals", "Variables and datatypes"),
    "decorator_factories": ("Functions and Scope", "Decorators"),
    "decorator_stacking": ("Functions and Scope", "Decorators"),
    "dict_creation": ("Data Structures", "Dictionaries and Sets"),
    "dict_key_coercion": ("Data Structures", "Dictionaries and Sets"),
    "dict_mutation_iteration": ("Data Structures", "Dictionaries and Sets"),
    "exception_handling": ("Error Handling", "Try/Except/Finally"),
    "exception_syntax": ("Error Handling", "Try/Except/Finally"),
    "file_io": ("Error Handling", "Context Managers (with statement)"),
    "float_rounding": ("Python Fundamentals", "Variables and datatypes"),
    "fstrings_advanced": ("Python Fundamentals", "Strings and String Formatting"),
    "function_execution": ("Functions and Scope", "Function Basics and Arguments(**args, **kwargs, defaults)"),
    "functools": ("Iterators and Generators", "itertools and functools"),
    "functools_wraps": ("Functions and Scope", "Decorators"),
    "garbage_collector": ("Memory & Performance", "Memory Management & Garbage Collections"),
    "generator_methods": ("Iterators and Generators", "Generator and yield"),
    "generator_return": ("Iterators and Generators", "Generator and yield"),
    "gotchas_sequences": ("Data Structures", "Lists & Tuples"),
    "hashability": ("Data Structures", "Dictionaries and Sets"),
    "is_operator": ("Python Fundamentals", "Mutable vs Immutable Types"),
    "is_vs_equals": ("Python Fundamentals", "Mutable vs Immutable Types"),
    "itertools": ("Iterators and Generators", "itertools and functools"),
    "json_module": ("Modules & Packaging", "Imports & Module System"),
    "lambda_functions": ("Functions and Scope", "Lambda & Higher Order Functions"),
    "legb_scope": ("Functions and Scope", "Scope & Namespaces (LEGB rule)"),
    "list_mutation_iteration": ("Data Structures", "Lists & Tuples"),
    "list_vs_tuple": ("Data Structures", "Lists & Tuples"),
    "loop_variable_leak": ("Python Fundamentals", "Control Flow (loops, conditionals)"),
    "memory_management": ("Memory & Performance", "Memory Management & Garbage Collections"),
    "mocking": ("Testing & Debugging", "unittest/ pytest Basics"),
    "mutability": ("Python Fundamentals", "Mutable vs Immutable Types"),
    "mutable_default_args": ("Memory & Performance", "Mutable Default Arguments"),
    "mutating_immutable": ("Python Fundamentals", "Mutable vs Immutable Types"),
    "nan_reflexivity": ("Python for Data/ML", "NumPy Array Internals & Broadcasting"),
    "property_decorators": ("OOP", "Class Methods, Static methods, Properties"),
    "pytest": ("Testing & Debugging", "unittest/ pytest Basics"),
    "python_execution_model": ("Modules & Packaging", "Imports & Module System"),
    "python_features": ("Python Fundamentals", "Variables and datatypes"),
    "reference_counting": ("Memory & Performance", "Memory Management & Garbage Collections"),
    "regex": ("Python Fundamentals", "Strings and String Formatting"),
    "slots": ("OOP", "Classes & Objects"),
    "slots_memory": ("Memory & Performance", "Memory Management & Garbage Collections"),
    "sort_stability": ("Data Structures", "Lists & Tuples"),
    "string_concat_performance": ("Python Fundamentals", "Strings and String Formatting"),
    "type_hints": ("Testing & Debugging", "Type hints & mypy"),
    "venv_deps": ("Modules & Packaging", "Virtual Environment & pip"),
    "weakref": ("Memory & Performance", "Memory Management & Garbage Collections"),
    "yield_from": ("Iterators and Generators", "Generator and yield"),
}


def main():
    db = SessionLocal()
    try:
        updated = 0
        for topic, (ch_name, st_name) in MAPPING.items():
            ch = db.query(Chapter).filter_by(name=ch_name).first()
            st = db.query(Subtopic).filter_by(name=st_name, chapter_id=ch.id).first() if ch else None
            if not ch or not st:
                print(f"SKIP {topic}: {ch_name}/{st_name} not found")
                continue
            n = (
                db.query(Question)
                .filter(Question.topic == topic, Question.chapter_id.is_(None))
                .update({"chapter_id": ch.id, "subtopic_id": st.id})
            )
            updated += n
        db.commit()
        print(f"Updated {updated} questions")

        remaining = (
            db.query(Question.topic, Question.id)
            .filter(Question.chapter_id.is_(None), Question.parent_question_id.is_(None))
            .all()
        )
        if remaining:
            leftover_topics = sorted({t for t, _ in remaining})
            print(f"Still NULL chapter_id: {len(remaining)} rows across topics: {leftover_topics}")
    finally:
        db.close()


if __name__ == "__main__":
    main()