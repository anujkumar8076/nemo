import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import tseslint from "typescript-eslint";

const compat = new FlatCompat({ baseDirectory: import.meta.dirname });

export default tseslint.config(
  { ignores: [".next/**", "next-env.d.ts"] },
  js.configs.recommended,
  ...compat.extends("next/core-web-vitals", "next/typescript"),
);
