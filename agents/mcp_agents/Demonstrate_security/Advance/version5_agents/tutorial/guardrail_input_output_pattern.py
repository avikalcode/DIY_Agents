# Here is a complete, runnable Python example showing 
# how a simple class (Abc) with a (titu) method uses the 
# (_Args) guardrail pattern to validate a 
#  (game_name) string before running.
from typing import Annotated, Any
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)

# --- 1. Field-level Before & After Validators ---

# BEFORE: Clean messy raw input before Pydantic checks the type
def strip_spaces_before(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value

def clean_number_string_before(value: Any) -> Any:
    # Converts strings like " 85 pts " or "85" into "85" before int parsing
    if isinstance(value, str):
        return value.replace("pts", "").strip()
    return value

# AFTER: Check business rules once types are guaranteed
def block_banned_games_after(value: str) -> str:
    # Guaranteed to be a clean str here
    if value.lower() == "banned_game":
        raise ValueError("This game is not allowed")
    return value


def clean_game_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Game name cannot be empty or just spaces")
    return cleaned

# 1. -----------Custom GameName type ----------------
GameName = Annotated[
    str,
    BeforeValidator(strip_spaces_before),     # Step 1: Trim spaces on raw input
    Field(min_length=1, max_length=50),       # Step 2: Check str type & length
    AfterValidator(block_banned_games_after), # Step 3: Custom rule on clean str
]

# 2.------------------ Custom Score type: must be an int and strictly less than 100 (< 100)
# Score = Annotated[StrictInt, Field(lt=100)]
Score = Annotated[
    int,
    BeforeValidator(clean_number_string_before), # Step 1: Clean raw input like "85 pts"
    Field(ge=0, lt=100),                         # Step 2: Parse int & enforce 0 <= score < 100
]


# 3. -------------Strict Argument
class _Args(BaseModel):
    model_config = ConfigDict(extra="forbid")  # rejects unknown arguments


# 2 required field :TituArgs expects both game_name and score. Leaving either one out triggers a Field required error.
# Automatic Type Validation: score: int verifies that the value is an integer (and automatically parses clean numeric strings like "200" into 200, unless use StrictInt).
class TituArgs(_Args):
    game_name: GameName
    # score: int  # Added second required argument of type int ( score to be optional with a default of 0, you would write score: int = 0)
    score: Score

    # MODEL BEFORE: Runs on the raw dictionary before any field is validated
    @model_validator(mode="before")
    @classmethod
    def check_raw_dict_before(cls, data: Any) -> Any:
        if isinstance(data, dict) and "game" in data and "game_name" not in data:
            # Example: normalize an old key name "game" -> "game_name"
            data = dict(data)
            data["game_name"] = data.pop("game")
        return data

    # MODEL AFTER: Runs after BOTH game_name and score are valid
    @model_validator(mode="after")
    def check_both_fields_after(self) -> "TituArgs":
        # Cross-field rule: Chess max score in this app is 50
        if self.game_name.lower() == "chess" and self.score > 50:
            raise ValueError("Score for Chess cannot exceed 50")
        return self

# 3. -------------------Class Abc with method titu
class Abc:
    
    def titu(self, **raw_args) -> str:
        
        try:
        
            # Validate incoming arguments against TituArgs
            valid = TituArgs.model_validate(raw_args) # ==========> Over here it validates
        
        except ValidationError as exc:
            # Join all validation error messages cleanly
            
            # reason = exc.errors(include_input=False)[0]["msg"]
            reasons = "; ".join(
                f"{err['loc'][0]}: {err['msg']}"
                for err in exc.errors(include_input=False)
            )
             
            return f"Rejected: {reasons}"

        # Runs only when game_name is valid
        return f"Game: {valid.game_name} | Score: {valid.score}"

# --- Testing Abc.titu ---
app = Abc()

# 1. Valid call with both arguments
print("1.", app.titu(game_name="  Minecraft  ", score=150))

# 2. Valid call with numeric string (Pydantic converts "200" to int 200)
print("2.", app.titu(game_name="Chess", score="200"))

# 3. Invalid: score is not a valid integer
print("3.", app.titu(game_name="Chess", score="high"))

# 4. Invalid: missing score
print("4.", app.titu(game_name="Chess"))

# 5. Invalid: extra unknown argument passed
print("5.", app.titu(game_name="Chess", score=100, level=5))

# Expected output
# 1. Game: Minecraft | Score: 150
# 2. Game: Chess | Score: 200
# 3. Rejected -> score: Input should be a valid integer, unable to parse string as an integer
# 4. Rejected -> score: Field required
# 5. Rejected -> level: Extra inputs are not permitted