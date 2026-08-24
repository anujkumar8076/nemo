import { describe, expect, it } from "vitest";

import { isApiHealth } from "../src";

describe("isApiHealth", () => {
  it("accepts a valid API health envelope", () => {
    expect(isApiHealth({ service: "api", status: "healthy" })).toBe(true);
  });

  it("rejects an untrusted shape", () => {
    expect(isApiHealth({ service: "worker", status: "healthy" })).toBe(false);
  });
});
