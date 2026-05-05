from agents.uiux_agent.schemas import UserFlow, FlowNode, FlowEdge, UIScreen


def _slugify(text: str) -> str:
    """
    Converts a screen name into a safe route/file name.

    Example:
    "Product Details" -> "product_details"
    """
    return (
        text.lower()
        .replace("/", " ")
        .replace("&", "and")
        .replace("-", " ")
        .replace("{", "")
        .replace("}", "")
        .replace("_", " ")
        .strip()
        .replace("  ", " ")
        .replace(" ", "_")
    )


def _contains_any(text: str | None, keywords: list[str]) -> bool:
    """
    Checks whether text contains any keyword.
    """
    if not text:
        return False

    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)


def _requirement_text(fr: dict) -> str:
    """
    Creates searchable text from one functional requirement.
    """
    return f"{fr.get('title', '')} {fr.get('description', '')}".lower()


def _extract_api_operations(api_contract: dict) -> list[dict]:
    """
    Extracts useful API operation information from an OpenAPI document.

    Output example:
    {
        "method": "GET",
        "path": "/products",
        "tag": "Catalog",
        "summary": "List products"
    }
    """
    operations = []

    paths = api_contract.get("paths", {})

    for path, path_data in paths.items():
        if not isinstance(path_data, dict):
            continue

        for method, operation in path_data.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue

            if not isinstance(operation, dict):
                continue

            tags = operation.get("tags", [])
            tag = tags[0] if tags else "General"

            operations.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "tag": tag,
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                }
            )

    return operations


def _match_requirements(frs: list[dict], keywords: list[str]) -> list[str]:
    """
    Matches requirements to a screen using keyword matching.
    """
    matched = []

    for fr in frs:
        text = _requirement_text(fr)

        if any(keyword.lower() in text for keyword in keywords):
            fr_id = fr.get("id")
            if fr_id:
                matched.append(fr_id)

    return matched


def _derive_screen_name_from_api(operation: dict) -> str:
    """
    Converts an API operation into a UI-friendly screen name.

    Examples:
    GET /products -> Product List
    GET /products/{product_id} -> Product Details
    POST /checkout -> Checkout
    GET /orders -> Order List
    POST /admin/products -> Admin Product Create
    """
    method = operation["method"]
    path = operation["path"].lower()
    tag = operation["tag"]

    if "auth" in path or "login" in path or "register" in path:
        return "Account Access"

    if path == "/products" and method == "GET":
        return "Product Catalog"

    if "/products/" in path and method == "GET":
        return "Product Details"

    if "cart" in path:
        return "Shopping Cart"

    if "checkout" in path:
        return "Checkout"

    if path == "/orders" and method == "POST":
        return "Order Placement"

    if path == "/orders" and method == "GET":
        return "Order History"

    if "admin" in path:
        return f"Admin {tag}"

    clean_tag = tag.replace("_", " ").replace("-", " ").title()
    clean_path = path.strip("/").replace("/", " ").replace("{", "").replace("}", "").title()

    if clean_path:
        return f"{clean_tag} {clean_path}"

    return clean_tag or "Generated Screen"


def _derive_route_from_screen_name(name: str) -> str:
    """
    Creates a frontend route from the screen name.
    """
    slug = _slugify(name).replace("_", "-")
    return f"/{slug}"


def _screen_already_exists(screens: list[UIScreen], name: str) -> bool:
    """
    Prevents duplicate screens.
    """
    normalized = name.lower().strip()

    return any(screen.name.lower().strip() == normalized for screen in screens)


def _add_screen(
    screens: list[UIScreen],
    name: str,
    description: str,
    route: str,
    related_requirements: list[str],
) -> UIScreen:
    """
    Adds a screen with automatic UI-SCR-XX ID.
    """
    screen_number = len(screens) + 1
    screen_id = f"UI-SCR-{screen_number:02d}"
    slug = _slugify(name)

    screen = UIScreen(
        id=screen_id,
        name=name,
        file_name=f"{screen_id}_{slug}.html",
        description=description,
        route=route,
        related_requirements=related_requirements,
    )

    screens.append(screen)

    return screen


