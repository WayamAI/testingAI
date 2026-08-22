const { add, divide } = require("./math");

test("add sums two numbers", () => {
  expect(add(2, 3)).toBe(5);
});

test("divide returns the quotient", () => {
  expect(divide(10, 2)).toBe(5);
});

// Intentionally wrong expectation — proves the fixture produces a real
// failing result, not an all-green demo.
test("add is intentionally asserted wrong", () => {
  expect(add(2, 2)).toBe(5);
});
