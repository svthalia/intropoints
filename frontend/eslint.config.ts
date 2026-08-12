import { globalIgnores } from "eslint/config"
import { defineConfigWithVueTs, vueTsConfigs } from "@vue/eslint-config-typescript"
import pluginVue from "eslint-plugin-vue"
import pluginVitest from "@vitest/eslint-plugin"
import pluginOxlint from "eslint-plugin-oxlint"
import skipFormatting from "eslint-config-prettier/flat"
import js from "@eslint/js"

export default defineConfigWithVueTs(
  {
    name: "app/files-to-lint",
    files: ["**/*.{vue,ts,mts,tsx}"],
  },

  globalIgnores(["**/dist/**", "**/dist-ssr/**", "**/coverage/**", "shims-vue.d.ts"]),

  js.configs.recommended,

  ...pluginVue.configs["flat/essential"],

  vueTsConfigs.recommended,

  {
    ...pluginVitest.configs.recommended,
    files: ["src/**/__tests__/*"],
  },

  // Custom rules for mirroring Ruff's strictness on the frontend
  {
    rules: {
      // Prefer modern syntax
      "prefer-const": "error",
      "no-var": "error",

      // Mirrors Ruff's SIM (simplification)
      "object-shorthand": "error",

      // Warns for use of any type or unsed variables
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_", // Allow _prefix for intentionally unused args
          varsIgnorePattern: "^_",
        },
      ],

      // Enforces import type for imports that are only used as types, not as values at runtime
      "@typescript-eslint/consistent-type-imports": [
        "error",
        {
          prefer: "type-imports",
        },
      ],

      // Don't enforce single word component ban because of pages/views conventions
      "vue/multi-word-component-names": "off",

      // Enforce <script setup> api style
      "vue/component-api-style": ["error", ["script-setup"]],

      // Enforce defineProps before defineEmits for consistent code structure
      "vue/define-macros-order": [
        "error",
        {
          order: ["defineProps", "defineEmits"],
        },
      ],
    },
  },

  ...pluginOxlint.buildFromOxlintConfigFile(".oxlintrc.json"),

  // Must be last
  skipFormatting,
)