def build_default_screens(
    srs: dict,
    api_contract: dict,
    include_admin: bool = True,
    change_request: str | None = None,
) -> list[UIScreen]:
    """
    Automatically builds UI screens from approved SRS + approved API contract.

    No fixed UI-SCR-01 Login / UI-SCR-02 Catalog list is used here.
    Screens are discovered from:
    - OpenAPI paths
    - OpenAPI tags
    - SRS functional requirements
    - optional change request
    """

    frs = srs.get("functional_requirements", [])
    operations = _extract_api_operations(api_contract)

    screens: list[UIScreen] = []

    # ---------------------------------------------------------
    # 1. Create screens from API operations
    # ---------------------------------------------------------
    for operation in operations:
        path = operation["path"].lower()

        if not include_admin and "admin" in path:
            continue

        screen_name = _derive_screen_name_from_api(operation)

        if _screen_already_exists(screens, screen_name):
            continue

        searchable_text = (
            f"{operation.get('tag', '')} "
            f"{operation.get('summary', '')} "
            f"{operation.get('description', '')} "
            f"{operation.get('path', '')}"
        ).lower()

        keywords = searchable_text.replace("/", " ").replace("{", " ").replace("}", " ").split()

        related_requirements = _match_requirements(frs, keywords)

        _add_screen(
            screens=screens,
            name=screen_name,
            description=(
                f"Auto-generated UI screen based on API operation "
                f"{operation['method']} {operation['path']}."
            ),
            route=_derive_route_from_screen_name(screen_name),
            related_requirements=related_requirements,
        )

    # ---------------------------------------------------------
    # 2. Create screens from SRS requirements not covered by API
    # ---------------------------------------------------------
    covered_frs = set()

    for screen in screens:
        covered_frs.update(screen.related_requirements)

    for fr in frs:
        fr_id = fr.get("id")
        title = fr.get("title", "").strip()
        description = fr.get("description", "").strip()

        if not fr_id:
            continue

        if fr_id in covered_frs:
            continue

        screen_name = title or f"Requirement {fr_id}"

        if _screen_already_exists(screens, screen_name):
            continue

        _add_screen(
            screens=screens,
            name=screen_name,
            description=description or f"Auto-generated UI screen for requirement {fr_id}.",
            route=_derive_route_from_screen_name(screen_name),
            related_requirements=[fr_id],
        )

    # ---------------------------------------------------------
    # 3. Create screens from user change request
    # ---------------------------------------------------------
    if _contains_any(change_request, ["wishlist", "save for later"]):
        if not _screen_already_exists(screens, "Wishlist"):
            _add_screen(
                screens=screens,
                name="Wishlist",
                description="Auto-generated wishlist screen requested by user refinement.",
                route="/wishlist",
                related_requirements=_match_requirements(frs, ["wishlist", "save", "product"]),
            )

    if _contains_any(change_request, ["payment failed", "failed payment", "payment error", "checkout error", "error state"]):
        if not _screen_already_exists(screens, "Checkout Error State"):
            _add_screen(
                screens=screens,
                name="Checkout Error State",
                description="Auto-generated checkout error state requested by user refinement.",
                route="/checkout-error",
                related_requirements=_match_requirements(frs, ["checkout", "payment", "error"]),
            )

    if _contains_any(change_request, ["return", "refund"]):
        if not _screen_already_exists(screens, "Returns And Refunds"):
            _add_screen(
                screens=screens,
                name="Returns And Refunds",
                description="Auto-generated returns/refunds screen requested by user refinement.",
                route="/returns-and-refunds",
                related_requirements=_match_requirements(frs, ["return", "refund", "order"]),
            )

    # ---------------------------------------------------------
    # 4. Safety fallback
    # ---------------------------------------------------------
    if not screens:
        _add_screen(
            screens=screens,
            name="Generated E-commerce Home",
            description="Fallback UI screen generated because SRS/API did not provide enough UI details.",
            route="/",
            related_requirements=[],
        )

    return screens


def _screen_score(screen: UIScreen, keywords: list[str]) -> int:
    """
    Scores how closely a screen matches a group of keywords.
    """
    text = f"{screen.name} {screen.description} {screen.route}".lower()

    return sum(1 for keyword in keywords if keyword.lower() in text)


