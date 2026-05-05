from agents.uiux_agent.schemas import UIScreen


def _contains_any(text: str | None, keywords: list[str]) -> bool:
    """
    Checks whether text contains any keyword.
    """
    if not text:
        return False

    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)


def _screen_text(screen: UIScreen) -> str:
    """
    Combines screen metadata into searchable text.
    """
    return f"{screen.name} {screen.description} {screen.route}".lower()


def _infer_screen_purpose(screen: UIScreen) -> str:
    """
    Infers the purpose of a screen from its generated metadata.

    This does not depend on fixed UI-SCR IDs.
    """
    text = _screen_text(screen)

    if _contains_any(text, ["login", "account", "auth", "register"]):
        return "form"

    if _contains_any(text, ["catalog", "browse", "products", "product list"]):
        return "grid"

    if _contains_any(text, ["details", "detail"]):
        return "detail"

    if _contains_any(text, ["cart", "basket"]):
        return "cart"

    if _contains_any(text, ["checkout", "payment", "shipping"]):
        return "checkout"

    if _contains_any(text, ["confirmation", "success"]):
        return "success"

    if _contains_any(text, ["history", "orders", "list"]):
        return "list"

    if _contains_any(text, ["admin", "manage"]):
        return "table"

    if _contains_any(text, ["error", "failed"]):
        return "error"

    if _contains_any(text, ["wishlist", "save for later"]):
        return "grid"

    if _contains_any(text, ["return", "refund"]):
        return "form"

    return "generic"


def _page_shell(project_name: str, screen: UIScreen, body: str, related: str) -> str:
    """
    Common page shell used by all dynamically generated wireframes.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen.id} - {screen.name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 text-slate-900">
    <main class="max-w-7xl mx-auto p-8">
        <header class="mb-8 flex justify-between items-start">
            <div>
                <p class="text-sm text-slate-500">{project_name}</p>
                <h1 class="text-4xl font-bold">{screen.id} — {screen.name}</h1>
                <p class="text-slate-600 mt-2">{screen.description}</p>
            </div>
            <div class="text-sm bg-slate-200 rounded-full px-4 py-2">{screen.route}</div>
        </header>

        {body}

        <footer class="mt-10 text-xs text-slate-500">
            Related requirements: {related}
        </footer>
    </main>
</body>
</html>"""


def _top_nav_block() -> str:
    """
    Reusable navigation block.
    """
    return """
    <div class="bg-white rounded-2xl border p-5 shadow-sm mb-6 flex justify-between items-center">
        <div class="flex gap-3">
            <div class="h-11 w-72 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Search / input</div>
            <div class="h-11 w-40 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Filter</div>
        </div>
        <div class="flex gap-3">
            <div class="h-11 w-24 rounded-lg border bg-slate-50 flex items-center justify-center text-sm">Action</div>
            <div class="h-11 w-24 rounded-lg bg-slate-900 text-white flex items-center justify-center text-sm">Primary</div>
        </div>
    </div>
    """


def _form_body(screen: UIScreen) -> str:
    """
    Dynamic form-style wireframe.
    Used for login, account, returns, checkout forms, etc.
    """
    return f"""
    <section class="grid grid-cols-12 gap-6">
        <div class="col-span-7 bg-white rounded-2xl border shadow-sm p-8">
            <h2 class="text-2xl font-semibold mb-6">{screen.name} Form</h2>

            <div class="grid grid-cols-2 gap-5">
                <div>
                    <label class="block text-sm font-medium mb-2">Primary Field</label>
                    <div class="h-12 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Enter value</div>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Secondary Field</label>
                    <div class="h-12 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Enter value</div>
                </div>
                <div class="col-span-2">
                    <label class="block text-sm font-medium mb-2">Description / Notes</label>
                    <div class="h-32 rounded-lg border bg-slate-50 px-4 py-3 text-slate-400">Long text input area</div>
                </div>
            </div>

            <div class="mt-6 flex gap-3">
                <div class="h-12 px-6 rounded-lg bg-slate-900 text-white flex items-center justify-center">Submit</div>
                <div class="h-12 px-6 rounded-lg border bg-slate-50 flex items-center justify-center">Cancel</div>
            </div>
        </div>

        <aside class="col-span-5 bg-white rounded-2xl border shadow-sm p-8">
            <h3 class="text-xl font-semibold mb-4">Guidance</h3>
            <div class="space-y-3 text-sm text-slate-600">
                <p>• This panel explains what the user should do.</p>
                <p>• Validation messages appear near inputs.</p>
                <p>• Help text can be generated from SRS constraints.</p>
            </div>
        </aside>
    </section>
    """


