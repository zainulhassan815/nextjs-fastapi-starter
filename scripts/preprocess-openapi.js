const fs = require("fs");
const path = require("path");

const specPath =
  process.argv[2] || path.join(__dirname, "../frontend/openapi.json");
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));

// Remove tag prefix from operation IDs for cleaner SDK method names
// "auth-register" → "register"
for (const pathData of Object.values(spec.paths || {})) {
  for (const operation of Object.values(pathData)) {
    if (operation.operationId && operation.tags?.[0]) {
      const prefix = `${operation.tags[0]}-`;
      if (operation.operationId.startsWith(prefix)) {
        operation.operationId = operation.operationId.slice(prefix.length);
      }
    }
  }
}

fs.writeFileSync(specPath, JSON.stringify(spec, null, 2));
console.log("Preprocessed OpenAPI spec:", specPath);
