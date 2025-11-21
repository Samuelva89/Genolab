import globals from "globals";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";
import hooksPlugin from "eslint-plugin-react-hooks";
import refreshPlugin from "eslint-plugin-react-refresh";

export default tseslint.config(
  {
    ignores: ["dist", "node_modules", "eslint.config.js", "vite.config.ts"],
  },
  {
    files: ["**/*.{js,jsx,mjs,cjs,ts,tsx}"],
    plugins: {
      "react": pluginReact,
      "react-hooks": hooksPlugin,
      "react-refresh": refreshPlugin,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
      },
      parser: tseslint.parser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        // Usar tsconfig.app.json es más específico para el código de la aplicación
        project: "./tsconfig.app.json", 
      },
    },
    rules: {
      // Reglas recomendadas de React
      ...pluginReact.configs.recommended.rules,
      // Reglas recomendadas de React Hooks
      ...hooksPlugin.configs.recommended.rules,
      // Regla de Vite/React Refresh
      "react-refresh/only-export-components": "warn",
      // Apagar reglas innecesarias en un proyecto TypeScript/Vite
      "react/prop-types": "off", 
      "react/react-in-jsx-scope": "off"
    },
    settings: {
        react: {
            // Detecta automáticamente la versión de React
            version: "detect"
        }
    }
  },
  // Configuraciones recomendadas de typescript-eslint
  ...tseslint.configs.strict,
  ...tseslint.configs.stylistic,
);
