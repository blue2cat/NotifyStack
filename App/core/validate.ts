import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import schema from './schema.json';

const ajv = new Ajv({
  allErrors: true,
  strict: false
});

addFormats(ajv);

const validate = ajv.compile(schema);

export function validateNotification(data: unknown): {
  valid: boolean;
  errors?: string[];
} {
  const valid = validate(data);
  return {
    valid,
    errors: valid
      ? undefined
      : validate.errors?.map((e) => `${e.instancePath} ${e.message}`),
  };
}
