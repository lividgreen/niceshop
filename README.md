# Shopping Agents Implementation Comparison

The purpose of this project is to demonstrate difference between frameworks' concepts.

## Installation

Just use [uv](https://github.com/astral-sh/uv):

```shell
uv venv
uv sync 
```

## Run

Run and select agent implementation from the list:

```shell
python main.py
```

or provide agent implementation name explicitly:

```shell
python main.py --agent-impl=LangChain
```

## Considerations

Despite the naive implementation we want to cover real-world requirements to agents, such as:
 
- asynchronous calls
- strict schemas of the tool calls parameters and response

Every agent implementation should follow the same high-level workflow:

1. Provide information about items in the catalog
2. Provide and update contents of the shopping basket

## Base Application

The application is an HTTP server implemented using [AIOHTTP](https://docs.aiohttp.org/en/stable/index.html).

Routes:
 * `GET /` - home page (not a fancy one, sorry) 
 * `POST /api/auth` - creates new session and returns its identifier
 * `POST /api/chat` - sends a message to a LLM agent in the request body and retrieves its response in response body 
 * `GET  /api/checkout` - returns a message "You are going to purchase: <cart contents>"

## Agents

Agent implementations should use `src.agents.BaseAgent` as a base class.

Current implementations:

- LangChain
- LlamaIndex
- PydanticAI

Planned:

- Atomic Agents (?)
- Others (?)



