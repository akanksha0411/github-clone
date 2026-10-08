import re

def validate_username(username: str) -> str | None:
    #If username is empty, return error message
    if not username:
        return "Username cannot be empty"
    #Convert username to lowercase for validation
    username = username.lower()
    #Check if username length is between 3 and 50 characters
    if not (3 <= len(username) <= 50):
        return f"Length must be between 3 and 50 characters (currently {len(username)})."
    #Check if username starts with a lowercase letter
    if not username[0].isalpha() or not username[0].islower():
        return "Must start with a lowercase letter (a-z)."
    #Check if username contains only lowercase letters, digits, and underscores
    if not re.fullmatch(r"[a-z0-9_]+", username):
        return "Can only contain lowercase letters, digits, and underscores."
    return None  # Valid username

def validate_password(password: str) -> str | None:
    # Validate password based on the following criteria:
    # 1. Length between 8 and 20 characters
    # 2. At least one uppercase letter
    # 3. At least one lowercase letter
    # 4. At least one digit
    # 5. At least one special character (e.g., !@#$%^&*(),.?":{}|<>)
    if not password:
        return "Password cannot be empty"
    if len(password) < 8 or len(password) > 20:
        return "Password length must be 8-20 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    return None  # Valid password

def validate_repo_name(repo_name: str) -> str | None:
    # Validate repository name based on the following criteria:
    # 1. Length between 3 and 100 characters
    # 2. Can only contain letters, digits, hyphens, and underscores
    # 3. Must start with a letter
    if not repo_name:
        return "Repository name cannot be empty"
    if len(repo_name) < 3 or len(repo_name) > 100:
        return "Repository name length must be between 3 and 100 characters"
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", repo_name):
        return "Repository name can only contain letters, digits, hyphens, and underscores"
    if repo_name[0] not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return "Repository name must start with a letter"
    return None  # Valid repository name

def validate_repo_description(repo_description: str | None) -> str | None:
    # Validate repository description based on the following criteria:
    # 1. Length must not exceed 500 characters
    if repo_description is None:
        return None  # Description is optional
    if repo_description.strip() == "":
        return None  # Empty description is allowed
    if len(repo_description) > 500:
        return "Repository description cannot exceed 500 characters"
    return None  # Valid repository description
