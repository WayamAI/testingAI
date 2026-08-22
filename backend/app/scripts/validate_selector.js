// Real live validation that a proposed selector actually resolves on the
// live page — the last real check before a self-heal candidate is shown
// to a human for approval.
//
// Usage: node validate_selector.js <url> <selector>
const { chromium } = require("@playwright/test");

async function main() {
  const [url, selector] = process.argv.slice(2);
  if (!url || !selector) {
    console.error("usage: node validate_selector.js <url> <selector>");
    process.exit(1);
  }

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });
    const count = await page.locator(selector).count();
    console.log(JSON.stringify({ count }));
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(String(err));
  process.exit(1);
});