def _grid_body(screen: UIScreen) -> str:
    """
    Dynamic grid-style wireframe.
    Used for catalog, wishlist, product grids, etc.
    """
    card = """
    <div class="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <div class="h-40 bg-slate-200"></div>
        <div class="p-4">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold">Item Title</h3>
                <span class="text-sm bg-slate-100 px-2 py-1 rounded">Price</span>
            </div>
            <p class="text-sm text-slate-500 mb-3">Short item description generated from feature context.</p>
            <div class="flex items-center justify-between">
                <span class="text-xs text-slate-400">Status / Rating</span>
                <div class="text-sm bg-slate-900 text-white px-3 py-2 rounded-lg">View</div>
            </div>
        </div>
    </div>
    """

    return f"""
    <section class="grid grid-cols-12 gap-6">
        <aside class="col-span-3 bg-white rounded-2xl border p-6 shadow-sm">
            <h2 class="text-xl font-semibold mb-4">Filters</h2>
            <div class="space-y-4">
                <div>
                    <p class="text-sm font-medium mb-2">Search</p>
                    <div class="h-11 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Search...</div>
                </div>
                <div>
                    <p class="text-sm font-medium mb-2">Category / Type</p>
                    <div class="space-y-2">
                        <div class="h-9 rounded border bg-slate-50 px-3 flex items-center text-sm">Option A</div>
                        <div class="h-9 rounded border bg-slate-50 px-3 flex items-center text-sm">Option B</div>
                        <div class="h-9 rounded border bg-slate-50 px-3 flex items-center text-sm">Option C</div>
                    </div>
                </div>
            </div>
        </aside>

        <section class="col-span-9">
            {_top_nav_block()}
            <div class="grid grid-cols-3 gap-5">
                {card}
                {card}
                {card}
                {card}
                {card}
                {card}
            </div>
        </section>
    </section>
    """


def _detail_body(screen: UIScreen) -> str:
    """
    Dynamic detail-page wireframe.
    """
    return f"""
    <section class="grid grid-cols-12 gap-8">
        <div class="col-span-5 bg-white rounded-2xl border shadow-sm p-6">
            <div class="h-[420px] bg-slate-200 rounded-xl mb-4 flex items-center justify-center text-slate-400">
                Main visual / preview area
            </div>
            <div class="grid grid-cols-4 gap-3">
                <div class="h-20 bg-slate-100 rounded-lg border"></div>
                <div class="h-20 bg-slate-100 rounded-lg border"></div>
                <div class="h-20 bg-slate-100 rounded-lg border"></div>
                <div class="h-20 bg-slate-100 rounded-lg border"></div>
            </div>
        </div>

        <div class="col-span-7 bg-white rounded-2xl border shadow-sm p-8">
            <span class="inline-block text-xs px-3 py-1 rounded-full bg-slate-100 text-slate-600 mb-4">Detail View</span>
            <h2 class="text-3xl font-bold mb-2">{screen.name}</h2>
            <p class="text-sm text-slate-500 mb-4">Supporting metadata / rating / status</p>
            <p class="text-2xl font-semibold mb-6">Primary value</p>

            <div class="space-y-3 mb-6 text-slate-600">
                <p>• Key information point one</p>
                <p>• Key information point two</p>
                <p>• Key information point three</p>
            </div>

            <div class="flex gap-3 mb-6">
                <div class="h-11 bg-slate-900 text-white rounded-lg px-6 flex items-center justify-center">Primary Action</div>
                <div class="h-11 bg-white border rounded-lg px-6 flex items-center justify-center">Secondary Action</div>
            </div>

            <div class="border-t pt-5">
                <h3 class="font-semibold mb-3">Details</h3>
                <div class="h-4 bg-slate-100 rounded mb-2"></div>
                <div class="h-4 bg-slate-100 rounded mb-2"></div>
                <div class="h-4 bg-slate-100 rounded w-4/5"></div>
            </div>
        </div>
    </section>
    """


