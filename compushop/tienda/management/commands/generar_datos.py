from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tienda.models import Producto, Categoria, Proveedor
from faker import Faker
import random
from pathlib import Path

class Command(BaseCommand):
    help = "Genera datos de prueba para la tienda (categorías, proveedores, productos)"

    def handle(self, *args, **options):
        fake = Faker('es_ES')

        # --- Categorías ---
        categorias_nombres = [
            'Procesadores', 'Memorias RAM', 'Placas Base', 'Tarjetas Gráficas',
            'Monitores', 'Almacenamiento', 'Periféricos', 'Fuentes de Alimentación',
            'Cajas de PC', 'Refrigeración'
        ]
        categorias = []
        for nombre in categorias_nombres:
            slug = slugify(nombre)
            categoria, creada = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'slug': slug}
            )
            categorias.append(categoria)
        self.stdout.write(self.style.SUCCESS(f'{len(categorias)} categorías creadas o existentes.'))

        # --- Proveedores ---
        proveedores_nombres = [
            'TechWorld', 'InfoParts', 'CompuHub', 'DigitalLine', 'ElectroSystems',
            'HardPlus', 'PCMaster', 'RedNova', 'DataCore', 'ByteStore'
        ]

        def generar_cif_unico():
            """Genera un CIF tipo español (una letra + 8 dígitos) y garantiza unicidad."""
            import string
            from tienda.models import Proveedor

            letras = string.ascii_uppercase
            while True:
                cif = random.choice(letras) + ''.join(random.choices('0123456789', k=8))
                if not Proveedor.objects.filter(cif=cif).exists():
                    return cif

        proveedores = []
        for nombre in proveedores_nombres:
            proveedor, creado = Proveedor.objects.get_or_create(
                nombre_empresa=nombre,
                defaults={
                    'cif': generar_cif_unico(),
                    'email': fake.company_email(),
                    'telefono': fake.phone_number(),
                    'direccion': fake.address(),
                    'sitio_web': f"https://www.{nombre.lower()}.com",
                    'activo': True,
                    'iva': 21,
                    'descuento': random.randint(0, 15)
                }
            )
            proveedores.append(proveedor)
        self.stdout.write(self.style.SUCCESS(f'{len(proveedores)} proveedores creados o existentes.'))

        # --- Productos ---
        productos_generados = 0

        nombres_productos = [
            # Procesadores
            "Intel Core i3 12100F", "Intel Core i5 12400", "Intel Core i7 13700K", "Intel Core i9 13900K",
            "AMD Ryzen 5 5600", "AMD Ryzen 7 5800X3D", "AMD Ryzen 9 7950X", "AMD Ryzen 5 7600X",

            # Placas base
            "ASUS Prime B550M-A", "MSI MAG B650 Tomahawk", "Gigabyte Z790 AORUS Elite", "ASRock B550 Phantom Gaming 4",
            "ASUS ROG STRIX Z690-F", "Gigabyte B760 Gaming X DDR4", "MSI PRO B550-VC", "ASRock X670E Steel Legend",

            # Memorias RAM
            "Corsair Vengeance 16GB DDR4", "G.Skill Trident Z RGB 32GB DDR5", "Kingston Fury Beast 16GB DDR5",
            "Patriot Viper Steel 64GB DDR4", "Crucial Ballistix 32GB DDR4",

            # Tarjetas gráficas
            "NVIDIA RTX 4060 Ti", "NVIDIA RTX 4070 Super", "NVIDIA RTX 4080", "AMD Radeon RX 7800 XT", "ASUS Dual RX 6700 XT",
            "Gigabyte RTX 3060 Gaming OC", "MSI RX 6600 Mech 2X", "Zotac RTX 4090 Trinity",

            # Almacenamiento
            "Samsung 980 Pro 1TB NVMe", "Crucial P5 Plus 2TB SSD", "Western Digital Blue 1TB HDD", "Seagate Barracuda 2TB HDD",
            "Kingston KC3000 1TB", "ADATA XPG SX8200 512GB SSD",

            # Periféricos
            "Logitech MX Master 3S", "Razer DeathAdder V2", "Corsair K70 RGB MK.2", "HyperX Alloy Origins",
            "Logitech G Pro X Headset", "SteelSeries Arctis Nova 7", "Elgato Stream Deck Mini",

            # Monitores
            "BenQ 27'' QHD PD2700Q", "ASUS TUF Gaming VG27AQ", "Samsung Odyssey G5 32''", "LG Ultragear 24GN600",
            "AOC 24B2XH 24'' IPS",

            # Otros componentes
            "Cooler Master 750W PSU", "NZXT H510 Flow", "Noctua NH-U12A Cooler", "Be Quiet! Pure Rock 2",
            "DeepCool AK400", "Thermaltake Versa H26"
        ]

        for nombre in random.sample(nombres_productos, 50):
            categoria = random.choice(categorias)
            proveedor = random.choice(proveedores)

            descripcion = fake.paragraph(nb_sentences=3)
            precio = round(random.uniform(50, 1200), 2)
            stock = random.randint(0, 100)
            stock_minimo = random.randint(5, 20)
            slug = slugify(nombre)

            producto = Producto.objects.create(
                nombre=nombre,
                slug=slug,
                categoria=categoria,
                proveedor=proveedor,
                descripcion=descripcion,
                precio=precio,
                stock=stock,
                stock_minimo=stock_minimo,
                disponible=True,
                imagen=f'productos_demo/{random.randint(1,12)}.jpg'
            )

            productos_generados += 1

        self.stdout.write(self.style.SUCCESS(f'{productos_generados} productos generados correctamente.'))
        self.stdout.write(self.style.SUCCESS(f'Datos de prueba creados con éxito.'))
