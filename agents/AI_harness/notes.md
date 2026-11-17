# Evaluation of AI application dynamically in loop till it give correction response and no hallicunation

```
CLIENT  ->   SERVER      ->  LLM     ->  EVALUATOR
        <-      |             |      <-     |
                |             |     Loop    |
                |             |             |
                |             V             |
                |           Tools           |
                |__________________________ |
                        final response
```

# AI Harness (loop) : Stages in loop
```
            =====  Plan =====
            ^                 |
            |                 v
        Decide              Act 
            ^                 |
            |                 v
            <---  Observe <----

```
- Plan

- Act

- Observe

- Decide

## Plan
LLM decide what steps has to be perform
1. system prompt

2. user prompt

3. tools

## Action 
1. get tools version 1.0

2. Eval/Guardrails

## Observation (Evaluator)
Observe response from tools, or llm

- sucessful

- error response

- validations

##
- is enough information, or any more tools to call

- agent decides what to do next  

```
Generated output -> application validator -> valid -> yes-> complete
                            |                  |
                            |                  v
                            |                   No
                            |                   |
                            |                   v
                            |                 Validation feed back ( add context to prompt to get correct response)
                            |                   |
                            |                   v
                            |               Generate correct output
                            |__________________ |

```

# adding context management (add memory, checkpoints)
- conversation history : to - fro communication history adding to the context

- task state : 

- model context : final context provide to LLM after evaluation in loop, take inputs from `convesation history` along with `task state` or only 1 according to requirement

## Task State (checkpoints)
Store in database to be given to llm in structure
```
{
    "taskid"            : 
    "version"           :
    "status"            : "in progress"
    "current step"      : "Revising"
    "completed taskid"  : [
                            "task1"
                            "task2" 
    ]
    "attempts"          : 1
    " validationPased " : false
    " missing task "    : ["task4"]

}
```

```store checkpoint
chkont 1- fetch tickets using tools 
chkpnt2 - generated 1st draft
.....
```

## Context compaction : provide revelent information (summrize context without missing information)
Task:
Prepare release notes for version 2

Required task:
prj1, prj2, prj3

current result:
..........

validator error:
prj2 is missing

instruction:
correct the dfart without omitting any required ticket

# execution control
contol the number of attempts to perform AI harness loop

instruction retry

timeouts

# Human in the loop