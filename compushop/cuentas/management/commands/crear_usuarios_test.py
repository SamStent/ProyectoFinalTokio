from django.core.management.base import BaseCommand
from cuentas.models import Usuario


class Command(BaseCommand):
    help = 'Crea usuarios demo para los roles del personal (almacén, ventas, gerencia)'

    def handle(self, *args, **options):
        usuarios_demo = [
            ('almacen_user', 'almacen@compushop.local', 'almacen123', 'personal', 'almacen'),
            ('ventas_user', 'ventas@compushop.local', 'ventas123', 'personal', 'ventas'),
            ('gerencia_user', 'gerencia@compushop.local', 'gerencia123', 'personal', 'gerencia'),
        ]

        for username, email, password, tipo_cuenta, rol_personal in usuarios_demo:
            if not Usuario.objects.filter(username=username).exists():
                user = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    tipo_cuenta=tipo_cuenta,
                    rol_personal=rol_personal,
                    is_active=True,
                    is_staff=True  # puedes poner False si no quieres acceso al admin
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Usuario creado: {username} ({rol_personal})'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ El usuario "{username}" ya existe, se omitió.'))

        self.stdout.write(self.style.SUCCESS('\nUsuarios de prueba listos para usar.'))
        self.stdout.write(self.style.SUCCESS('Inicia sesión con:'))
        self.stdout.write('  🟢 Almacén → almacen_user / almacen123')
        self.stdout.write('  🔵 Ventas  → ventas_user / ventas123')
        self.stdout.write('  🟣 Gerencia → gerencia_user / gerencia123')
