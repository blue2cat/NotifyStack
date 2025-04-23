"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateNotification = validateNotification;
const ajv_1 = __importDefault(require("ajv"));
const ajv_formats_1 = __importDefault(require("ajv-formats"));
const schema_json_1 = __importDefault(require("./schema.json"));
const ajv = new ajv_1.default({
    allErrors: true,
    strict: false
});
(0, ajv_formats_1.default)(ajv);
const validate = ajv.compile(schema_json_1.default);
function validateNotification(data) {
    const valid = validate(data);
    return {
        valid,
        errors: valid
            ? undefined
            : validate.errors?.map((e) => `${e.instancePath} ${e.message}`),
    };
}
//# sourceMappingURL=validate.js.map