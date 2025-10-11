from django.core.management.base import BaseCommand
from tienda.models import Producto, Proveedor, Categoria
from faker import Faker
from decimal import Decimal
import random

class Command(BaseCommand):
    help = "Genera datos de ejemplo para Proveedores, Categorías y Productos"

    def add_arguments(self, parser):
        parser.add_argument(
            '--proveedores',
            type=int,
            default=10,
            help='Número de proveedores a crear (por defecto: 10)'
        )
        parser.add_argument(
            '--productos',
            type=int,
            default=40,
            help='Número de productos a crear (por defecto: 40)'
        )

    def handle(self, *args, **options):
        fake = Faker('es_ES')
        num_proveedores = options['proveedores']
        num_productos = options['productos']

        # --- Crear categorías si no existen ---
        categorias = list(Categoria.objects.all())
        if not categorias:
            self.stdout.write(self.style.WARNING("  No existen categorías, creando categorías base..."))
            categorias_nombres = ["Portátiles", "Componentes", "Periféricos", "Redes", "Accesorios"]
            for nombre in categorias_nombres:
                cat = Categoria.objects.create(nombre=nombre, slug=nombre.lower())
                categorias.append(cat)
            self.stdout.write(self.style.SUCCESS(f" {len(categorias)} categorías creadas."))

        # --- Crear proveedores ---
        self.stdout.write("\n Creando proveedores...")
        proveedores = []
        for _ in range(num_proveedores):
            proveedor = Proveedor.objects.create(
                nombre_empresa=fake.company(),
                cif=fake.unique.bothify(text="B########"),
                telefono=fake.phone_number(),
                email=fake.company_email(),
                direccion=fake.address(),
                descuento=Decimal(str(round(random.uniform(0, 15), 2))),
                iva=Decimal(str(random.choice([21.00, 10.00, 4.00]))),
            )
            proveedores.append(proveedor)

        self.stdout.write(self.style.SUCCESS(f"{len(proveedores)} proveedores creados."))

        # --- Crear productos ---
        self.stdout.write("\n  Creando productos...")
        for _ in range(num_productos):
            categoria = random.choice(categorias)
            proveedor = random.choice(proveedores)

            Producto.objects.create(
                categoria=categoria,
                nombre=fake.word().capitalize(),
                slug=fake.slug(),
                descripcion=fake.sentence(nb_words=10),
                precio=Decimal(str(round(random.uniform(10, 2000), 2))),
                stock=random.randint(0, 250),
                stock_minimo=random.randint(5, 30),
                disponible=random.choice([True, True, False]),
                proveedor=proveedor,
            )

        self.stdout.write(self.style.SUCCESS(
            f"\n Generación completada: {num_proveedores} proveedores, {num_productos} productos.\n"
        ))