def _cart_body(screen: UIScreen) -> str:
    """
    Dynamic cart/order-summary style wireframe.
    """
    row = """
    <div class="grid grid-cols-12 gap-4 items-center border-b pb-4">
        <div class="col-span-2 h-20 bg-slate-100 rounded-lg border"></div>
        <div class="col-span-4">
            <div class="h-5 bg-slate-200 rounded w-2/3 mb-2"></div>
            <div class="h-4 bg-slate-100 rounded w-1/2"></div>
        </div>
        <div class="col-span-2 text-center text-slate-600">Value</div>
        <div class="col-span-2">
            <div class="h-10 rounded-lg border bg-slate-50 flex items-center justify-center">Qty</div>
        </div>
        <div class="col-span-2 text-right text-slate-700">Remove</div>
    </div>
    """

    return f"""
    <section class="grid grid-cols-12 gap-6">
        <div class="col-span-8 bg-white rounded-2xl border shadow-sm p-6">
            <h2 class="text-2xl font-semibold mb-5">{screen.name}</h2>
            <div class="space-y-5">
                {row}
                {row}
                {row}
            </div>
        </div>

        <aside class="col-span-4 bg-white rounded-2xl border shadow-sm p-6">
            <h2 class="text-xl font-semibold mb-4">Summary</h2>
            <div class="space-y-3 text-sm text-slate-600">
                <div class="flex justify-between"><span>Subtotal</span><span>$149.97</span></div>
                <div class="flex justify-between"><span>Fees</span><span>$10.00</span></div>
                <div class="flex justify-between"><span>Tax</span><span>$12.00</span></div>
                <div class="flex justify-between font-semibold text-slate-900 pt-3 border-t"><span>Total</span><span>$171.97</span></div>
            </div>

            <div class="mt-6 h-12 rounded-lg bg-slate-900 text-white flex items-center justify-center font-medium">
                Continue
            </div>
        </aside>
    </section>
    """


def _checkout_body(screen: UIScreen, change_request: str | None) -> str:
    """
    Dynamic checkout/payment style wireframe.
    """
    error_block = ""
    if _contains_any(change_request, ["payment failed", "failed payment", "payment error", "checkout error", "error state"]):
        error_block = """
        <div class="mb-5 rounded-xl border border-red-300 bg-red-50 p-4 text-red-800">
            <p class="font-semibold">Error state</p>
            <p class="text-sm mt-1">Payment or validation issue appears here.</p>
        </div>
        """

    return f"""
    <section class="grid grid-cols-12 gap-6">
        <div class="col-span-8 bg-white rounded-2xl border shadow-sm p-6">
            <h2 class="text-2xl font-semibold mb-5">{screen.name}</h2>
            {error_block}

            <div class="grid grid-cols-2 gap-5">
                <div>
                    <h3 class="font-medium mb-3">User / Delivery Details</h3>
                    <div class="space-y-3">
                        <div class="h-11 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Full name</div>
                        <div class="h-11 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Email</div>
                        <div class="h-11 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Address</div>
                    </div>
                </div>

                <div>
                    <h3 class="font-medium mb-3">Payment / Confirmation Details</h3>
                    <div class="space-y-3">
                        <div class="h-11 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Payment method</div>
                        <div class="h-11 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Reference</div>
                        <div class="h-11 rounded-lg border bg-slate-50 px-4 flex items-center text-slate-400">Validation state</div>
                    </div>
                </div>
            </div>

            <div class="mt-6 h-12 rounded-lg bg-slate-900 text-white flex items-center justify-center font-medium">
                Confirm
            </div>
        </div>

        <aside class="col-span-4 bg-white rounded-2xl border shadow-sm p-6">
            <h2 class="text-xl font-semibold mb-4">Summary</h2>
            <div class="space-y-3 text-sm text-slate-600">
                <div class="flex justify-between"><span>Items</span><span>3</span></div>
                <div class="flex justify-between"><span>Subtotal</span><span>$149.97</span></div>
                <div class="flex justify-between"><span>Fees</span><span>$10.00</span></div>
                <div class="flex justify-between font-semibold text-slate-900 pt-3 border-t"><span>Total</span><span>$159.97</span></div>
            </div>
        </aside>
    </section>
    """


