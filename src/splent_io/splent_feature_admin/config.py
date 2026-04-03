"""
admin feature configuration.

Injects environment variables into Flask app.config.
To regenerate from source code: splent feature:inject-config splent_feature_admin
"""


def inject_config(app):
    app.config.update({})
