import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { StatusBadge } from "../components/status-badge";

describe("StatusBadge", () => {
  it("renders a human-readable label in addition to semantic color", () => {
    const markup = renderToStaticMarkup(<StatusBadge status="awaiting_approval" />);
    expect(markup).toContain("Waiting for approval");
    expect(markup).toContain("badge-info");
  });
});