def _success_body(screen: UIScreen) -> str:
    """
    Dynamic success/confirmation wireframe.
    """
    return f"""
    <section class="max-w-3xl mx-auto bg-white rounded-2xl border shadow-sm p-10 text-center">
        <div class="mx-auto h-20 w-20 rounded-full bg-green-100 flex items-center justify-center text-green-700 text-3xl mb-6">
            ✓
        </div>
        <h2 class="text-3xl font-bold mb-3">{screen.name}</h2>
        <p class="text-slate-600 mb-6">Success message or confirmation details appear here.</p>

        <div class="bg-slate-50 border rounded-xl p-6 text-left mb-6">
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div><strong>Reference:</strong> AUTO-001</div>
                <div><strong>Date:</strong> 2026-05-01</div>
                <div><strong>Status:</strong> Completed</div>
                <div><strong>Total:</strong> Value</div>
            </div>
        </div>

        <div class="flex gap-4 justify-center">
            <div class="h-11 px-6 rounded-lg bg-slate-900 text-white flex items-center justify-center">Primary Action</div>
            <div class="h-11 px-6 rounded-lg border bg-slate-50 flex items-center justify-center">Secondary Action</div>
        </div>
    </section>
    """


def _list_body(screen: UIScreen) -> str:
    """
    Dynamic list/history wireframe.
    """
    card = """
    <div class="bg-white border rounded-xl p-5 shadow-sm">
        <div class="flex justify-between items-center mb-3">
            <h3 class="font-semibold">Record #001</h3>
            <span class="text-xs px-3 py-1 rounded-full bg-green-100 text-green-700">Status</span>
        </div>
        <div class="grid grid-cols-3 gap-4 text-sm text-slate-600 mb-4">
            <div>Date: 2026-05-01</div>
            <div>Total: Value</div>
            <div>Items: 3</div>
        </div>
        <div class="flex gap-3">
            <div class="h-10 px-4 rounded-lg bg-slate-900 text-white flex items-center justify-center text-sm">View Details</div>
            <div class="h-10 px-4 rounded-lg border bg-slate-50 flex items-center justify-center text-sm">Track</div>
        </div>
    </div>
    """

    return f"""
    <section>
        {_top_nav_block()}
        <div class="space-y-4">
            {card}
            {card}
            {card}
        </div>
    </section>
    """


def _table_body(screen: UIScreen) -> str:
    """
    Dynamic table/admin wireframe.
    """
    return f"""
    <section>
        <div class="bg-white rounded-2xl border p-6 shadow-sm mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-2xl font-semibold">{screen.name}</h2>
                <p class="text-sm text-slate-500 mt-1">Manage records for this feature</p>
            </div>
            <div class="h-11 px-5 rounded-lg bg-slate-900 text-white flex items-center justify-center">
                Add New
            </div>
        </div>

        <div class="bg-white rounded-2xl border shadow-sm overflow-hidden">
            <div class="grid grid-cols-12 gap-4 px-6 py-4 bg-slate-50 border-b font-medium text-sm">
                <div class="col-span-4">Name</div>
                <div class="col-span-2">Type</div>
                <div class="col-span-2">Status</div>
                <div class="col-span-2">Updated</div>
                <div class="col-span-2">Actions</div>
            </div>

            <div class="grid grid-cols-12 gap-4 px-6 py-4 border-b text-sm">
                <div class="col-span-4">Sample Record A</div>
                <div class="col-span-2">Category</div>
                <div class="col-span-2">Active</div>
                <div class="col-span-2">Today</div>
                <div class="col-span-2 text-slate-600">Edit | Delete</div>
            </div>

            <div class="grid grid-cols-12 gap-4 px-6 py-4 border-b text-sm">
                <div class="col-span-4">Sample Record B</div>
                <div class="col-span-2">Category</div>
                <div class="col-span-2">Draft</div>
                <div class="col-span-2">Yesterday</div>
                <div class="col-span-2 text-slate-600">Edit | Delete</div>
            </div>
        </div>
    </section>
    """


