import inspect
from typing import Any, Dict


async def call_maybe_async(method, **kwargs):
    """
    Calls a method that may be either async or sync.

    Why we need this:
    - Some agents use async methods because they call Ollama.
    - Some agents use normal synchronous methods.
    - The orchestrator should work with both.
    """

    result = method(**kwargs)

    if inspect.isawaitable(result):
        return await result

    return result


async def call_architect_agent(
    agent: Any,
    run_id: str,
    srs_version: str,
    domain_version: str,
    architecture_version: str,
) -> Dict[str, Any]:
    """
    Calls the Architect Agent using a flexible method lookup.

    Supported Architect Agent method names:
    - generate_architecture_pack
    - generate_architecture
    - generate_sds
    - run
    """

    candidate_methods = [
        "generate_architecture_pack",
        "generate_architecture",
        "generate_sds",
        "run",
    ]

    for method_name in candidate_methods:
        if hasattr(agent, method_name):
            method = getattr(agent, method_name)

            return await call_maybe_async(
                method,
                run_id=run_id,
                srs_version=srs_version,
                domain_version=domain_version,
                architecture_version=architecture_version,
            )

    raise AttributeError(
        "ArchitectAgent does not have a supported generation method. "
        "Expected one of: generate_architecture_pack, generate_architecture, generate_sds, run."
    )


async def call_uiux_full_workflow(
    agent: Any,
    run_id: str,
    srs_version: str,
    domain_version: str,
    architecture_version: str,
    uiux_version: str,
    include_admin: bool = True,
    render_images: bool = True,
    fail_fast: bool = False,
    skip_existing: bool = True,
    max_screens: int | None = None,
    user_prompt: str | None = None,
) -> Dict[str, Any]:
    """
    Runs the UI/UX Agent full split workflow.

    The UI/UX Agent was previously developed as three stable steps:
    1. validate_approved_inputs()
    2. generate_plan()
    3. generate_all_wireframes()
    4. finalize_design_pack()

    The orchestrator now calls these steps in the correct order.
    """

    if not hasattr(agent, "validate_approved_inputs"):
        raise AttributeError("UIUXAgent is missing validate_approved_inputs().")

    if not hasattr(agent, "generate_plan"):
        raise AttributeError("UIUXAgent is missing generate_plan().")

    if not hasattr(agent, "generate_all_wireframes"):
        raise AttributeError("UIUXAgent is missing generate_all_wireframes().")

    if not hasattr(agent, "finalize_design_pack"):
        raise AttributeError("UIUXAgent is missing finalize_design_pack().")

    validation_result = await call_maybe_async(
        agent.validate_approved_inputs,
        run_id=run_id,
        srs_version=srs_version,
        domain_version=domain_version,
        architecture_version=architecture_version,
    )

    plan_result = await call_maybe_async(
        agent.generate_plan,
        run_id=run_id,
        srs_version=srs_version,
        domain_version=domain_version,
        architecture_version=architecture_version,
        uiux_version=uiux_version,
        include_admin=include_admin,
        render_images=render_images,
        user_prompt=user_prompt,
    )

    wireframe_result = await call_maybe_async(
        agent.generate_all_wireframes,
        run_id=run_id,
        srs_version=srs_version,
        domain_version=domain_version,
        architecture_version=architecture_version,
        uiux_version=uiux_version,
        render_images=render_images,
        user_prompt=user_prompt,
        fail_fast=fail_fast,
        skip_existing=skip_existing,
        max_screens=max_screens,
    )

    finalize_result = await call_maybe_async(
        agent.finalize_design_pack,
        run_id=run_id,
        srs_version=srs_version,
        domain_version=domain_version,
        architecture_version=architecture_version,
        uiux_version=uiux_version,
    )

    return {
        "validation_result": validation_result,
        "plan_result": plan_result,
        "wireframe_result": wireframe_result,
        "finalize_result": finalize_result,
    }


async def call_uiux_revision(
    agent: Any,
    run_id: str,
    current_version: str,
    new_version: str,
    change_request: str,
    srs_version: str,
    domain_version: str,
    architecture_version: str,
    include_admin: bool = True,
    render_images: bool = True,
    fail_fast: bool = False,
    skip_existing: bool = True,
    max_screens: int | None = None,
) -> Dict[str, Any]:
    """
    Calls UI/UX revision workflow.

    This is used when the human rejects the UI/UX output and requests changes.
    """

    if not hasattr(agent, "revise_design_pack"):
        raise AttributeError("UIUXAgent is missing revise_design_pack().")

    return await call_maybe_async(
        agent.revise_design_pack,
        run_id=run_id,
        current_version=current_version,
        new_version=new_version,
        change_request=change_request,
        srs_version=srs_version,
        domain_version=domain_version,
        architecture_version=architecture_version,
        include_admin=include_admin,
        render_images=render_images,
        fail_fast=fail_fast,
        skip_existing=skip_existing,
        max_screens=max_screens,
    )