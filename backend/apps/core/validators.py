# ==============================================================================
#
#                      CUSTOM VALIDATORS FOR CRYPTOBOT
#
# This file contains custom validation classes used throughout the project to
# enforce business logic and security rules. Each validator is designed to be a
# reusable piece of logic.
#
# ==============================================================================

# --- Required Imports ---
import re
from django.core.exceptions import ValidationError

# ------------------------------------------------------------------------------
# SECTION 1: Password Complexity Validator
# ------------------------------------------------------------------------------


class PasswordComplexityValidator:
    """
    A custom password validator that ensures a password meets industry-standard
    complexity requirements.

    This class is designed to be used within Django's `AUTH_PASSWORD_VALIDATORS`
    setting.

    Validation Rules:
      - Must contain at least one uppercase letter (A-Z).
      - Must contain at least one lowercase letter (a-z).
      - Must contain at least one digit (0-9).
      - Must contain at least one special character (e.g., !, @, #, $, _, etc.).
    """

    def validate(self, password, user=None):
        """
        Runs the validation logic against the provided password.

        This method is called automatically by the Django framework during form
        validation (e.g., user creation, password change).

        Args:
            password (str): The password string to validate.
            user: The user instance (optional, not used here but part of the
                  required signature for Django validators).

        Raises:
            ValidationError: If the password fails to meet any of the defined
                             complexity rules.
        """

        # --- Rule 1: Check for the presence of at least one uppercase letter ---
        # The pattern [A-Z] searches for any character in the range from A to Z.
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                'The password must contain at least one uppercase letter.',
                code='password_no_upper',
            )

        # --- Rule 2: Check for the presence of at least one lowercase letter ---
        # The pattern [a-z] searches for any character in the range from a to z.
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                'The password must contain at least one lowercase letter.',
                code='password_no_lower',
            )

        # --- Rule 3: Check for the presence of at least one digit ---
        # The \d shortcut is equivalent to [0-9] and searches for any numeric digit.
        if not re.search(r'\d', password):
            raise ValidationError(
                'The password must contain at least one digit.',
                code='password_no_digit',
            )

        # --- Rule 4: Check for the presence of at least one special symbol ---
        # The pattern [\W_] is a careful construction:
        #   \W : Searches for any character that is NOT alphanumeric (a letter or number).
        #   _  : The underscore is an exception to \W, so we add it explicitly.
        #   [] : The character set brackets mean "any character that is either \W or _".
        if not re.search(r'[\W_]', password):
            raise ValidationError(
                'The password must contain at least one special character.',
                code='password_no_symbol',
            )

    def get_help_text(self):
        """
        Provides a user-friendly help text.

        This method is called by Django to display the password requirements
        in forms, guiding the user before they type.

        Returns:
            str: A summary of all complexity rules.
        """
        return (
            'Your password must contain at least one uppercase letter, '
            'one lowercase letter, one digit, and one special character.'
        )