def _error_body(screen: UIScreen) -> str:
    """
    Dynamic error-state wireframe.
    """
    return f"""
    <section class="max-w-4xl mx-auto bg-white rounded-2xl border shadow-sm p-10">
        <div class="rounded-xl border border-red-300 bg-red-50 p-6 mb-6">
            <h2 class="text-2xl font-bold text-red-800 mb-2">{screen.name}</h2>
            <p class="text-red-700">An error or exception state is shown here.</p>
        </div>

        <div class="grid grid-cols-2 gap-6">
            <div class="bg-slate-50 border rounded-xl p-5">
                <h3 class="font-semibold mb-4">Error Details</h3>
                <ul class="space-y-2 text-sm text-slate-600">
                    <li>• Validation issue</li>
                    <li>• Processing failure</li>
                    <li>• User can retry or go back</li>
                </ul>
            </div>

            <div class="bg-slate-50 border rounded-xl p-5">
                <h3 class="font-semibold mb-4">Available Actions</h3>
                <div class="space-y-3">
                    <div class="h-11 rounded-lg bg-slate-900 text-white flex items-center justify-center">Retry</div>
                    <div class="h-11 rounded-lg border bg-white flex items-center justify-center">Edit Details</div>
                    <div class="h-11 rounded-lg border bg-white flex items-center justify-center">Go Back</div>
                </div>
            </div>
        </div>
    </section>
    """


def _generic_body(screen: UIScreen) -> str:
    """
    Generic fallback layout for any automatically discovered feature.
    """
    return f"""
    <section class="grid grid-cols-12 gap-6">
        <div class="col-span-8 bg-white rounded-2xl border shadow-sm p-8">
            <h2 class="text-2xl font-semibold mb-4">{screen.name}</h2>
            <p class="text-slate-600 mb-6">{screen.description}</p>

            <div class="grid grid-cols-2 gap-5">
                <div class="rounded-xl border bg-slate-50 p-5">
                    <h3 class="font-medium mb-3">Main Content Area</h3>
                    <div class="h-4 bg-slate-200 rounded mb-2"></div>
                    <div class="h-4 bg-slate-200 rounded mb-2"></div>
                    <div class="h-4 bg-slate-200 rounded w-2/3"></div>
                </div>

                <div class="rounded-xl border bg-slate-50 p-5">
                    <h3 class="font-medium mb-3">User Actions</h3>
                    <div class="h-10 bg-slate-900 rounded-lg mb-3"></div>
                    <div class="h-10 bg-white border rounded-lg"></div>
                </div>
            </div>
        </div>

        <aside class="col-span-4 bg-white rounded-2xl border shadow-sm p-8">
            <h3 class="text-xl font-semibold mb-4">Context Panel</h3>
            <p class="text-sm text-slate-600">
                Additional guidance, status, or related information appears here.
            </p>
        </aside>
    </section>
    """


def fallback_wireframe_html(
    project_name: str,
    screen: UIScreen,
    change_request: str | None = None,
) -> str:
    """
    Dynamically generates a wireframe from screen metadata.

    No fixed UI-SCR IDs are used.
    """
    related = ", ".join(screen.related_requirements)
    purpose = _infer_screen_purpose(screen)

    if purpose == "form":
        body = _form_body(screen)
    elif purpose == "grid":
        body = _grid_body(screen)
    elif purpose == "detail":
        body = _detail_body(screen)
    elif purpose == "cart":
        body = _cart_body(screen)
    elif purpose == "checkout":
        body = _checkout_body(screen, change_request)
    elif purpose == "success":
        body = _success_body(screen)
    elif purpose == "list":
        body = _list_body(screen)
    elif purpose == "table":
        body = _table_body(screen)
    elif purpose == "error":
        body = _error_body(screen)
    else:
        body = _generic_body(screen)

    return _page_shell(
        project_name=project_name,
        screen=screen,
        body=body,
        related=related,
    )