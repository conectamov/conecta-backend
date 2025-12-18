<img src="https://raw.githubusercontent.com/conectamov/.github/main/banner.png" width="300">

# Conecta API

This repository contains the source code and documentation for the Conecta REST API, which powers all platform services.
The full reference documentation (schemas, examples, endpoints) is available **[here](https://dolphin-app-ykgod.ondigitalocean.app/docs/swagger)**.

---

## Development Setup

If you haven't got a virtual environment set up yet, please do it like this:


Then, install the dependencies via bash:
```sh
sh install.sh
```

or

```sh
pip install -r requirements.txt
pre-commit install
```

You're free to go now.

## API Usage

A common initial flow for interacting with the API is:

`POST /user` → create a user
`POST /auth/login` → obtain an authentication token
`GET /user/{current_user.id}` → retrieve the authenticated user's data

Technical details for each route are available in the Swagger documentation.

---

## Permissions and Important Notes

Some endpoints are protected and require specific role permissions.
A key behavioral detail is the conditional access to user-scoped routes.

### Access rules for `GET /user/{user_id}`

- **When requesting the authenticated user's own ID** (`user_id == current_user.id`):
  the request is allowed.

- **When requesting a different user's ID**:
  the caller must have a privileged role to access that data.
  Requests without the required role will be denied.

**IMPORTANT NOTE**: This rule applies to any endpoint that explicitly requires a `user_id`.

---
