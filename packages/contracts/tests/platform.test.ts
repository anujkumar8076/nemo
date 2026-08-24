import { describe, expect, it } from "vitest";

import { isProjectPage } from "../src/platform";

describe("platform contracts", () => {
  it("rejects malformed project pages at the service boundary", () => {
    expect(isProjectPage({ items: [{ id: "only-an-id" }], next_cursor: null })).toBe(false);
  });
});
