"""Strict input validation & DTO schemas (Japan-enterprise style).

Spring equivalent: Jakarta Bean Validation (@NotBlank, @Pattern, @Email, @Size) + @Valid.
Returns field-level error lists: [{"field": "empCode", "message": "..."}].
"""

import re

from .exceptions import ValidationError

EMP_CODE_RE = re.compile(r"^EMP-\d{4}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ALLOWED_DEPARTMENTS = {
    "Sales": "営業部",
    "Engineering": "開発部",
    "HR": "人事部",
    "Finance": "経理部",
    "QA": "品質保証部",
}


def validate_create_employee(body):
    """Validate full payload for POST /@@api-employees."""
    errors = []

    emp_code = str(body.get("empCode", "")).strip().upper()
    if not emp_code:
        errors.append({"field": "empCode", "message": "Required."})
    elif not EMP_CODE_RE.match(emp_code):
        errors.append({"field": "empCode", "message": "Must match format EMP-0001."})

    _validate_common_fields(body, errors, partial=False)

    if errors:
        raise ValidationError(errors)

    dept_en = body["departmentEn"].strip()
    return {
        "emp_code": emp_code,
        "name_en": body["nameEn"].strip(),
        "name_ja": body["nameJa"].strip(),
        "department_en": dept_en,
        "department_ja": body.get("departmentJa", "").strip() or ALLOWED_DEPARTMENTS[dept_en],
        "role": body["role"].strip(),
        "email": body["email"].strip().lower(),
        "skills": _normalize_skills(body.get("skills", [])),
    }


def validate_put_employee(body):
    """Validate full replacement payload for PUT /@@api-employees/{empCode}."""
    errors = []

    # Optimistic locking check (Japan-enterprise standard, like JPA @Version)
    version = body.get("version")
    if not isinstance(version, int) or version < 1:
        errors.append({"field": "version", "message": "Required positive integer for optimistic locking."})

    _validate_common_fields(body, errors, partial=False)

    if errors:
        raise ValidationError(errors)

    dept_en = body["departmentEn"].strip()
    return {
        "version": version,
        "name_en": body["nameEn"].strip(),
        "name_ja": body["nameJa"].strip(),
        "department_en": dept_en,
        "department_ja": body.get("departmentJa", "").strip() or ALLOWED_DEPARTMENTS[dept_en],
        "role": body["role"].strip(),
        "email": body["email"].strip().lower(),
        "skills": _normalize_skills(body.get("skills", [])),
    }


def validate_patch_employee(body):
    """Validate partial update payload for PATCH /@@api-employees/{empCode}."""
    if not body:
        raise ValidationError([{"field": "body", "message": "At least one field is required."}])

    errors = []
    _validate_common_fields(body, errors, partial=True)

    if "version" in body and (not isinstance(body["version"], int) or body["version"] < 1):
        errors.append({"field": "version", "message": "Must be a positive integer."})

    if errors:
        raise ValidationError(errors)

    cleaned = {}
    if "version" in body:
        cleaned["version"] = body["version"]
    if "nameEn" in body:
        cleaned["name_en"] = body["nameEn"].strip()
    if "nameJa" in body:
        cleaned["name_ja"] = body["nameJa"].strip()
    if "departmentEn" in body:
        dept_en = body["departmentEn"].strip()
        cleaned["department_en"] = dept_en
        cleaned["department_ja"] = body.get("departmentJa", "").strip() or ALLOWED_DEPARTMENTS[dept_en]
    elif "departmentJa" in body:
        cleaned["department_ja"] = body["departmentJa"].strip()
    if "role" in body:
        cleaned["role"] = body["role"].strip()
    if "email" in body:
        cleaned["email"] = body["email"].strip().lower()
    if "skills" in body:
        cleaned["skills"] = _normalize_skills(body["skills"])

    return cleaned


def _validate_common_fields(body, errors, partial=False):
    for field_name, max_len in [("nameEn", 100), ("nameJa", 100), ("role", 100)]:
        if partial and field_name not in body:
            continue
        val = str(body.get(field_name, "")).strip()
        if not val:
            errors.append({"field": field_name, "message": "Required."})
        elif len(val) > max_len:
            errors.append({"field": field_name, "message": f"Max length is {max_len}."})

    if not partial or "departmentEn" in body:
        dept_en = str(body.get("departmentEn", "")).strip()
        if not dept_en:
            errors.append({"field": "departmentEn", "message": "Required."})
        elif dept_en not in ALLOWED_DEPARTMENTS:
            allowed = ", ".join(sorted(ALLOWED_DEPARTMENTS.keys()))
            errors.append({"field": "departmentEn", "message": f"Must be one of: {allowed}."})

    if not partial or "email" in body:
        email = str(body.get("email", "")).strip()
        if not email:
            errors.append({"field": "email", "message": "Required."})
        elif not EMAIL_RE.match(email):
            errors.append({"field": "email", "message": "Invalid email format."})

    if "skills" in body and not isinstance(body["skills"], list):
        errors.append({"field": "skills", "message": "Must be a JSON array of strings."})


def _normalize_skills(skills):
    return [str(s).strip() for s in skills if str(s).strip()]
