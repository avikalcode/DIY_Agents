from typing import Annotated
from pydantic import Field, StringConstraints

Title = Annotated[str, StringConstraints(
    strip_whitespace=True, min_length=1, max_length=100,
    pattern=r"^[^\x00-\x1f\x7f]+$",
)]
TodoId = Annotated[int, Field(ge=1, le=1_000_000)]