def _find_best_screen(screens: list[UIScreen], keywords: list[str]) -> UIScreen | None:
    """
    Finds the best matching screen for a flow step.
    """
    best = None
    best_score = 0

    for screen in screens:
        score = _screen_score(screen, keywords)

        if score > best_score:
            best = screen
            best_score = score

    return best


def build_user_flow(
    screens: list[UIScreen],
    change_request: str | None = None,
) -> UserFlow:
    """
    Automatically builds user flow from generated screen inventory.

    It does not assume fixed screen IDs.
    It orders screens by purpose using screen name/description/route.
    """

    nodes: list[FlowNode] = [
        FlowNode(id="FLOW-N01", label="Start", screen_id=None),
    ]

    ordered_screens: list[UIScreen] = []

    preferred_order = [
        ["account", "login", "auth", "register"],
        ["catalog", "product catalog", "browse", "product list"],
        ["details", "product details"],
        ["wishlist", "save for later"],
        ["cart", "shopping cart"],
        ["checkout"],
        ["checkout error", "payment failed", "error state"],
        ["order placement", "place order"],
        ["confirmation", "order confirmation"],
        ["history", "orders"],
        ["return", "refund"],
        ["admin"],
    ]

    for keyword_group in preferred_order:
        screen = _find_best_screen(screens, keyword_group)

        if screen and screen not in ordered_screens:
            ordered_screens.append(screen)

    # Add custom screens that were not matched by preferred order.
    for screen in screens:
        if screen not in ordered_screens:
            ordered_screens.append(screen)

    for index, screen in enumerate(ordered_screens, start=2):
        nodes.append(
            FlowNode(
                id=f"FLOW-N{index:02d}",
                label=screen.name,
                screen_id=screen.id,
                related_requirements=screen.related_requirements,
            )
        )

    edges: list[FlowEdge] = []

    if len(nodes) > 1:
        edges.append(
            FlowEdge(
                from_node="FLOW-N01",
                to_node=nodes[1].id,
                condition="Start journey",
            )
        )

    for index in range(1, len(nodes) - 1):
        current_node = nodes[index]
        next_node = nodes[index + 1]

        if "admin" in next_node.label.lower():
            continue

        if "checkout error" in next_node.label.lower():
            continue

        edges.append(
            FlowEdge(
                from_node=current_node.id,
                to_node=next_node.id,
                condition="Next step",
            )
        )

    checkout_node = None
    error_node = None

    for node in nodes:
        if "checkout" in node.label.lower() and "error" not in node.label.lower():
            checkout_node = node

        if "checkout error" in node.label.lower() or "payment failed" in node.label.lower():
            error_node = node

    if checkout_node and error_node:
        edges.append(
            FlowEdge(
                from_node=checkout_node.id,
                to_node=error_node.id,
                condition="Payment or validation failed",
            )
        )
        edges.append(
            FlowEdge(
                from_node=error_node.id,
                to_node=checkout_node.id,
                condition="Retry checkout",
            )
        )

    return UserFlow(
        id="UF-001",
        name="Auto-generated UI Flow",
        actor="Customer",
        nodes=nodes,
        edges=edges,
    )


def build_mermaid_from_flow(flow: UserFlow) -> str:
    """
    Converts structured UserFlow into Mermaid syntax.
    """
    lines = ["flowchart TD"]

    for node in flow.nodes:
        label = node.label

        if node.screen_id:
            label = f"{node.screen_id} {node.label}"

        safe_label = label.replace('"', "'")

        if node.id == "FLOW-N01":
            lines.append(f'    {node.id}(["{safe_label}"])')
        else:
            lines.append(f'    {node.id}["{safe_label}"]')

    lines.append("")

    for edge in flow.edges:
        if edge.condition:
            condition = edge.condition.replace('"', "'")
            lines.append(f'    {edge.from_node} -->|"{condition}"| {edge.to_node}')
        else:
            lines.append(f"    {edge.from_node} --> {edge.to_node}")

    return "\n".join(lines)