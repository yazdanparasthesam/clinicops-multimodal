from .providers import MockChatModel, get_provider
from ...config import settings
import time

def self_criticism_loop(initial_prompt: str, provider=None, max_loops: int=None) -> str:
    provider = provider or get_provider()
    max_loops = max_loops if max_loops is not None else settings.ai_max_critique_loops
    # bounded loop
    draft = provider.invoke(initial_prompt)
    for i in range(max_loops):
        critique = provider.invoke(f"critique: {draft}")
        # deterministic stub: if critique says add precision, we revise once
        if "add" in critique.lower() or "precision" in critique.lower():
            draft = provider.invoke(f"revise ({i+1}): {draft} | critique: {critique}")
        else:
            break
    return draft

def react_agent(query: str, tools_registry: dict, provider=None, max_steps: int=4) -> str:
    provider = provider or get_provider()
    # simplified: collect tool outputs deterministically
    context = []
    for name, fn in list(tools_registry.items())[:max_steps]:
        try:
            context.append(f"{name}: {fn()}")
        except Exception as e:
            context.append(f"{name}: error {e}")
    prompt = f"ReAct query: {query} | tools: {' | '.join(context)}"
    return provider.invoke(prompt)

def rewoo_agent(plan_prompt: str, tools_registry: dict, provider=None, max_steps: int=8) -> str:
    provider = provider or get_provider()
    # Plan stub: 3 known tools
    plan = ["get_scores","get_validations","get_visit"]
    executed = []
    for name in plan[:max_steps]:
        if name in tools_registry:
            executed.append(f"{name}={tools_registry[name]()}")
        else:
            continue  # drop unknown
    prompt = f"ReWOO plan: {plan_prompt} | executed ({len(executed)}): {'; '.join(executed)}"
    return provider.invoke(prompt)
