"""Deterministic Playwright test-code templates, one per baseline category.

Used directly by the demo AI fallback (so baseline generation is fully
functional with zero AI configuration) and as the skeleton the real Ollama
provider is asked to specialize. Every template is syntactically valid,
runnable JS — never a string that merely looks like a test.
"""
import asyncio
import json

CATEGORIES = [
    "auth", "api", "crud", "ui_form", "ui_navigation",
    "ui_component", "integration", "edge_case", "performance", "accessibility",
]

_TEMPLATES: dict[str, str] = {
    "auth": """test('{title}', async ({{ page }}) => {{
  await page.goto('/login');
  await page.getByLabel(/email/i).fill('user@example.com');
  await page.getByLabel(/password/i).fill('placeholder-password');
  await page.getByRole('button', {{ name: /sign in|log in/i }}).click();
  await expect(page).not.toHaveURL(/login/);
}});""",
    "api": """test('{title}', async ({{ request }}) => {{
  const response = await request.get('/api/health');
  expect(response.status()).toBeLessThan(500);
}});""",
    "crud": """test('{title}', async ({{ page }}) => {{
  await page.goto('/');
  // Create
  const createButton = page.getByRole('button', {{ name: /create|add|new/i }}).first();
  if (await createButton.isVisible().catch(() => false)) {{
    await createButton.click();
  }}
  // Verify the page responded to the action without a fatal error page.
  await expect(page.locator('body')).not.toContainText(/500|internal server error/i);
}});""",
    "ui_form": """test('{title}', async ({{ page }}) => {{
  await page.goto('/');
  const firstInput = page.locator('input, textarea').first();
  if (await firstInput.isVisible().catch(() => false)) {{
    await firstInput.fill('test value');
  }}
  await expect(page.locator('body')).toBeVisible();
}});""",
    "ui_navigation": """test('{title}', async ({{ page }}) => {{
  await page.goto('/');
  const startUrl = page.url();
  const firstLink = page.locator('a[href]').first();
  if (await firstLink.isVisible().catch(() => false)) {{
    await firstLink.click();
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).not.toBe(startUrl);
  }}
}});""",
    "ui_component": """test('{title}', async ({{ page }}) => {{
  await page.goto('/');
  await expect(page.locator('body')).toBeVisible();
  await expect(page).toHaveTitle(/.+/);
}});""",
    "integration": """test('{title}', async ({{ page }}) => {{
  await page.goto('/');
  // Multi-step flow placeholder: navigate, then verify a second real page loads.
  const link = page.locator('a[href]').first();
  if (await link.isVisible().catch(() => false)) {{
    await link.click();
    await expect(page.locator('body')).toBeVisible();
  }}
}});""",
    "edge_case": """test('{title}', async ({{ page }}) => {{
  await page.goto('/');
  const input = page.locator('input').first();
  if (await input.isVisible().catch(() => false)) {{
    await input.fill('');
    const submit = page.getByRole('button', {{ name: /submit|save|send/i }}).first();
    if (await submit.isVisible().catch(() => false)) await submit.click();
  }}
  await expect(page.locator('body')).not.toContainText(/500|internal server error/i);
}});""",
    "performance": """test('{title}', async ({{ page }}) => {{
  const start = Date.now();
  await page.goto('/');
  const loadTime = Date.now() - start;
  expect(loadTime).toBeLessThan(10000);
}});""",
    "accessibility": """test('{title}', async ({{ page }}) => {{
  await page.goto('/');
  const images = page.locator('img');
  const count = await images.count();
  for (let i = 0; i < Math.min(count, 10); i++) {{
    const alt = await images.nth(i).getAttribute('alt');
    expect(alt).not.toBeNull();
  }}
}});""",
}


def render_test(category: str, title: str) -> str:
    """Returns a complete, syntactically valid Playwright test file body
    (single test) for the given category. Unknown categories fall back to
    ui_component, the least assumption-laden template."""
    body = _TEMPLATES.get(category, _TEMPLATES["ui_component"])
    safe_title = json.dumps(title)[1:-1]  # escape quotes/backslashes for JS string literal
    rendered_body = body.format(title=safe_title)
    return (
        "const { test, expect } = require('@playwright/test');\n\n"
        + rendered_body
        + "\n"
    )


async def validate_js_syntax(code: str) -> bool:
    """Real syntax validation via `node --check` — the shared gate every
    AI-generated (or demo-templated) test must pass before persistence.
    Never trust generated code as runnable just because it parsed as JSON."""
    proc = await asyncio.create_subprocess_exec(
        "node", "--check", "/dev/stdin",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.communicate(input=code.encode())
    return proc.returncode == 0
