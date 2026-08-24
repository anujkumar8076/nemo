import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { ServiceStatus } from "../components/service-status";

describe("ServiceStatus", () => {
  it("includes status text so color is not the only signal", () => {
    const markup = renderToStaticMarkup(
      <ServiceStatus name="postgresql" status={{ status: "available" }} />,
    );
    expect(markup).toContain("Available");
    expect(markup).toContain("postgresql");
  });
});
