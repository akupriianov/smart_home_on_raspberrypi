# v1/access_control/views.py

from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import RFIDCard, AccessLog
from django.http import JsonResponse
from acces_control.rfid_reader import LATEST_CARD_UID  # Import stałej/zmiennej związanej z ostatnim odczytem karty
from acces_control.models import LatestScan
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

class CardListView(LoginRequiredMixin, ListView):
    """
    Widok oparty o klasę ListView, umożliwiający wyświetlenie listy kart RFID.
    - model: Model, z którego pobierane są obiekty do wyświetlenia
    - template_name: Ścieżka do szablonu renderującego listę kart
    - context_object_name: Nazwa, pod którą lista obiektów będzie dostępna w szablonie
    - paginate_by: Liczba obiektów na stronę (paginacja)
    """
    model = RFIDCard                       # Model, z którego pobierane są obiekty do wyświetlenia
    template_name = 'acces_control/card_list.html'  # Ścieżka do szablonu renderującego listę kart
    context_object_name = 'cards'      # Nazwa, pod którą lista obiektów będzie dostępna w szablonie
    ordering = ['id']          
    paginate_by = 20                       # Liczba obiektów na stronę (paginacja)

class CardCreateView(LoginRequiredMixin, CreateView):
    """
    Widok oparty o klasę CreateView, służący do dodawania nowych kart RFID.
    """
    model = RFIDCard                                  # Model, do którego zapisywane są dane
    template_name = 'acces_control/card_form.html'    # Szablon formularza do tworzenia nowej karty
    fields = ['uid', 'owner']                         # Pola modelu, które mają być widoczne w formularzu
    success_url = reverse_lazy('card-list')           # URL przekierowania po pomyślnym utworzeniu karty

class CardDeleteView(LoginRequiredMixin, DeleteView):
    """
    Widok oparty o klasę DeleteView, pozwalający na usunięcie wybranej karty.
    """
    model = RFIDCard                                          # Model karty, która ma zostać usunięta
    template_name = 'acces_control/card_confirm_delete.html'  # Szablon z potwierdzeniem usunięcia
    success_url = reverse_lazy('card-list')                   # URL przekierowania po pomyślnym usunięciu karty

@login_required
def get_latest_card(request):
    """
    Funkcja zwracająca w formacie JSON identyfikator (UID) ostatnio zeskanowanej karty.
    Jeżeli nie istnieje rekord w bazie (LatestScan), zwracany jest pusty ciąg znaków.
    """
    try:
        # Próba pobrania obiektu LatestScan z kluczem głównym 1
        scan = LatestScan.objects.get(pk=1)
        current_uid = scan.uid or ""
    except LatestScan.DoesNotExist:
        # Jeśli nie ma takiego obiektu, zwróć pusty UID
        current_uid = ""
    return JsonResponse({"last_card_uid": current_uid})

class AccesLogListView(LoginRequiredMixin, ListView):
    """
    Widok oparty na klasie ListView – wyświetla listę logów dostępu (AccessLog) w szablonie HTML.
    """
    model = AccessLog                                  # Model, z którego pobierane są logi
    template_name = 'acces_control/log_list.html'      # Szablon renderujący listę logów
    context_object_name = 'logs'                       # Nazwa listy logów w kontekście szablonu
    ordering = ['-timestamp']                          # Sortowanie – najnowsze logi pojawiają się jako pierwsze
    paginate_by = 20                                   # Liczba logów wyświetlanych na jednej stronie

@login_required
def logs_json(request):
    """
    Funkcja/endpoint, który zwraca listę logów w formacie JSON z uwzględnieniem paginacji.
    """
    # Pobranie numeru strony z parametrów GET, domyślnie jest to strona 1
    page_number = request.GET.get('page', 1)
    
    # Pobranie wszystkich logów z bazy i ich posortowanie (najnowsze pierwsze)
    logs_qs = AccessLog.objects.order_by('-timestamp')
    
    # Utworzenie obiektu Paginator z listą logów, 20 logów na stronę
    paginator = Paginator(logs_qs, 20)
    
    try:
        # Próba pobrania obiektów odpowiedniej strony
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # Jeśli page_number nie jest liczbą całkowitą, pobieramy pierwszą stronę
        page_obj = paginator.page(1)
    except EmptyPage:
        # Jeśli page_number jest większy niż liczba dostępnych stron, pobieramy ostatnią stronę
        page_obj = paginator.page(paginator.num_pages)
    
    # Przygotowanie listy słowników z danymi logów do zwrócenia w JSON
    data_logs = []
    for log in page_obj.object_list:
        # Konwersja strefy czasowej na lokalną (o ile mamy różne ustawienia strefy w systemie)
        local_dt = timezone.localtime(log.timestamp)
        formatted_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
        data_logs.append({
            'timestamp': formatted_time,
            'message': log.message,
            'card_uid': log.card.uid if log.card else None,  # UID karty, jeśli jest powiązana z logiem
        })
    
    # Dodatkowe informacje o paginacji (aktualna strona, liczba stron itd.)
    response_data = {
        'logs': data_logs,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
    }
    
    # Zwrócenie danych w formacie JSON
    return JsonResponse(response_data)
