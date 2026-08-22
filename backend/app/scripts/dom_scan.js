// Real DOM scan for self-healing candidate discovery. Launches a real
// headless Chromium (via the frontend's installed @playwright/test),
// navigates to the given URL, and prints a JSON array of real interactive
// elements — never a synthetic/guessed list.
//
// Usage: node dom_scan.js <url>
const { chromium } = require("@playwright/test");

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error("usage: node dom_scan.js <url>");
    process.exit(1);
  }

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });

    const candidates = await page.$$eval(
      "a, button, input, select, textarea, [role='button']",
      (elements) =>
        elements.slice(0, 100).map((el, index) => {
          const tag = el.tagName.toLowerCase();
          const text = (el.textContent || el.getAttribute("placeholder") || el.getAttribute("aria-label") || "").trim().slice(0, 80);
          const id = el.getAttribute("id");
          const testId = el.getAttribute("data-testid");
          const name = el.getAttribute("name");
          const role = el.getAttribute("role");

          let selector_hint;
          if (testId) selector_hint = `[data-testid="${testId}"]`;
          else if (id) selector_hint = `#${id}`;
          else if (name) selector_hint = `${tag}[name="${name}"]`;
          else if (role) selector_hint = `[role="${role}"]`;
          else selector_hint = `${tag}:nth-of-type(${index + 1})`;

          return { index, tag, text, selector_hint };
        })
    );

    console.log(JSON.stringify(candidates));
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(String(err));
  process.exit(1);
});
