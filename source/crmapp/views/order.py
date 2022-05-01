from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, CreateView

from crmapp.forms import OrderForm, ServiceOrderFormSet, StaffOrderFormSet
from crmapp.models import Order


class OrderListView(ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_service'] = self.object.order_services.all()
        context['staff'] = self.object.order_cliners.all()
        return context


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/order_create.html'
    success_url = 'crmapp:order_index'

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['cliners'] = StaffOrderFormSet(self.request.POST)
            context['services'] = ServiceOrderFormSet(self.request.POST)
        else:
            context['cliners'] = StaffOrderFormSet()
            context['services'] = ServiceOrderFormSet()
        return context

    def form_valid(self, form):
        print('я тут')
        context = self.get_context_data()
        services = context['services']
        cliners = context['cliners']
        with transaction.atomic():
            self.object = form.save()
            if services.is_valid() and cliners.is_valid():
                cliners.instance = self.object
                services.instance = self.object
                cliners.save()
                services.save()
        return super(OrderCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('crmapp:order_index')