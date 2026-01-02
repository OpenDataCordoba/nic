import string
from core.views import AnalyticsViewMixin
from web.listas.utils import generate_lista_table
from django.views.generic.base import TemplateView


class ProvinciasArgentinasListView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Provincias Argentinas'
        context['site_description'] = 'Lista de provincias argentinas'
        # Lista de provincias argentinas
        data = [
            'buenosaires',
            'catamarca',
            'chaco',
            'chubut',
            'cordoba',
            'corrientes',
            'entrerios',
            'formosa',
            'jujuy',
            'lapampa',
            'larioja',
            'mendoza',
            'misiones',
            'neuquen',
            'rionegro',
            'salta',
            'sanjuan',
            'sanluis',
            'santacruz',
            'santafe',
            'santiagodelestero',
            'tierradelfuego',
            'tucuman',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar', 'gob.ar'])
        context['data'] = dom_data

        return context


class DominiosUnaCaracterView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Dominios de una letra'
        context['site_description'] = 'Lista de dominios de una sola letra'
        # Lista de dominios de una letra
        data = list(string.ascii_lowercase) + list(string.digits)
        dom_data = generate_lista_table(data, zonas_relevantes=['ar', 'com.ar'])
        context['data'] = dom_data

        return context


class DominiosDosCaracteresView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Dominios de dos letras en .ar'
        context['site_description'] = 'Lista de dominios de dos letras en .ar'
        # Lista de dominios de dos letras
        data = []
        for char1 in string.ascii_lowercase + string.digits:
            for char2 in string.ascii_lowercase + string.digits:
                data.append(f"{char1}{char2}")
        dom_data = generate_lista_table(data, zonas_relevantes=['ar'])
        context['data'] = dom_data

        return context


class CiudadesArgentinasView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Ciudades Argentinas'
        context['site_description'] = 'Lista de ciudades argentinas'
        # Lista de ciudades argentinas
        data = [
            'buenosaires',
            'cordoba',
            'rosario',
            'carlospaz',
            'mendoza',
            'laplata',
            'sanmiguel',
            'mardelplata',
            'salta',
            'santafe',
            'sanjuan',
            'resistencia',
            'bahiablanca',
            'parana',
            'merlo',
            'quilmes',
            'sansalvador',
            'guaymallen',
            'posadas',
            'sanrafael',
            'laferrere',
            'lanus',
            'godoycruz',
            'banfield',
            'riocuarto',
        ]
        data = sorted(data)
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar', 'gob.ar'])
        context['data'] = dom_data

        return context


class PorteniosView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Dominios Porteños'
        context['site_description'] = 'Lista de dominios porteños'
        # Lista de dominios porteños
        data = [
            'tango',
            'laboca',
            'palermo',
            'recoleta',
            'belgrano',
            'caballito',
            'flores',
            'monserrat',
            'sanisidro',
            'villaurquiza',
            'nuñez',
            'constitucion',
            'almagro',
            'boedo',
            'parquechacabuco',
            'villaurquiza',
            'parquepatricios',
            'villaurquiza',
            'bsas',
            'baires',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar', 'gob.ar'])
        context['data'] = dom_data

        return context


class ComidasView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Comidas Populares'
        context['site_description'] = 'Lista de comidas populares'
        # Lista de comidas populares
        data = [
            'pizza',
            'empanadas',
            'asado',
            'milanesa',
            'chori',
            'choripan',
            'pan',
            'locro',
            'humita',
            'provoleta',
            'leche',
            'queso',
            'dulcedeleche',
            'alfajor',
            'mate',
            'medialunas',
            'chocotorta',
            'pollo',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class BebidasView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Bebidas Populares'
        context['site_description'] = 'Lista de bebidas populares'
        # Lista de bebidas populares
        data = [
            'agua',
            'fernet',
            'cerveza',
            'vino',
            'jugo',
            'cafe',
            'te',
            'matecocido',
            'licuado',
            'champagne',
            'whisky',
            'vodka',
            'ron',
            'sidra',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class FutbolistasView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Dominios de futbol argentino'
        context['site_description'] = 'Lista de dominios de futbol argentino'
        data = [
            'talleres',
            'afa',
            'velez',
            'racing',
            'river',
            'boca',
            'independiente',
            'sanlorenzo',
            'newells',
            'rosario',
            'central',
            'colon',
            'union',
            'estudiantes',
            'gimnasia',
            'instituto',
            'lanus',
            'platense',
            'aldosivi',
            'argentinos',
            'banfield',
            'huracan',
            'tigre',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar', 'org.ar'])
        context['data'] = dom_data

        return context


class CiudadesMundoView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ciudades Importantes del Mundo'
        context['site_description'] = 'Lista de ciudades importantes del mundo como dominios argentinos'
        # Lista de ciudades importantes del mundo
        data = [
            'amsterdam',
            'barcelona',
            'berlin',
            'dubai',
            'london',
            'losangeles',
            'madrid',
            'miami',
            'moscu',
            'newyork',
            'paris',
            'roma',
            'sydney',
            'tokyo',
            'viena',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar', 'tur.ar'])
        context['data'] = dom_data

        return context


class FinanzasView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Finanzas'
        context['site_description'] = 'Lista de dominios relacionados con finanzas e inversiones'
        data = [
            'ahorro',
            'banco',
            'billetera',
            'bitcoin',
            'bolsa',
            'broker',
            'cripto',
            'credito',
            'dinero',
            'dolar',
            'finanzas',
            'litio',
            'hipoteca',
            'inversion',
            'oro',
            'plata',
            'prestamo',
            'seguro',
            'tarjeta',
            'trading',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class TecnologiaView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Tecnología'
        context['site_description'] = 'Lista de dominios relacionados con tecnología'
        data = [
            'android',
            'app',
            'ai',
            'apps',
            'cloud',
            'codigo',
            'cyber',
            'data',
            'digital',
            'hosting',
            'ia',
            'internet',
            'iphone',
            'online',
            'software',
            'tech',
            'web',
            'wifi',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class DeportesView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Deportes'
        context['site_description'] = 'Lista de dominios relacionados con deportes'
        data = [
            'basket',
            'boxeo',
            'ciclismo',
            'fitness',
            'futbol',
            'golf',
            'gym',
            'hockey',
            'natacion',
            'padel',
            'polo',
            'rugby',
            'running',
            'ski',
            'surf',
            'tenis',
            'voley',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class VerbosAccionView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Verbos de Acción'
        context['site_description'] = 'Lista de dominios con verbos de acción'
        data = [
            'alquilar',
            'buscar',
            'comprar',
            'conocer',
            'contratar',
            'cotizar',
            'encontrar',
            'enviar',
            'pagar',
            'pedir',
            'reservar',
            'vender',
            'viajar',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class ProfesionesView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Profesiones'
        context['site_description'] = 'Lista de dominios relacionados con profesiones'
        data = [
            'abogado',
            'abogados',
            'arquitecto',
            'arquitectos',
            'contador',
            'contadores',
            'dentista',
            'dentistas',
            'disenador',
            'doctor',
            'ingeniero',
            'ingenieros',
            'medico',
            'medicos',
            'escribano',
            'nutricionista',
            'psicologo',
            'programador',
            'veterinario',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class MusicaArtesView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Música y Artes'
        context['site_description'] = 'Lista de dominios relacionados con música y artes'
        data = [
            'arte',
            'banda',
            'cine',
            'cumbia',
            'cultura',
            'disco',
            'folklore',
            'guitarra',
            'musica',
            'piano',
            'radio',
            'reggaeton',
            'rock',
            'teatro',
            'tv',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class VehiculosView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Vehículos'
        context['site_description'] = 'Lista de dominios relacionados con vehículos'
        data = [
            'auto',
            'autos',
            'bici',
            'bicicleta',
            'camion',
            'camioneta',
            'moto',
            'motos',
            'nautica',
            'repuestos',
            'taller',
            'tractor',
            'usados',
            'vehiculos',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class PropiedadesView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Propiedades'
        context['site_description'] = 'Lista de dominios relacionados con propiedades e inmuebles'
        data = [
            'alquiler',
            'alquileres',
            'barrio',
            'casa',
            'casas',
            'departamento',
            'edificio',
            'inmobiliaria',
            'inmueble',
            'inmuebles',
            'lote',
            'oficina',
            'propiedad',
            'terreno',
            'venta',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context


class EducacionView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios de Educación'
        context['site_description'] = 'Lista de dominios relacionados con educación'
        data = [
            'academia',
            'aprende',
            'capacitacion',
            'clases',
            'colegio',
            'colegios',
            'curso',
            'cursos',
            'doctorado',
            'doctorados',
            'educacion',
            'escuela',
            'escuelas',
            'estudio',
            'idiomas',
            'ingles',
            'instituto',
            'master',
            'maestria',
            'maestrias',
            'profesor',
            'universidad',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar'])
        context['data'] = dom_data

        return context
