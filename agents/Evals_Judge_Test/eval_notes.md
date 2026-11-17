# AI EVAL - LLM undeterministic response evaluation through unit test case to know is it behaving like the way it is apart from false positive
- LLM generates good answere but not exactly in same sentence that can not be tested by comparing response with expected as they are done for deterministic way .

- The LLM response dependent on factors which changes based on factors

    - System Promt : is system prompt is correct

    - switch the model

    - chunk size

    - Number of retrieval

    - temperature

    - add tool/remove

    - RAG top-k, Threshold : Where vectorDB retrived right chunks, top-k results are correct, similarity search mapped

    ## How to accomplish through unit test
    ```
    Input           : what is the return policy
    Expected        : Must mention 30 days return window
    Actual response : you may return product within 30 days
    ```
    
    **1. test Input**

    **2. Expected Behavior** what should be mentioned 

        - proper Tool calling

        - RAG - is correct document is retrieved

        - is correct json schema is returned in response

    **3. Evaluation Mechanism**
        - match `expected intent` with `actual response`

## Evaluation based on some parameters :
- Deterministic response    : code to test if answere is binary or classification) because response is deterministic 
- UnDeterministic response  : LLM as judge

# Evaluation / Golden Dataset : 
- `Set of Question/Answeres/Tools/ Tool arguments` on which LLM application is evaluated covering edge cases, if model is changed, tok-k to know which reponse is better for same set of dataset
- `out scope`

- `edge cases`

-  `Adverse Question`  : like chnaging the system propmts, prompt injection

    - For AI Agent 
        - Question    
            -- what is return perios

            -- can I exchange damage shoes

            -- how long does refund take

            -- can i return without original package

        - Expected Tool

        - Expected Argument

        - Expected Answere

    - For RAG
        - Questions

        - expected top -k retrieved

        - expected LLM aanswer

    - for structure output

        - question

        - expected json schema

# Deterministic Evaluation:

Through code like 

- Type instance checking - checking the structure schema of the retuned response through LLM 

    - is json valid?

    - is semantics correct?

- Tool name returned by LLM or that is being called

- For RAG case cases where top-k should be zero.

# Non - Deterministic evaluation

`using Judge Element to return structured output` to evalute results given by LLM
- Pointwise : at one time one one prompt is tested/evaulated by judge on 5 evalution quality parameters mentioned below
- Pairwise  : give 2 different prompts with same context but diffent wordings to know which prompt RESPONSE has better evaluation score by Judge LLM

`rubrics`- Rules to score from 1-5 (1 being lowest, 5 being excellent)

eg
- faithfulness metric measured through rules
    - Rule 1- The answere sunstantially contractics or ignores the context
    - Rule 2- large portions of the answere are unsupported
    - Rule 3- The main ansere is supported but there are meanigful un supported claims
    - Rule 4- Amost all claims are supported with inly a minor unsupported deatil that does not effect the answere
    - Rule 5- whether every factual claim in the answere is supported by the provided contect 

```
Base on AI Quality matrix

1. Relevance
2. Correctness
3. faithfulness
4  Helpfulness
5  Halucination

LLM Judge returned (5 being high rating (excellent) and 1 being low)
{
    relevance: 5,
    correctness: 5,
    faithfulness: 4,
    helfulness: 4,
    halucination: 1

}

ask judge LLM to judge one by one factors to avoid to much rule contect to go in if want all metrices to be covered in one go
```

`1. Relevance score high/low (1-5)` :    Did the LLM responded to user query (Answer yes/no) and return relevence score , high/ low (1-5)

`2. Correctness Score :` related it with source of truth "Golden dataset"

eg 

Q : what is the return policy?
LLM responded : Company is founded in 2019, we sell clothers, shoes etc

Over here: 

    - correctness is high   : as the information is correct about company

    - relevance is low      : as the  information is not related to expected answere

`3. faithfulness:`

if the Return Policy is : user can return till 30 days

user asked              : can I return product if I have purchased item 20 days ago

LLM responsded:         : Product can be returned till 30 days.
                        (and added by itself as it was not in the provided context) Refund is usually procesed within 24 hours

over here
    - relevence score is high
    
    - correctness score is high

    - faithfulness score is LOW as it added the 24 hours information by itself



`4  Helpfulness:`

- query     : can I return damaged shoes
  Response  : yes
  over here
    - relevence score is high as response was related to query
    
    - correctness score is high as its a right response

    - faithfulness score is high as it did not added by itself


`5  Halucination:` generate information that does not exist / Fabricated response / unsupported by facts, 

-if the Return Policy RAG context is : 

    - user can return till 30 days

    - if the user is non-prime user then 10% deduction is made on return

- prime user ask question   : can I return item after 20 days?
- LLM response              : yes you can but 10% will be deducted

The response is not correct, relevent and faithful but LLM was not able to understand the context correctly and conveyed wrong information that is not true

# 



    






    



   
