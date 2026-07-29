from splent_io.splent_feature_auth.models import User
from splent_framework.seeders.BaseSeeder import BaseSeeder


class AdminSeeder(BaseSeeder):
    priority = 0  # Run before other seeders

    def run(self):
        admin = User(
            email="admin@admin.com", password="admin", active=True, role="admin"
        )
        self.seed([admin])
