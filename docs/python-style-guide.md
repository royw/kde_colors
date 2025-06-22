# Python Style Guide

## Type Annotations

When writing Python code in this project, always follow the **Magic Spell for Modern Type Annotations**:

> "Use Python 3.10+ style type annotations: lowercase generics (list[str], dict[str, int]), pipe operator for unions (str | None), and minimize typing imports."

### Guidelines

1. **Use lowercase collection types:**
   ```python
   # ✅ Correct - Modern (Python 3.9+)
   def get_items() -> list[str]:
       ...

   # ❌ Incorrect - Old style
   from typing import List
   def get_items() -> List[str]:
       ...
   ```

2. **Use the pipe operator for unions:**
   ```python
   # ✅ Correct - Modern (Python 3.10+)
   def find_user(id: int) -> User | None:
       ...

   # ❌ Incorrect - Old style
   from typing import Optional
   def find_user(id: int) -> Optional[User]:
       ...
   ```

3. **Only import from typing what's absolutely necessary:**
   - Only import Protocol, TypeVar, TypeAlias, and other special types
   - Don't import collection types like Dict, List, etc.

4. **Use type aliases with proper annotation:**
   ```python
   from typing import TypeAlias

   PathLike: TypeAlias = str | Path
   ```

5. **Use collections.abc for abstract containers** when appropriate

These standards are mandatory for all Python code in this project. They ensure consistency and take advantage of the modern Python type system.
