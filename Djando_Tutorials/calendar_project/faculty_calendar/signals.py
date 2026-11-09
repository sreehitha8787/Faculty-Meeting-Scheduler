"""Automatic demo-account creation is intentionally disabled.

Do not create users or assign passwords from post_migrate signals. If demo data is
needed, create it through an explicit development-only management command using
credentials supplied outside source control.
"""
